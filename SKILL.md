1|---
2|name: ai-gzh-platform
3|description: AI公众号内容生产全平台技能。一键安装完整的公众号内容生产系统，包含选题调研、爆款分析、内容撰写(khazix-writer风格)、四层自检、配图生成(GPT Image 2，支持6种风格含小姚手绘)、HTML排版、推草稿到公众号、飞书资料包创建。当用户说安装公众号平台、搭建公众号系统、装公众号技能、配置AI公众号内容平台、写公众号文章、按SOP写内容、生产今天的公众号内容、走内容流程、写篇推文时触发。
4|version: 2.0.0
5|author: 大姚
6|license: MIT
7|platforms: [linux, macos, windows]
8|metadata:
9|  hermes:
10|    tags: [wechat, content, gpt-image,publishing, automation]
11|    category: productivity
12|---
13|
14|# AI公众号内容平台
15|
16|> 一键安装 → 自动生产，从选题到交付的公众号内容全闭环系统。兼容 Coze / Hermes / OpenClaw / 任意 Agent 平台。
17|
18|## When to Use
19|
20|触发：用户说"写公众号文章 / 用 ai-gzh-platform / 生产公众号内容 / 走内容流程 / 写篇推文"时。
21|
22|## 首次安装（Phase 0：Agent 驱动引导）
23|
24|如果 `config.json` 不存在或 `setup_status != "configured"`，**禁止直接生成文章**。
25|
26|照 baoyu 式 agent 驱动流程，不是丢给 CLI 脚本：
27|
28|### Phase 0a: 自动读取（30秒，不问用户）
29|
30|并行读取：
31|- `~/.hermes/USER.md`（用户画像、主线方向、偏好）
32|- `~/.hermes/AGENTS.md`（命名约定，如"大姚=AI 名"）
33|- 系统注入的 USER PROFILE 段
34|- skill 自带 `config.example.json`
35|- `~/.hermes/.env` 是否有 `FEISHU_APP_ID/SECRET`、`WX_APPID/APPSECRET`、`GPT_IMAGE2_API_KEY`
36|
37|产出：列出「已能确定的字段」vs「真正需要问用户的字段」。
38|
39|### Phase 0b: 自动填充（不问用户）
40|
41|能从画像读出来的直接填，不问：
42|
43|| 字段 | 来源 | 依据 |
44||---|---|---|
45|| `brand_name` | AGENTS.md | "大姚=AI 名" → `大姚AI提效` |
46|| `content_directions` | USER PROFILE 主线 | "AI 企业应用"主线 + 副线 |
47|| `target_audience` | example.json 复用 | example 写得够准就复用 |
48|| `html_template.style_name` | USER PROFILE 配色偏好 | 默认 `tech-blue`，USER.md 有明确偏好则覆盖 |
49|| `image_style.name` | 检查 `assets/examples/` | 有小姚校准图 → `xiaoyao-illustrations`；没有 → `baoyu-notion` |
50|| `feishu.enabled` | .env 是否有飞书凭证 | 有 → 准备启用；没有 → false |
51|| `wechat_proxy.enabled` | .env 是否有微信凭证 | 有 → 准备启用；没有 → false |
52|
53|**禁忌**：
54|- ❌ 把"我不知道"伪装成"默认"
55|- ❌ 把"我猜的"说成"智能判断"
56|- ✅ 不确定就标"待核验"
57|
58|### Phase 0c: 交互引导 ⚠️ REQUIRED
59|
60|只剩**用户才能真正决定**的问题才问。最多 3 轮，用 `clarify` 交互（不是 CLI input）：
61|
62|**优先级排序（从高到低，已有的跳过）：**
63|
64|1. **排版风格确认** — 如果 USER.md 无明确偏好：
65|   - 用 clarify 给 4 个选项：`tech-blue(推荐/AI工具)` / `classic-blue(通用干货)` / `warm-orange(个人IP)` / `minimal-gray(严肃分析)`
66|   - 其他 6 种风格 → 用户可选"其他"自行输入
67|
68|2. **配图风格确认** — 如果 assets/examples 为空：
69|   - 用 clarify 给 3 个选项：`baoyu-notion(推荐/稳妥)` / `minimal-flat(扁平)` / `hand-drawn(手绘)`
70|   - 小姚风格需要校准图 → 提示"需要安装 5 张校准图，是否安装？"
71|
72|3. **API 模块确认** — 如果 .env 有对应凭证：
73|   - 用 clarify 问一次："检测到飞书/图片/微信凭证，是否启用对应模块？启用前会先实测验证。"
74|   - 给选项：`全部启用(推荐)` / `仅文字链路(不开图/飞书)` / `仅写作+配图` / `逐个确认`
75|
76|4. **IP 形象定义** — 如果配图风格选了 `custom-ip`：
   - 引导用户走 5 步 IP 定义流程（照 `references/ip-definition-guide.md`）
   - 第 1 问（clarify）：角色性别+职业 → 给选项：`男/产品经理` / `女/程序员` / `男/设计师` / `其他`
   - 第 2 问（clarify）：外形识别点 3-5 个 → "想想你的 IP 角色长什么样？给 3-5 个关键特征，比如'圆框眼镜+双麻花辫+柠檬黄衬衫'"
   - 第 3 问（clarify）：主色调 → 给选项：`暖橙#F97316` / `柠檬黄` / `科技蓝` / `其他`
   - 第 4 问（clarify）：性格关键词 3-5 个 → "你的 IP 是什么性格？比如'务实/强执行/幽默'或'温暖/细腻/有耐心'"
   - 第 5 问：常用道具 3-5 个 → 自由输入
   - agent 自动生成 `references/my-ip.md` + `references/my-ip-prompt.md`（照小姚格式）
   - 用 image API 生成 5 张校准样图 → 存到 `assets/examples/`
   - 后续 generate_image.py 的 prompt 自动拼接用户 IP 定义
   - **详见**：`references/ip-definition-guide.md`

