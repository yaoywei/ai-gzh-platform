# 把 ai-gzh-platform 的 Prompt 注入到既有 n8n 工作流 — 踩坑记录

适用于：**用户的 n8n 上已经有"公众号生产+飞书归档"类型的工作流**，用户指定"用我的 n8n 工作流"而不是直接走 ai-gzh-platform。

不是新做一个 n8n 工作流——是**改造既有节点的 system prompt 字段**，让它从其他风格（如小红书爆文）切到 ai-gzh-platform 的 khazix-writer + enterprise-windvane 风格。

---

## 0. 决策框架 — 什么时候改造 n8n 节点

用户说"用我的 n8n 工作流"或"用工作流"时：

1. **先查工作流**：`GET /api/v1/workflows/{id}` 拿节点清单 + jsCode + 节点参数
2. **看 system prompt 在哪**：通常在 Code 节点（KB Builder / Prompt Builder）的字符串变量里，或在 HTTP Request 节点的 jsonBody 里
3. **不要"重写整个工作流"**：用户要的是**注入新 prompt**，不是替换工作流
4. **改前必备份**：把现有 jsCode 写到本地再改

---

## 坑 1：n8n HTTP Request 节点的 credential 鉴权失败

**复现条件**：工作流的 HTTP Request 节点配了 `httpBearerAuth` 类型的 credential，但目标 endpoint 需要 `X-Api-Key` header（如 minimaxi.com 的 anthropic 兼容端点）。

**症状**：`NodeApiError: Authorization failed - please check your credentials` 或 `HTTP 401`

**根因**：credential 的 key 类型与 endpoint 期望的 header 不匹配。`LIGHTCLAW_API_KEY` 这类 key 在 minimaxi 端点会失败，必须用 `MINIMAX_CODING_API_KEY`。

**修法**（三种，按优先级）：

1. **新建 httpHeaderAuth credential**：n8n 控制台 → Credentials → New → Header Auth → Name=`X-Api-Key`, Value=对应平台的 key
2. **硬编码 key 到节点**（最快，但泄 key 到工作流 JSON 里）：

```json
{
  "parameters": {
    "sendHeaders": true,
    "specifyHeaders": "keypair",
    "headerParameters": {
      "parameters": [
        {"name": "X-Api-Key", "value": "<KEY>"},
        {"name": "anthropic-version", "value": "2023-06-01"}
      ]
    }
  },
  "credentials": {}
}
```

3. **改 endpoint**：如果用户用的是其他平台的兼容 endpoint，可能根本不需要 X-Api-Key

**验证**：执行后看 execution 日志的 `headers` 字段确认实际发了哪个 header。

---

## 坑 2：HTTP Request 节点的 jsonBody 表达式引用错误

**复现条件**：Writer/Cleaner 节点的 jsonBody 用了 `$json.xxx` 引用前一个节点的输出。

**症状**：`HTTP 400 - invalid params`，body 只有 `{model: "MiniMax-M3"}`，其他字段全丢。

**根因**：`$json` 是**当前节点自身的输入**，不是上一个节点的输出。跨节点引用必须用 `$('NodeName').item.json.xxx`。

**修法**：

```javascript
// 错
jsonBody: `={{ JSON.stringify({model:'X', max_tokens:$json.write_max_tokens, system:$json.write_system, messages:$json.write_messages}) }}`

// 对
jsonBody: `={{ JSON.stringify({model:'X', max_tokens:$('KB Builder').item.json.write_max_tokens, system:$('KB Builder').item.json.write_system, messages:$('KB Builder').item.json.write_messages}) }}`
```

**注意**：如果同一个 workflow 里 Cleaner 节点写对了（用 `$('KB Builder').item.json.xxx`），而 Writer 节点写错了（用 `$json.xxx`），不要照搬 Cleaner——而是**对比**发现差异。这种不对称就是 bug 信号。

---

## 坑 3：Code 节点的 jsCode 字符串里含真换行符 → JS 语法错

**复现条件**：用 Python `json.dumps(system_prompt, ensure_ascii=False).encode("utf-8")` POST 到 n8n，PUT 工作流更新 jsCode 字段。

**症状**：`SyntaxError: Invalid or unexpected token`，0.1-0.4 秒就挂。

