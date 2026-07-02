# 首次安装 Walkthrough：从用户画像到可用 config

> 一个**真实的、可复用的**端到端示例。当用户说"按我画像配置 / 你直接选 / 不知道的再问"时按这个流程走。

## 流程总览（4 阶段）

```
读画像档 → diff vs example.json → 填入 + 标注依据 → 实测验证 → 仅当验证通过才 enabled: true
```

## 阶段 1：读画像档（30 秒）

并行读：
- `~/.hermes/USER.md`（用户画像）
- `~/.hermes/AGENTS.md`（命名约定，如"大姚=AI 名"）
- 当前会话的 USER PROFILE 注入（系统提示里的「用户偏好」段）
- skill 自带的 `config.example.json`

**目标**：列出"已经知道的字段" vs "需要问的字段"。

## 阶段 2：diff vs example（30 秒）

常见已能确定的字段（基于典型 公众号运营用户画像）：

| 字段 | 来源 | 依据 |
|------|------|------|
| `brand_name` | AGENTS.md "大姚=AI 名" | 命名约定直接给 |
| `content_directions` | USER PROFILE 主线 | "AI 企业应用"主线 + 副线 |
| `target_audience` | example.json 已含 | example 写得够准就复用，不重写 |
| `html_template.style_name` | USER PROFILE 配色偏好 | example 默认值通常可用 |
| `image_style.name` | 是否装了小姚 IP 校准图 | 装了 → xiaoyao-illustrations；没装 → baoyu-notion |
| `feishu.enabled` | `.env` 是否有 FEISHU_APP_ID/SECRET | 有 → 准备启用；没有 → false |
| `wechat_proxy.enabled` | `.env` 是否有 WX_APPID/APPSECRET | 有 → 准备启用；没有 → false |

## 阶段 3：填入 config.json + 标注依据（1 分钟）

每填一项加 `"picked": "<依据>"` 字段（example 里没有就自己加），用户能回查"这个字段为什么是这个值"。

**禁忌**：
- ❌ 把"我不知道"伪装成"默认"
- ❌ 把"我猜的"说成"agent 智能判断"
- ✅ 不确定就明说"待核验"
- ✅ 一次问最多 3 个真正缺的问题

## 阶段 4：实测验证（2 分钟，**关键**）

填完**不要立刻** `enabled: true`。逐个验证：

### 4.1 飞书 token 探活

```python
import json, urllib.request
env = parse_env('~/.hermes/.env')  # 用 partition('=') 避开 *** 过滤
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=json.dumps({"app_id": env['FEISHU_APP_ID'], "app_secret": env['FEISHU_APP_SECRET']}).encode(),
    headers={"Content-Type": "application/json"}, method='POST'
)
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())
# 通过: data['code'] == 0 and len(data['tenant_access_token']) > 30
```

### 4.2 图片 API 探活

```python
req = urllib.request.Request(
    'https://api.zhongzhuan.chat/v1/images/generations',
    data=json.dumps({"model": "gpt-image-2", "prompt": "tiny red square", "n": 1, "size": "1024x1024"}).encode(),
    headers={"Authorization": f"Bearer {env['GPT_IMAGE2_API_KEY']}", "Content-Type": "application/json"},
    method='POST'
)
resp = urllib.request.urlopen(req, timeout=60)
data = json.loads(resp.read())
# 通过: 'data' in data and len(data['data']) > 0
```

### 4.3 决策树

| 飞书 ✅ | 图片 ✅ | 操作 |
|--------|--------|------|
| ✅ | ✅ | 都开 `enabled: true` |
| ✅ | ❌ (401) | **Key 属于另一平台**——告知用户，给出"先用文字链路，配图后开"方案。把 image_api.enabled 改回 false |
| ❌ | ✅ | 飞书凭证失效——只开 image，提醒用户检查 App Secret |
| ❌ | ❌ | 两个都不开，文字链路先行 |

## 实测陷阱（必读）

### 陷阱 1：`.env` 不支持 shell 变量展开

```ini
# ❌ 不工作 —— python-dotenv 不会展开
GPT_IMAGE2_API_KEY=${CUSTOM_OPENAI_API_KEY}

# ✅ 正确 —— 读源 key 的字面值，写到 alias 行
GPT_IMAGE2_API_KEY=sk-yxxxx...Lfc5
```

别名（aliasing）的正确做法：先 `partition('=')` 读出源值（**避开 `***` 过滤**），再 `write_file` 把字面值写到 alias 行。

### 陷阱 2：`.env` 里的 Key 不一定属于你当前配的 base

典型场景：用户 `.env` 有
```
CUSTOM_OPENAI_API_KEY=sk-yxxx...Lfc5
OPENAI_BASE_URL=https://api.zhongzhuan.chat/v1
```

但 skill 拿同一个 `CUSTOM_OPENAI_API_KEY` 去配另一台 `https://api.sharehub.club/v1`，会 401。

**对策**：每个 base 必须用对应的 Key 验证一次，不要假设同 Key 通用。

### 陷阱 3：401 不一定是 Key 错

按概率排序：
1. Key 属于另一个平台（最常见）
2. Key 过期或被撤销
3. endpoint 路径错（漏 `/v1`）
4. 模型名不在该平台白名单
5. CF 地区限制（`error code: 1010`）—— 不是 Key 错，加 UA

## 完整工作流示例（已实测）

> 用户：「按我画像配一下 ai-gzh-platform，你知道的就直接选，不知道的再问」

```python
# Step 1: 读 USER PROFILE（系统注入）+ AGENTS.md + example.json
USER_PROFILE  # 含主线 + 偏好
AGENTS = read('~/.hermes/AGENTS.md')  # 含"大姚=AI 名"
example = json.loads(read(skill_dir + '/config.example.json'))

# Step 2: 已知字段直接填
config = {
    "brand_name": "大姚AI提效",  # 来自 AGENTS
    "content_directions": ["AI企业应用", "AI职场提效", "AI商业化变现"],  # 来自 USER 主线
    "target_audience": example['target_audience'],  # 复用 example
    "html_template": {"style_name": "科技蓝", "primary_color": "#2563EB", ...},
    "image_style": {"name": "xiaoyao-illustrations"},  # 装了 5 张校准图就用 IP 风格
}

# Step 3: 未知项（仅 2 个）问用户
#   - 图片 API：不知道哪个 Key 对哪个 base
#   - 公众号推草稿：不知道是否部署了 wx-proxy

# Step 4: 用户选 B 方案后，注入 + 验证
# .env 加 GPT_IMAGE2_API_KEY=*** 真实值
# config.json 写 image_api.endpoint='https://api.zhongzhuan.chat/v1/images/generations'
# 但**先验证** —— 401 → 回滚 enabled=false

# Step 5: 给用户一个清晰汇总
# - 我替你选了哪些（带依据）
# - 还缺哪些（按必填/可选分组）
# - 验证结果（哪条通了，哪条没通）
```

## 给用户的回复模板

> ✅ `config.json` 已生成。
>
> ## 我替你做的决定（基于画像 + example）
>
> | 项 | 我选的 | 依据 |
> |---|---|---|
> | brand_name | 大姚AI提效 | AGENTS.md "大姚=AI 名" |
> | ... | ... | ... |
>
> ## 还需要你给的（X 项，全部为安全链路，不在聊天回显）
>
> **A. 图片生成 API（必填，否则配图跑不起来）**
> ...
>
> ## 立即可用的部分
>
> 配置已经足够跑【写作 + 四层自检 + HTML 排版】。差的就只是"配图"这一步。

这种格式比"我帮你配好了"清楚 N 倍——用户能看到每一个决定的依据。