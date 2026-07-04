# 常见 Live Failure（按实测整理）

> 每条都有复现条件 + 修法。agent 命中具体坑时按需加载本文件。

## 1. 标题字节超限（最常见、最致命）

- **症状**：写到 Step 7 标题，长度看似"差不多"，实测 47-76B，超 30B。
- **修法**：写完立刻 `python3 scripts/check_title_digest.py --title "标题"` 实测。每汉字 3B、每 ASCII 1B。
- **预防**：标题公式按"≤ 8 个汉字 + ≤ 4 个英文/数字 token"做初稿。

## 2. execute_code 读不到 env

- **症状**：`os.getenv('GPT_IMAGE2_API_KEY')` 返回 `None`，但 `env | grep` 能看到。
- **根因**：`execute_code` 沙箱进程不继承 shell 的 export。
- **修法**：调 `generate_image.py` 用 `terminal()` 而不是 `execute_code`。

## 3. 推草稿 HTML 不压缩

- **症状**：4 张 PNG 总 5.7MB，HTML 直接 base64 内嵌就 7MB+，必触发 45002。
- **修法**：先 `python scripts/compress_images.py imgs/` 转 JPG（13% 压缩比），然后推草稿版 HTML 引用 `.jpg`，**且不含封面**（封面走 thumb_media_id）。

## 4. 飞书 doc 一次写超过 50 个 block

- **症状**：Feishu API 返回 `code != 0`，文档半截写入。
- **修法**：按 30 个 block / 批分页写，最后 `GET /raw_content` 验 content 长度 > 500。

## 5. L1 自检里的「这意味着」「换句话说」漏检

- **症状**：首轮自检通过，但实际还有 1-2 处命中。
- **修法**：自检脚本要 `content.count(w) > 0` 而不是只看 `w in content` 第一个命中；分多次 replace_all。

## 6. GPT Image 2 偶有英文字母混入（如"AA景区"）

- **症状**：纯中文 prompt 生成出"A级景区"变成"AA景区"。
- **判断**：行业常见写法 + 不影响理解 = 不重生成，记到验收表"微小瑕疵"即可。
- **避免过度 QA 卡死**：极轻微标点/装饰瑕疵记录即可，反复重生成会拖慢交付。

## 7. 微信粘贴版 vs 推草稿版只产一个

- **症状**：只做了 7MB 单 HTML，用户本地能看但 `push_draft.py` 一推必 45002。
- **修法**：**永远产两个版本**（双 HTML 模式，见 `references/two-html-pattern.md`）。

## 8. 表头/分隔行被当数据行渲染

- **症状**：markdown 表格里的 `|---|---|---|` 分隔行渲染出空白格。
- **修法**：渲染前过滤 `all(set(c)<=set("-: ") for c in row)` 的行。