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

## 9. 5 张图 base64 内嵌触顶飞书消息体（实测 2026-07-06）

- **症状**：4 张 1792x1024 图 base64 内嵌约 1.5MB 没问题；**5 张（封面+4 Step）涨到 7.96MB**。send_message 走 IM 通道，**单条消息体上限 4MB**，HTML 发不出去，用户收不到。
- **根因**：双 HTML 模式（`references/two-html-pattern.md`）的"微信粘贴版（b64 内嵌）"假设是 4 张图，没考虑 5+ 张图场景。
- **修法**：
  1. **5+ 张图版本**必须走 `python3 ~/.agents/skills/feishu-send-attachment/scripts/send_file.py --file <html> --chat-id <id>`，**msg_type=file** 通道（上限 10MB）能发。
  2. 或降级：5 张图 → JPG 压缩后 base64 内嵌（cover 200KB + 4 张 400KB ≈ 1.8MB，OK）。
  3. 或拆：4 张图 base64 + 第 5 张用相对路径（但本机双击 HTML 看不到第 5 张）。
- **自检**：写完 HTML 跑 `wc -c <file>.html` 看大小，> 4MB → 走 send_file 通道。

## 10. `for` 循环多图生成被 SIGTERM -15 一次性 kill

- **症状**：3 张图塞进一个 `for i in 01 02 03; do python3 generate_image.py ...; done`，外层 shell 进程被 SIGTERM 后，**3 张全部丢失**，没有进度残留。
- **根因**：单 shell 进程串行跑多张图，任何一张超时或父进程被 OOM kill，所有 in-flight 的图片 API 调用都断。
- **修法**：
  1. **每张图独立 background 跑**（`background=true, notify_on_complete=true`），3 张图 3 个独立 session_id，每张完成/失败单独通知。
  2. 或 `nohup python3 ... &` 写日志文件 `output/<date>/imgs/01.log`，中断后从日志恢复已完成的图。
  3. 永远不要把 3+ 张图塞进一个 for 循环 + 一次性 `wait`。
- **教训**：2026-07-06 一次 for 循环跑 3 张 Step 图，外层被 SIGTERM -15 杀，3 张图全部 0 字节。

## 11. `execute_code` 沙盒无状态（NameError 反复）

- **症状**：第一次 `execute_code` 里 import 了 `from hermes_tools import web_search` 调成功；第二次 `execute_code` 又调 `web_search(...)`，报 `NameError: name 'web_search' is not defined`。
- **根因**：`execute_code` 每次都跑在**新 Python 进程**，所有 import 和变量不保留。Pitfall #2 已记录"读不到 env"，但更广的"状态不保留"问题没记。
- **修法**：
  1. **多步逻辑合并到一次 execute_code**：一次脚本里跑完 5 步转换，不要拆 5 次。
  2. 跨 turn 持久化用 `write_file` 落盘。
  3. 跨 turn 状态读取用 `read_file`。
  4. `import` 永远放脚本最顶端（不是中段），避免后续步骤假设已 import。