**根因**：n8n 解析 PUT body 是标准 JSON，字符串值里的 `\n` 会被解码为**真换行符**。n8n 把这个真换行符原样写入节点的 jsCode 字段。JS 字符串**不允许跨行**，立即语法错。

**修法**：**用 base64 编码注入**，让 jsCode 里只出现 base64 字面（无真换行）：

```javascript
// 在 n8n Code 节点里
const write_system = Buffer.from(
  '5L2g5piv6LWE5rex5YWs5LyX5Y+357yW...',  // base64 编码的 system prompt
  'base64'
).toString('utf-8');
```

Python 端：

```python
import base64, requests
prompt_b64 = base64.b64encode(system_prompt.encode('utf-8')).decode('ascii')

# 替换节点 jsCode 里的 write_system / clean_system 赋值
js = re.sub(
    r'const write_system = `.*?`;',
    f"const write_system = Buffer.from('{prompt_b64}', 'base64').toString('utf-8');",
    js, count=1, flags=re.DOTALL
)
```

**验证**：本地 `node -e "new Function('(async function(){' + code + '})');"` 解析通过再 PUT。

---

## 坑 4：Code 节点字符串里含半角双引号 → JSON 截断

**复现条件**：jsCode 里 `clean_system: "..."` 的字符串值里又包含半角双引号（如 `双引号「""」`）。

**症状**：`SyntaxError: Invalid or unexpected token`，报错在 clean_system 那行。

**根因**：Python `json.dumps(..., ensure_ascii=False)` 输出 `\"`，但 n8n 解析 JSON 后写入 jsCode 的是字面的半角双引号，JS 字符串提前结束。

**修法**：

1. **字符串值里禁用半角双引号**：全部用全角「」或单引号
2. **或**配合坑 3 用 base64 编码（base64 字符里只有 a-z A-Z 0-9 + / =，无双引号）

---

## 坑 5：regex 替换吞并多行 base64

**复现条件**：用 `re.sub(r'clean_system:[^,]+,', ...)` 替换 Code 节点里的 clean_system 赋值。

**症状**：替换后文件里 clean_system 那行变成 2000+ 字符的单行，把下一行的 `,` 和内容也吞了。

**根因**：`[^,]+` 贪婪匹配到下一个 `,`——base64 字符串里**没有 `,`**（只有字母数字加号斜杠），所以一直匹配到下一处出现 `,` 的位置（可能是下一个变量）。

**修法**：

1. **限制到行末**：`re.sub(r'clean_system: [^\n]+,', ...)` （用 `\n` 而不是 `,` 终止）
2. **或直接重写整个 jsCode**：用 f-string 拼一份干净的完整 jsCode 替换整个字段
3. **regex 用非贪婪**：注意 `[^,]+` 默认是贪婪的，必须用 `[^,]+?,` 非贪婪

**优先选方案 2**：复杂 Code 节点改 prompt 时，整体重写比逐行替换更安全。

---

## 坑 6：Code 节点的 try/catch 兜底必须有 fallback 字段

**复现条件**：KB Builder Code 节点通过 `this.helpers.httpRequest` 调外部 KB API（如 `http://122.51.231.52:8085/api/query`），API 不可达时进 catch。

**症状**：catch 块只返回 `{error: e.message}`，但下游 Writer 节点引用 `$('KB Builder').item.json.write_messages` 拿到 undefined → body 是 `{model: 'X'}` → 400 invalid params。

**修法**：catch 块**必须返回和正常路径一样的完整 schema**：

```javascript
} catch(e) {
  return [{json: {
    topic: 'fallback',
    style: '引流',
    atoms_count: 0,
    used_count: 0,
    write_messages: [{role:'user', content:'写一篇公众号爆文，主题：AI企业应用'}],
    write_system: '...',  // 同样的 system prompt
    write_max_tokens: 4000,
    clean_system: '...',
    clean_max_tokens: 3000,
    error: e.message
  }}];
}
```

**教训**：workflow 报错信息可能很模糊（"Error in workflow"），但跑不到下游节点的根因往往是**上游节点的 fallback schema 不全**。每次改 try/catch 都要保证返回结构一致。

---

## 坑 7：execution 日志 30 分钟滚动

**复现条件**：调试 workflow 时多次触发 webhook。

**症状**：想看历史 execution 时，前面的已经被滚出。

**修法**：

