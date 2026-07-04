# 推草稿到公众号 — 踩坑记录（2026-07-02 实测）

每条踩坑都附**复现条件 + 修法 + 验证方法**。下次跑 Step 12 前必读。

---

## 坑 1：中文内容在草稿箱显示为 `\uXXXX` 字面量（最严重）

**复现条件**：`push_draft.py` 用 `http_client.post(url, json=data, ...)` 推 content。

**症状**（来自实际草稿截图）：
- 草稿箱预览：标题/作者/日期正常 → 正文部分全是 `\u6211\u505a\u4e86` 之类的字面量
- ASCII 字符（数字、AI、英文）正常显示
- 元数据区（作者名/公众号名/日期）正常显示

**根因**：`requests` 库的 `json=` 参数内部走 `json.dumps(..., ensure_ascii=True)`，把所有非 ASCII 字符转义为 `\uXXXX`。**微信后端没做二次解码**（或 wx-proxy.js 没解码），直接存入数据库，渲染时显示字面量。

**修法**（已应用到 `scripts/push_draft.py` L18-33）：

```python
def api_call(path, data=None, method="GET"):
    import json as _json
    ...
    if method == "POST":
        # CRITICAL: ensure_ascii=False
        body = _json.dumps(data, ensure_ascii=False).encode("utf-8")
        resp = http_client.post(url, headers=headers, data=body, timeout=30)
```

**验证方法**（每次推完必跑）：

```bash
# 1) 拉草稿内容
curl -X POST "http://127.0.0.1:8787/cgi-bin/draft/get?access_token=$AT" \
  -H "X-Publish-Token: $WX_PROXY_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"media_id\":\"$NEW_MEDIA_ID\"}"

# 2) 关键指标
# - content 中文字符数 > 1000
# - content 中 "\u" 出现次数 = 0
# - content 中 "&#39;" 或 "&quot;" 正常（HTML 实体）
```

如果中文字符数 < 100 或 `\u` 出现 > 0，**立刻删草稿重发**。

---

## 坑 2：title 限制是 30 **字节**（不是 30 字符）

**复现条件**：用 Python `len(title)` 校验标题长度。

**症状**：`errcode: 45003, errmsg: title size out of limit`

**根因**：微信公众号 title 限制 30 字节，UTF-8 中文 = 3 字节/字符。

**校验代码**：

```python
def title_ok(t):
    return len(t.encode('utf-8')) <= 30
# "8 个月 AI 写公众号复盘" = 14 字符 = 30 字节 ✅
# "8 个月 AI 写公众号，我才明白为什么要杀 AI 写手" = 28 字符 = 84 字节 ❌
```

---

## 坑 3：digest 限制是 54 **字节**

**复现条件**：同上。

**症状**：`errcode: 45004, errmsg: description size out of limit`

**修法**：

```python
def digest_ok(d):
    return len(d.encode('utf-8')) <= 54
```

---

## 坑 4：content 超 2MB / HTML 字符超限

**复现条件**：单图 PNG > 1MB 直接 base64 嵌入 HTML。

**症状**：`errcode: 45002, errmsg: content size out of limit`

**根因**：单篇公众号文章 content 限制 ~2MB。3 张 1MB PNG base64 = 4MB，3 倍超。

**修法**（三选一）：

1. **PIL 转 jpg q80**（推荐）：3MB PNG → 300KB jpg，3 张图总计 1MB 以内
2. **cover 不进 HTML**：封面用 thumb_media_id，HTML 里不放
3. **分块上传**：先调 `/cgi-bin/media/uploadimg` 拿 URL，再把 URL 嵌入 HTML

**代码示例**：

```python
from PIL import Image
img = Image.open(src)
if img.mode in ('RGBA', 'LA', 'P'):
    bg = Image.new('RGB', img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[-1])
    img = bg
img.save(dst, 'JPEG', quality=80, optimize=True)
```

---

## 坑 5：飞书文档创建后**内容为空**（POST /documents 不写 content）

**复现条件**：`POST /docx/v1/documents` 只传 `title` + `content` 字段。

**症状**：文档创建成功（返回 document_id），打开后**只有标题，正文为空**。

**根因**：飞书新版文档 OpenAPI 是 **Block 树**结构。`POST /documents` **只创建空文档 + 返回 document_id**。要写入内容需要**第二个 API**：

```
POST /open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children
```

其中 `{block_id}` 默认就是 `{document_id}`（Page Block 是根节点）。

**修法**：分两步

```python
# Step 1: 创建空文档
POST /open-apis/docx/v1/documents
Body: {"title": "..."}
Returns: {"data": {"document": {"document_id": "..."}}}

# Step 2: 写入 blocks
POST /open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children
Body: {
  "index": 0,
  "children": [
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "..."}}], "style": {}}},
    {"block_type": 3, "heading1": {"elements": [{"text_run": {"content": "..."}}], "style": {}}},
    ...
  ]
}
```

**block_type 速查**：
- `2` = text
- `3` = heading1
- `4` = heading2
- `12` = bullet
- `22` = divider

**限制**：单次 `children` 数组**最多 50 个**（实测 51+ 报 `the max len is 50`）。超过要分批。

**⚠️ 写入前必做**：先用 1 个 block 测试格式，确认返回 code=0 后再批量写入。不同 block_type 的 elements 结构不同，直接批量写容易触发 1770001 invalid param。详见 `references/feishu-block-pitfall.md`。