**clarify 规则（照 baoyu）：**
77|- 一次一个问题，最重要的先问
78|- 用户不回答 → **不要静默替用户选默认**，报告默认值让用户看到
79|- 能从画像读的直接填，不重复问
80|- 密钥/Token 走安全链路，不在聊天回显
81|
82|### Phase 0d: 实测验证（启用前必做）
83|
84|填完**不要立刻** `enabled: true`。逐个验证：
85|- 飞书 token：`POST /auth/v3/tenant_access_token/internal` → code==0
86|- 图片 API：`POST /images/generations` → 200 + data 非空
87|- 微信代理：`GET /health` → 200
88|
89|详见 `references/setup-walkthrough.md` 阶段 4。
90|
91|**决策树：**
92|
93|| 飞书 | 图片 | 微信 | 操作 |
94||---|---|---|---|
95|| ✅ | ✅ | ✅ | 全开 |
96|| ✅ | ✅ | ❌ | 开飞书+图片，微信不发 |
97|| ✅ | ❌ | ❌ | 仅开飞书，文字链路先行 |
98|| ❌ | ✅ | ❌ | 仅开图片，文字链路先行 |
99|| ❌ | ❌ | ❌ | 全不开，纯文字链路 → Step 1-8 可跑，Step 9 跳过 |
100|
101|### Phase 0e: 交付汇总表
102|
103|配置完成后，给用户一个**可见的决策依据表**（不是"配好了"一句话）：
104|
105|```
106|✅ config.json 已生成
107|
108|## 我替你选的（基于画像）
109|| 项 | 值 | 依据 |
110||---|---|---|
111|| brand_name | 大姚AI提效 | AGENTS.md |
112|| 排版风格 | tech-blue | 默认（USER.md 无偏好） |
113|| 配图风格 | xiaoyao-illustrations | assets/examples 有校准图 |
114|
115|## 你确认的
116|| 项 | 值 |
117||---|---|
118|| API模块 | 图片+飞书启用，微信未开 |
119|
120|## 实测验证
121|| 模块 | 状态 |
122||---|---|
123|| 图片 API | ✅ 200 |
124|| 飞书 token | ✅ code=0 |
125|| 微信代理 | ⏭ 未启用 |
126|
127|## 立即可用
128|写作 + 四层自检 + HTML排版 + 配图 + 飞书资料包 ✅
129|推草稿到公众号 ⏭ 需后续配 wx-proxy
130|```
131|
132|**详见**：`references/setup-walkthrough.md`（完整配置→注入→验证→决策树→回复模板）
133|
134|### 排版风格（10选1）
135|
136|| id | 中文名 | 适合 |
137||---|---|---|
138|| `classic-blue` | 经典青蓝 | 通用干货、教程、知识卡片 |
139|| `tech-blue` | 科技蓝 | AI、SaaS、企业服务、技术产品 |
140|| `business-purple` | 商务紫 | 咨询、管理、B端解决方案 |
141|| `warm-orange` | 温暖橙 | 个人IP、成长、陪伴型内容 |
142|| `mint-green` | 薄荷绿 | 效率工具、轻教程、清爽知识内容 |
143|| `rose-red` | 玫瑰红 | 女性成长、消费、情绪价值内容 |
144|| `midnight-blue` | 深夜蓝 | 深度分析、趋势判断、行业报告 |
145|| `minimal-gray` | 极简灰 | 严肃评论、方法论、低装饰感内容 |
146|| `forest-green` | 森林绿 | 长期主义、组织管理、可持续增长 |
147|| `milk-tea` | 奶茶棕 | 生活方式、副业、温和商业化 |
148|
149|### 配图风格（6选1）
150|
151|| id | 中文名 | 适合 |
152||---|---|---|
153|| `baoyu-notion` | Notion知识卡 | 稳妥通用；封面 + 2张信息图 |
154|| `xiaoyao-illustrations` | 小姚手绘 | 原创IP人格化；封面 + 3-5张正文配图 |
155|| `hand-drawn` | 手绘风格 | 轻松、陪伴感、低压教程 |
156|| `minimal-flat` | 极简扁平 | SaaS、流程图、工具教程 |
157|| `isometric-3d` | 等距3D | 系统架构、自动化平台、科技感展示 |
158|| `custom` | 自定义prompt | 已有品牌视觉规范，需填写 `style_prompt_prefix` |
| `custom-ip` | 自定义IP形象 | 引导用户定义自己的IP角色（照 `references/ip-definition-guide.md` 走 5 步流程） |
159|
160|## 执行门禁
161|
162|每次生产前必须读取并执行 `references/execution-gate.md`。门禁优先级高于本文件中的便捷兜底；配置、模型、API 实测、视觉 QA 任一项不通过，停止正式交付并报告阻塞，不得用占位产物冒充完成。
163|
164|## 文件结构
165|
166|```
167|skills/ai-gzh-platform/
168|├── SKILL.md                        ← 本文件（路由索引 + workflow）
169|├── config.example.json             ← 配置模板
170|├── config.json                     ← 用户配置（首次安装后生成）
171|├── references/
172|│   ├── execution-gate.md           ← 强制门禁
173|│   ├── setup-walkthrough.md        ← 首次配置工作流
174|│   ├── writing-style.md            ← khazix-writer 写作风格
175|│   ├── n8n-wechat-full-prompt.md   ← n8n 公众号生产完整提示词（Writer+Cleaner 两段式）
176|│   ├── enterprise-windvane.md      ← AI企业应用风向标结构增强模式
177|│   ├── ip-definition-guide.md      ← 自定义IP形象定义引导(5步流程)
│   ├── visual-templates.md         ← 配图视觉模板(6种风格)
178|│   ├── xiaoyao-ip.md               ← 小姚IP定义
179|│   ├── style-dna.md                ← 小姚风格DNA
180|│   ├── prompt-template.md          ← 小姚prompt模板
181|│   ├── composition-patterns.md     ← 小姚构图模式
182|│   ├── qa-checklist.md             ← 配图QA检查清单
183|│   ├── two-html-pattern.md         ← 双HTML模式（微信粘贴版+推草稿版）
184|│   ├── push-draft-pitfalls.md      ← 推草稿踩坑记录
185|│   ├── push-draft-double-encoding-pitfall.md ← 双重UTF-8编码陷阱
186|│   ├── live-failures.md            ← 常见 Live Failure 速查
187|│   ├── n8n-integration-pitfalls.md ← n8n 工作流调试记录
188|│   ├── local-fallback-html-pack.md  ← 本地降级 HTML 包
189|│   ├── system-prompt.md            ← Agent System Prompt 参考
190|│   └── public-release-checklist.md  ← 公开仓库发布前隐私检查清单
191|├── scripts/
192|│   ├── init_config.py              ← 首次配置向导
193|│   ├── generate_image.py           ← GPT Image 2生成（含指数退避重试）
194|│   ├── push_draft.py               ← 微信推草稿（必须走 wx-proxy）
195|│   ├── compress_images.py          ← PNG→JPG 压缩
196|│   ├── check_title_digest.py       ← 标题/摘要字节校验（≤30B/≤54B）
197|│   └── wx-proxy.js                 ← 微信代理服务器
198|└── assets/examples/                ← 小姚风格校准样图(5张)
199|```
200|
201|## 风格路由决策表
202|
203|只保留两种写作风格，简化路由：
204|
205|| 选题关键词 | 写作风格文件 | 叠加 |
206||---|---|---|
207|| AI工具/课程/工作流/变现/n8n/飞书/线索/获客/客服/销售/自动化 | `n8n-wechat-full-prompt.md` | — |
208|| 政策解读/企业深度分析/个人视角叙事 | `writing-style.md`（khazix-writer） | — |
209|| AI企业应用/B端/SaaS/Agent落地/ROI/采购/供应商风险 | `writing-style.md` | + `enterprise-windvane.md` |
210|
211|## 生产流程（13步 Checklist）
212|
213|**核心原则**：全自动执行，异常才上报，主人只看结果。
214|
215|输出目录：`output/{date}-{slug}/`（slug: 2-4 words kebab-case）
216|
217|```
218|公众号生产 Progress:
219|- [ ] Step 1: 配比轮转判断 → state.json (round_state)
220|      按 content_ratio 轮转（默认60%-30%-10%）。读 config.json round_state 判断当前该写哪类。
221|- [ ] Step 2: 爆款调研（必做） → research.md
222|      从 content_directions 提取关键词，限定最近7天，搜索3-5条爆款标题。
223|      选题防撞：扫 covered_topics，重叠则换方向。
224|      详见 references/writing-style.md 的调研策略。
225|- [ ] Step 3: 选题评分
226|      五维评分（5分制）：生存焦虑(30%)+需求具体(20%)+可复制(25%)+画像匹配(15%)+数据支撑(10%)
227|      AI企业应用/B端选题 → 7维评分：读 references/enterprise-windvane.md
228|      决策：≥4.0直接写，3.5-3.9写但排后，<3.5淘汰。
229|- [ ] Step 4: 文章原型判断
230|      调查实验型/产品体验型/现象解读型/工具分享型/方法论分享型/enterprise-windvane型
231|      查 references/writing-style.md 原型表。
232|- [ ] Step 5: 内容撰写 → article.md
233|      查上方「风格路由决策表」选风格文件。约1200字（n8n-blogger 风格1000-1500字）。
234|      写作硬规则：禁小标题/冒号/破折号/双引号(用「」)/emoji；口语化转场；CTA公式。
235|      **⚠️ execute_code 沙箱读不到 env** → 调 generate_image.py 必须用 terminal()。
236|- [ ] Step 6: 四层自检（必做）  → qa-report.md
237|      L1 禁用词+禁用标点零命中 | L2 口语化≥5词组 | L3 观点有支撑 | L4 像真人写的
238|      enterprise-windvane 模式追加 Step 6.5 风向标结构自检（见 references/enterprise-windvane.md）
239|- [ ] Step 7: 标题打磨 ⚠️ REQUIRED
240|      标题公式：[主体]+[场景/数字]+[解决什么问题]。
241|      硬约束：title ≤ 30 字节，digest ≤ 54 字节（UTF-8，中文3B/字）。
242|      写完立刻实测：python3 scripts/check_title_digest.py --title "标题" --digest "摘要"
243|- [ ] Step 8: 落脚点检查
244|      读者拿走能直接用的是什么？步骤+截图/提示词模板/可抄作业方案 ✅ | 纯功能介绍 ❌
245|- [ ] Step 9: 配图生成 → imgs/ + prompts/*.md
246|      读 config.json image_style，按对应风格生成。
247|      先写 prompt file 到 prompts/NN-{type}-{slug}.md，再调 generate_image.py。
248|      详见 references/visual-templates.md
249|      generate_image.py: python3 scripts/generate_image.py --prompt "..." --size "1792x768" --output "imgs/cover.png"
250|- [ ] Step 10: HTML转换 → html/{slug}-微信粘贴版-v1.html + {slug}-推草稿版-v1.html
251|      双HTML模式（必做）：见 references/two-html-pattern.md
252|      推草稿前必跑：compress_images.py → HTML 引用 .jpg 不含封面 → check_title_digest.py
253|- [ ] Step 11: 资料包创建（可选，feishu.enabled=true时）
254|      飞书doc分两步写入（POST /documents → POST /blocks/{id}/children），按30/batch分批。
255|      顺序约束：飞书doc必须在HTML之前创建（CTA链接嵌入doc_id）。
256|      详见 references/push-draft-pitfalls.md 坑5-6
257|- [ ] Step 12: 推草稿到公众号（可选，wechat_proxy.enabled=true时）
258|      预处理3步：compress_images.py → HTML不嵌cover → check_title_digest.py
259|      python3 scripts/push_draft.py --title "标题" --digest "摘要" --html 推草稿版.html --cover cover.jpg --images imgs/*.jpg
260|      推完必跑验证：拉draft/get确认中文字符>1000且\u=0。详见 references/push-draft-pitfalls.md
261|- [ ] Step 13: 交付通知
262|      推送全部产出物：article.md + HTML×2 + 配图 + 资料包链接 + CTA关键词。
263|      更新 state.json: {"step":13,"pushed":true}
264|```
265|
266|### state.json Checkpoint 机制
267|
268|每步完成后更新 `output/{date}-{slug}/state.json`：
269|
270|```json
271|{
272|  "step": 5,
273|  "slug": "ai-consumer-policy",
274|  "title": null,
275|  "style": "writing-style.md",
276|  "images": [],
277|  "html_paste": null,
278|  "html_draft": null,
279|  "pushed": false
280|}
281|```
282|
283|中断后重新进入时：先读 `state.json` → 从 step+1 恢复，不从头来。
284|
285|## 合规红线
286|
287|- 禁止无数据来源的百分比
288|- 禁止极限词（最好/第一/唯一等）
289|- CTA禁止诱导关注（"关注后领取"❌，"回复XX获取"✅）
290|- **发布前必须经主人确认**
291|
292|## Reference 路由表（按需加载）
293|
294|| 需要什么 | 加载文件 |
295||---|---|
296|| 首次配置流程 | `references/setup-walkthrough.md` |
297|| 执行门禁细则 | `references/execution-gate.md` |
298|| khazix-writer 写作风格 | `references/writing-style.md` |
299|| n8n 完整两段式 prompt | `references/n8n-wechat-full-prompt.md` |
300|| 企业风向标结构增强 | `references/enterprise-windvane.md` |
301|| 自定义IP定义引导 | `references/ip-definition-guide.md` |
| 配图视觉模板 | `references/visual-templates.md` |
302|| 小姚IP定义 | `references/xiaoyao-ip.md` |
303|| 小姚风格DNA | `references/style-dna.md` |
304|| 小姚prompt模板 | `references/prompt-template.md` |
305|| 小姚构图模式 | `references/composition-patterns.md` |
306|| 配图QA检查 | `references/qa-checklist.md` |
307|| 双HTML模式 | `references/two-html-pattern.md` |
308|| 推草稿踩坑 | `references/push-draft-pitfalls.md` |
309|| 双重UTF-8编码陷阱 | `references/push-draft-double-encoding-pitfall.md` |
310|| 常见 Live Failure | `references/live-failures.md` |
311|| n8n 工作流调试 | `references/n8n-integration-pitfalls.md` |
312|| 本地降级 HTML | `references/local-fallback-html-pack.md` |
313|| System Prompt 参考 | `references/system-prompt.md` |
314|| 公开仓库发布检查 | `references/public-release-checklist.md` |
315|
316|## Pitfalls 速查
317|
318|1. **标题字节超限** → 写完立刻跑 `check_title_digest.py`，每汉字3B
319|2. **execute_code 读不到 env** → 调 `generate_image.py` 用 `terminal()` 不用 `execute_code`
320|3. **推草稿 HTML 不压缩** → 先 `compress_images.py` 转 JPG，推草稿版不含封面
321|4. **飞书 doc 一次写超50个block** → 按30/batch分批
322|5. **L1自检「这意味着」漏检** → `content.count(w)>0` 不是 `w in content`
323|6. **GPT Image 2 偶有英文字母混入** → 记录即可，不重生成
324|7. **只产一个HTML版本** → 永远产两个（微信粘贴版+推草稿版）
325|8. **表头分隔行被渲染** → 过滤 `all(set(c)<=set("-: ") for c in row)`
326|
327|详见 `references/live-failures.md`
328|
329|## 验收表
330|
331|每次正式交付必须输出：
332|
333|| 项 | 结果 |
334||---|---|
335|| skill | ai-gzh-platform |
336|| config | configured / blocked |
337|| article workflow | 13步已执行 / 哪步阻塞 |
338|| image model | 实际 model |
339|| image endpoint | 已实测 2xx / 阻塞 |
340|| image files | cover + n 张正文图 |
341|| visual QA | 通过 / 哪张失败 |
342|| article QA | L1-L4 通过 / 哪层失败 |
343|| title bytes | x / 30 |
344|| digest bytes | x / 54 |
345|| HTML | 微信粘贴版 + 推草稿版 / 阻塞 |
346|| optional publish | 飞书/公众号草稿是否执行 |