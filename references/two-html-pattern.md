# 双 HTML 模式｜公众号文章 HTML 交付模板

> Step 10 的可复用模板。每次按 `ai-gzh-platform` 生产正式交付时，按本文档产两份 HTML，避免单文件既"用户能粘贴"又"能推草稿"的二选一困境。

## 为什么需要两个版本

| 版本 | 用途 | 图片策略 | 大小 | 触发 45002 风险 |
|---|---|---|---|---|
| **微信粘贴版** | 用户 Chrome 打开 → Cmd+A → Cmd+C → 公众号后台 Cmd+V | base64 内嵌 4 张图（封面+3正文） | 通常 800KB-1.5MB | 风险高，但用户不推草稿所以无所谓 |
| **推草稿版** | 配合 `push_draft.py` 自动推草稿 | 相对路径 `imgs/*.jpg`（**不含封面**），封面单独走 thumb_media_id | 通常 20-30KB | 几乎为零 |

只产一个版本的代价：

- 只产粘贴版（7MB）：用户本地能看，`push_draft.py` 必报 45002
- 只产推草稿版（22KB）：推草稿能过，但用户单独收到 HTML 在飞书/浏览器打开看不到图（相对路径找不到 imgs/）

**结论：永远产两个版本。** 产物是 `output/<date>-<slug>/html/<slug>-微信粘贴版-v1.html` 和 `<slug>-推草稿版-v1.html`。

## 实测大小参考

来自 2026-07-03 AI消费补贴文章：

- 4 张 GPT Image 2 PNG 总大小：5.7MB（1792×768 封面 1.4MB + 3 张 1792×1024 正文各 1.3MB）
- PNG → JPG 压缩后：约 700KB（脚本 `compress_images.py`，quality=80）
- 微信粘贴版（b64 内嵌）：927KB
- 推草稿版（相对路径）：22KB

## 实现骨架

### 1. 生成 4 张图后立即压缩

```bash
cd ~/.hermes/skills/ai-gzh-platform
python3 scripts/compress_images.py output/<date>-<slug>/imgs/
# 输出：cover.jpg + 01-xxx.jpg + 02-xxx.jpg + 03-xxx.jpg
```

### 2. 微信粘贴版（base64 内嵌）

```python
import base64
b64 = {}
for f in ["cover.jpg", "01-xxx.jpg", "02-xxx.jpg", "03-xxx.jpg"]:
    with open(f"output/<date>-<slug>/imgs/{f}", "rb") as fp:
        b64[f] = base64.b64encode(fp.read()).decode()

# HTML 里所有 <img> 用 data:image/jpeg;base64,<b64[f]>
```

**优点**：单文件可独立打开，飞书发送、浏览器预览、邮件附件都能用。

### 3. 推草稿版（相对路径）

```python
# HTML 里所有 <img src="imgs/01-xxx.jpg"> （相对路径）
# 关键：删掉封面那一行，封面走 thumb_media_id
```

**与 `push_draft.py` 配合**：`push_draft.py` 调用时把封面图作为 `thumb_media_id` 上传，HTML body 里不重复出现封面图（否则 45002）。

## HTML 模板要点（tech-blue 风格）

- background: `#FFFFFF`
- primary: `#2563EB`（主色）
- accent: `#F97316`（强调色）
- text: `#1F2937`
- sub: `#6B7280`
- border: `#E5E7EB`

**必须全内联**——微信公众号粘贴时会过滤掉 `<style>` 标签和外部 CSS。

## 表格渲染坑

markdown 表格里的 `|---|---|---|` 分隔行会被当作数据行渲染出空白格。

**修法**：渲染前过滤：

```python
cleaned = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
```

## 与其它 step 的衔接

- **Step 11 飞书资料包**：必须在 Step 10 之前创建（因为 HTML 的 CTA 区需要嵌入飞书 doc 的 URL）
- **Step 12 推草稿**：必须用推草稿版，不是粘贴版

## 检查清单

交付前自检：

- [ ] `output/<date>-<slug>/html/<slug>-微信粘贴版-v1.html` 存在
- [ ] `output/<date>-<slug>/html/<slug>-推草稿版-v1.html` 存在
- [ ] 微信粘贴版 ≤ 2MB（base64 内嵌后）
- [ ] 推草稿版 ≤ 50KB（相对路径 + JPG）
- [ ] 两个版本标题/正文/H2 数量一致（除了封面图）
- [ ] 表格分隔行已被过滤
- [ ] 关键短语（品牌名、CTA 关键词）命中