**验证方法**：

```bash
GET /open-apis/docx/v1/documents/{document_id}/raw_content
# content length > 500 (有内容) / = 32 (只有标题，空文档)
```

---

## 坑 6：create blocks 一次超过 50 个 block

**复现条件**：单次 `POST /blocks/.../children` 传超过 50 个 children。

**症状**：`{"code":99992402,"msg":"field validation failed","field_violations":[{"field":"children","description":"the max len is 50"}]}`

**修法**：分批写，每批 ≤ 30（留 buffer）。后续 batch 的 `index = 之前所有 batch 的总数`：

```python
# Batch 1: index=0
batches[0] → index=0
# Batch 2: index = len(batches[0])
batches[1] → index=len(batches[0])
# Batch 3: index = len(batches[0]) + len(batches[1])
...
```

---

## 坑 7：上传图片时传 .png 但 HTML 引用 .jpg（或反之）

**复现条件**：压缩图后传给 `push_draft.py --images *.jpg`，但 HTML 仍用 PNG base64。

**症状**：`残留 base64: 3`（脚本 L96 报告），3 张图都没替换成微信 URL，文章里图片显示"加载失败"。

**修法**：**保持一致**——压缩图后用 `*.jpg` 重新生成 HTML，让 `push_draft.py` 也传 `*.jpg`。

---

## 坑 8：wx-proxy 401 / 403

**症状**：`{"error": "unauthorized"}` 或 `{"error": "path not allowed: ..."}`

**修法**：
- 401：检查 `X-Publish-Token` 头是否等于 `/opt/wx-proxy/.env` 里 `WECHAT_PROXY_TOKEN` 值
- 403：检查路径白名单（`/cgi-bin/{token, material, draft, freepublish, media}`）

---

## 一次性脚本：删除草稿

```python
# 用于"修了 push_draft.py 但旧草稿是坏的，需要删掉重发"场景
import os, json, urllib.request
env = {}
with open('/home/ubuntu/.hermes/.env') as f:
    for ln in f:
        s = ln.strip()
        if s and not s.startswith('#') and '=' in s:
            env[s.split('=', 1)[0].strip()] = s.split('=', 1)[1].strip()
PT = env['WX_PROXY_TOKEN']
A = env['WX_APPID']
sc = env['WX_APPSECRET']
# Get token
url = "http://127.0.0.1:8787/cgi-bin/token?grant_type=client_credential&appid=" + A + "&secret=" + sc
req = urllib.request.Request(url, headers={"X-Publish-Token": PT})
at = json.loads(urllib.request.urlopen(req).read())['access_token']
# Delete
OLD = "<要删的 media_id>"
url = "http://127.0.0.1:8787/cgi-bin/draft/delete?access_token=" + at
body = json.dumps({"media_id": OLD}, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(url, data=body, headers={"X-Publish-Token": PT, "Content-Type": "application/json; charset=utf-8"}, method='POST')
print(json.loads(urllib.request.urlopen(req).read()))
```

---

## 完整重发 checklist（推完一篇必跑）

1. ✅ 跑 `push_draft.py` 拿到新 `media_id`
2. ✅ 拉 `draft/get` 验证中文字符数 > 1000
3. ✅ 拉 `draft/get` 验证 `\u` 出现次数 = 0
4. ✅ 拉 `draft/get` 验证 残留 base64 = 0（`data:image/` 不出现在 content 中）
5. ✅ 拉 `draft/get` 验证 `img src="http://mmbiz.qpic.cn/..."` 至少 3 个（图片 URL 替换成功）
6. ✅ 飞书文档 `content length > 500`（不是 32）
7. ✅ 通知用户：发飞书消息 + 4 张图 + .md + .html

任一不通过 → 立刻删草稿 + 修脚本 + 重发。

---

## 坑 9：WX_PROXY_SERVER 环境变量未设置导致 URL 构建失败（2026-07-04 实测）

**复现条件**：`~/.hermes/.env` 中没有 `WX_PROXY_SERVER` 配置，或 `source .env` 后未 `export`。

**症状**：
```
token失败: {'error': "Invalid URL 'http://:8787/cgi-bin/token?...': No host supplied"}
```
URL 变成 `http://:8787/...`，host 为空。

**根因**：`push_draft.py` 用 `f"http://{os.getenv('WX_PROXY_SERVER', '')}:{os.getenv('WX_PROXY_PORT', '8787')}"` 构建 URL。当 `WX_PROXY_SERVER` 为空时，host 部分为空。

**修法**（三步）：

1. 在 `~/.hermes/.env` 中添加：
```bash
WX_PROXY_SERVER=10.0.0.4  # 替换为你的本机IP
```

2. 更新 `config.json`：
```json
{
  "wechat_proxy": {
    "enabled": true,
    "server_ip": "10.0.0.4"
  }
}
```

3. 运行时确保 export：
```bash
source ~/.hermes/.env && export WX_PROXY_SERVER WX_PROXY_PORT WX_PROXY_TOKEN WX_APPID WX_APPSECRET
```

**验证方法**：
```bash
# 测试wx-proxy连通性
curl -s "http://$WX_PROXY_SERVER:8787/health"
# 应返回 {"status": "ok", "proxy": "wx-api-proxy"}
```

**⚠️ 关键**：`source .env` 只是读取变量到当前 shell，Python 子进程拿不到。必须 `export` 才能传给子进程。