```python
import requests
r = requests.get(
    f"{base}/api/v1/executions",
    headers={"X-N8N-API-KEY": key},
    params={"limit": 5, "includeData": "true"},
    timeout=15
)
execs = r.json().get("data", [])
```

`includeData=true` 才能看到节点级 runData + error context（包括 stack trace + request headers + request body）。

**节省时间技巧**：触发 webhook 后**立即**拉 executions 看错误，不要等。

---

## 坑 8：workflow 改动后必须重新触发才能验证

**复现条件**：PUT /workflows/{id} 修改节点参数后，怀疑改坏了。

**修法**：

1. **本地 node 解析**：`node -e "new Function('(async function(){' + jsCode + '})');"` 检查 jsCode 语法
2. **触发 webhook**：POST /webhook/{path} 实际跑
3. **拉 executions** 看 status + error
4. **不要**相信 "PUT 返回 200" = 工作流 OK——PUT 只验证 JSON schema 合法，不验证 JS 语法和业务逻辑

---

## 完整改造 SOP（替换既有 n8n 节点的 system prompt）

按以下顺序执行，避免反复试错：

### Step 1：取工作流
```python
r = requests.get(f"{base}/api/v1/workflows/{wf_id}", headers={"X-N8N-API-KEY": key})
wf = r.json()
```

### Step 2：定位 system prompt 字段
- Code 节点：`jsCode` 字段里的 `write_system = ...` 字符串
- HTTP Request 节点：`jsonBody` 表达式里的 `system: ...`

### Step 3：备份原始代码
写到本地 `/tmp/wf_backup_{wf_id}_{timestamp}.js`，出问题能恢复。

### Step 4：base64 编码新 prompt
```python
import base64
new_prompt_b64 = base64.b64encode(new_prompt.encode('utf-8')).decode('ascii')
```

### Step 5：替换（优先整体重写 jsCode）
不要用 regex 替换字符串值里的换行/引号——直接用 Python f-string 拼一份新的完整 jsCode 替换整个字段。

### Step 6：本地解析验证
```bash
node -e "new Function('(async function(){' + jsCode + '})');"
```

### Step 7：PUT 更新
```python
payload = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"], ...}
r = requests.put(f"{base}/api/v1/workflows/{wf_id}", headers={"X-N8N-API-KEY": key}, json=payload)
```

### Step 8：触发 webhook
```python
r = requests.post(f"{base}/webhook/{path}", json={"topic": "...", "style": "..."}, timeout=180)
```

### Step 9：拉 execution 日志
看 `resultData.error` + 每个节点的 `runData`。

### Step 10：确认下游产物
- 飞书 doc 是否创建（看 archive 节点输出）
- 文章长度是否合理（不要 fallback 时的 200 字，要 1500+ 字）
- 飞书 doc raw_content > 500 字符

---

## 关键经验汇总

1. **n8n Code 节点的字符串处理是反直觉的**：JSON 解析会把 `\n` 解码成真换行符。**永远 base64 编码长字符串**。
2. **n8n PUT 返回 200 ≠ 工作流能跑**：JSON schema 合法 ≠ JS 语法合法 ≠ 业务逻辑正确。三步验证缺一不可。
3. **正则替换长字符串是定时炸弹**：用 `\n` 或非贪婪匹配，或干脆整体重写。
4. **workflow 报错信息很模糊**：99% 的"Error in workflow" 根因在某个节点输出 schema 不全。下游节点的 `$('X').item.json.yyy` 拿到 undefined 是高频坑。
5. **execution 日志是唯一调试入口**：默认只保留 30 分钟，触发后立即拉。带 `includeData=true` 才能看到节点级错误。
6. **HTTP Request 节点的 credential 类型要严格匹配 endpoint 期望的 header**：Bearer 头 / X-Api-Key 头 / query param 三种模式不互通。
7. **try/catch 兜底必须返回完整 schema**：上游节点是 schema 来源，下游节点引用任意字段都要保证 catch 路径里都有默认值。

---

## 不要做的事

- **不要**因为 credential 失败就把 key 硬编码到节点而不告知用户
- **不要**改 workflow 后不验证就直接说"已替换"
- **不要**假设 workflow 在另一台机器跑就行为一致（IP 白名单、API 配额）
- **不要**用 `LIGHTCLAW_API_KEY` 之类跨平台的 key 硬编码——它可能根本不是目标平台的有效 key