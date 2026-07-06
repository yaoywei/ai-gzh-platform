---
name: ai-gzh-platform
description: AI公众号内容生产全平台技能。一键安装完整的公众号内容生产系统，包含选题调研、爆款分析、内容撰写(n8n-blogger B端爆文为主，khazix-writer 备选)、四层自检、配图生成(GPT Image 2，支持6种风格含小姚手绘)、HTML排版、推草稿到公众号、飞书资料包创建。当用户说安装公众号平台、搭建公众号系统、装公众号技能、配置AI公众号内容平台、写公众号文章、按SOP写内容、生产今天的公众号内容、走内容流程、写篇推文时触发。
version: 2.1.0
author: 大姚
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wechat, content, gpt-image, publishing, automation, multiplatform]
    category: productivity
---

# AI公众号内容平台

> 一键安装 → 自动生产，从选题到交付的公众号内容全闭环系统。兼容 Coze / Hermes / OpenClaw / 任意 Agent 平台。

## When to Use

触发：用户说"写公众号文章 / 用 ai-gzh-platform / 生产公众号内容 / 走内容流程 / 写篇推文"时。

## 首次安装（Phase 0：Agent 驱动引导）

如果 `config.json` 不存在或 `setup_status != "configured"`，**禁止直接生成文章**。

照 baoyu 式 agent 驱动流程，不是丢给 CLI 脚本：

### Phase 0a: 自动读取（30秒，不问用户）

并行读取：
- `~/.hermes/USER.md`（用户画像、主线方向、偏好）
- `~/.hermes/AGENTS.md`（命名约定，如"品牌名=AI 名"）
- 系统注入的 USER PROFILE 段
- skill 自带 `config.example.json`
- `~/.hermes/.env` 是否有 `FEISHU_APP_ID/SECRET`、`WX_APPID/APPSECRET`、`GPT_IMAGE2_API_KEY`

产出：列出「已能确定的字段」vs「真正需要问用户的字段」。

### Phase 0b: 自动填充（不问用户）

能从画像读出来的直接填，不问：

| 字段 | 来源 | 依据 |
|---|---|---|
| `brand_name` | AGENTS.md | "品牌名=AI 名" → `你的品牌名` |
| `content_directions` | USER PROFILE 主线 | "AI 企业应用"主线 + 副线 |
| `target_audience` | example.json 复用 | example 写得够准就复用 |
| `html_template.style_name` | USER PROFILE 配色偏好 | 默认 `tech-blue`，USER.md 有明确偏好则覆盖 |
| `image_style.name` | 检查 `assets/examples/` | 有小姚校准图 → `xiaoyao-illustrations`；没有 → `baoyu-notion` |
| `feishu.enabled` | .env 是否有飞书凭证 | 有 → 准备启用；没有 → false |
| `wechat_proxy.enabled` | .env 是否有微信凭证 | 有 → 准备启用；没有 → false |

**禁忌**：
- ❌ 把"我不知道"伪装成"默认"
- ❌ 把"我猜的"说成"智能判断"
- ✅ 不确定就标"待核验"

### Phase 0c: 交互引导 ⚠️ REQUIRED

只剩**用户才能真正决定**的问题才问。最多 3 轮，用 `clarify` 交互（不是 CLI input）：

**优先级排序（从高到低，已有的跳过）：**

1. **排版风格确认** — 如果 USER.md 无明确偏好：
   - 用 clarify 给 4 个选项：`tech-blue(推荐/AI工具)` / `classic-blue(通用干货)` / `warm-orange(个人IP)` / `minimal-gray(严肃分析)`
   - 其他 6 种风格 → 用户可选"其他"自行输入

2. **配图风格确认** — 如果 assets/examples 为空：
   - 用 clarify 给 3 个选项：`baoyu-notion(推荐/稳妥)` / `minimal-flat(扁平)` / `hand-drawn(手绘)`
   - 小姚风格需要校准图 → 提示"需要安装 5 张校准图，是否安装？"

3. **API 模块确认** — 如果 .env 有对应凭证：
   - 用 clarify 问一次："检测到飞书/图片/微信凭证，是否启用对应模块？启用前会先实测验证。"
   - 给选项：`全部启用(推荐)` / `仅文字链路(不开图/飞书)` / `仅写作+配图` / `逐个确认`

4. **IP 形象定义** — 如果配图风格选了 `custom-ip`：
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
- 一次一个问题，最重要的先问
- 用户不回答 → **不要静默替用户选默认**，报告默认值让用户看到
- 能从画像读的直接填，不重复问
- 密钥/Token 走安全链路，不在聊天回显

### Phase 0d: 实测验证（启用前必做）

填完**不要立刻** `enabled: true`。逐个验证：
- 飞书 token：`POST /auth/v3/tenant_access_token/internal` → code==0
- 图片 API：`POST /images/generations` → 200 + data 非空
- 微信代理：`GET /health` → 200

详见 `references/setup-walkthrough.md` 阶段 4。

**决策树：**

| 飞书 | 图片 | 微信 | 操作 |
|---|---|---|---|
| ✅ | ✅ | ✅ | 全开 |
| ✅ | ✅ | ❌ | 开飞书+图片，微信不发 |
| ✅ | ❌ | ❌ | 仅开飞书，文字链路先行 |
| ❌ | ✅ | ❌ | 仅开图片，文字链路先行 |
| ❌ | ❌ | ❌ | 全不开，纯文字链路 → Step 1-8 可跑，Step 9 跳过 |

### Phase 0e: 交付汇总表

配置完成后，给用户一个**可见的决策依据表**（不是"配好了"一句话）：

```
✅ config.json 已生成

## 我替你选的（基于画像）
| 项 | 值 | 依据 |
|---|---|---|
| brand_name | 你的品牌名 | AGENTS.md |
| 排版风格 | tech-blue | 默认（USER.md 无偏好） |
| 配图风格 | xiaoyao-illustrations | assets/examples 有校准图 |

## 你确认的
| 项 | 值 |
|---|---|
| API模块 | 图片+飞书启用，微信未开 |

## 实测验证
| 模块 | 状态 |
|---|---|
| 图片 API | ✅ 200 |
| 飞书 token | ✅ code=0 |
| 微信代理 | ⏭ 未启用 |

## 立即可用
写作 + 四层自检 + HTML排版 + 配图 + 飞书资料包 ✅
推草稿到公众号 ⏭ 需后续配 wx-proxy
```

**详见**：`references/setup-walkthrough.md`（完整配置→注入→验证→决策树→回复模板）

### 排版风格（10选1）

| id | 中文名 | 适合 |
|---|---|---|
| `classic-blue` | 经典青蓝 | 通用干货、教程、知识卡片 |
| `tech-blue` | 科技蓝 | AI、SaaS、企业服务、技术产品 |
| `business-purple` | 商务紫 | 咨询、管理、B端解决方案 |
| `warm-orange` | 温暖橙 | 个人IP、成长、陪伴型内容 |
| `mint-green` | 薄荷绿 | 效率工具、轻教程、清爽知识内容 |
| `rose-red` | 玫瑰红 | 女性成长、消费、情绪价值内容 |
| `midnight-blue` | 深夜蓝 | 深度分析、趋势判断、行业报告 |
| `minimal-gray` | 极简灰 | 严肃评论、方法论、低装饰感内容 |
| `forest-green` | 森林绿 | 长期主义、组织管理、可持续增长 |
| `milk-tea` | 奶茶棕 | 生活方式、副业、温和商业化 |

### 配图风格（6选1）

| id | 中文名 | 适合 |
|---|---|---|
| `baoyu-notion` | Notion知识卡 | 稳妥通用；封面 + 2张信息图 |
| `xiaoyao-illustrations` | 小姚手绘 | 原创IP人格化；封面 + 3-5张正文配图 |
| `hand-drawn` | 手绘风格 | 轻松、陪伴感、低压教程 |
| `minimal-flat` | 极简扁平 | SaaS、流程图、工具教程 |
| `isometric-3d` | 等距3D | 系统架构、自动化平台、科技感展示 |
| `custom` | 自定义prompt | 已有品牌视觉规范，需填写 `style_prompt_prefix` |
| `custom-ip` | 自定义IP形象 | 引导用户定义自己的IP角色（照 `references/ip-definition-guide.md` 走 5 步流程） |

## 执行门禁

每次生产前必须读取并执行 `references/execution-gate.md`。门禁优先级高于本文件中的便捷兜底；配置、模型、API 实测、视觉 QA 任一项不通过，停止正式交付并报告阻塞，不得用占位产物冒充完成。

## 文件结构

```
skills/ai-gzh-platform/
├── SKILL.md                        ← 本文件（路由索引 + workflow）
├── config.example.json             ← 配置模板
├── config.json                     ← 用户配置（首次安装后生成）
├── references/
│   ├── execution-gate.md           ← 强制门禁
│   ├── setup-walkthrough.md        ← 首次配置工作流
│   ├── writing-style.md            ← khazix-writer 写作风格
│   ├── n8n-wechat-full-prompt.md   ← n8n 公众号生产完整提示词（Writer+Cleaner 两段式）
│   ├── enterprise-windvane.md      ← AI企业应用风向标结构增强模式
│   ├── ip-definition-guide.md      ← 自定义IP形象定义引导(5步流程)
│   ├── visual-templates.md         ← 配图视觉模板(6种风格)
│   ├── xiaoyao-ip.md               ← 小姚IP定义
│   ├── style-dna.md                ← 小姚风格DNA
│   ├── prompt-template.md          ← 小姚prompt模板
│   ├── composition-patterns.md     ← 小姚构图模式
│   ├── qa-checklist.md             ← 配图QA检查清单
│   ├── two-html-pattern.md         ← 双HTML模式（微信粘贴版+推草稿版）
│   ├── push-draft-pitfalls.md      ← 推草稿踩坑记录
│   ├── push-draft-double-encoding-pitfall.md ← 双重UTF-8编码陷阱
│   ├── live-failures.md            ← 常见 Live Failure 速查
│   ├── n8n-integration-pitfalls.md ← n8n 工作流调试记录
│   ├── local-fallback-html-pack.md  ← 本地降级 HTML 包
│   ├── system-prompt.md            ← Agent System Prompt 参考
│   ├── public-release-checklist.md  ← 公开仓库发布前隐私检查清单
│   └── user-asset-ingestion.md     ← 用户素材盘点与分配（多轮对话收图后必走）
├── scripts/
│   ├── init_config.py              ← 首次配置向导
│   ├── generate_image.py           ← GPT Image 2生成（含指数退避重试）
│   ├── push_draft.py               ← 微信推草稿（必须走 wx-proxy）
│   ├── compress_images.py            ← PNG→JPG 压缩
│   ├── md_to_html.py                 ← Markdown → tech-blue HTML（含占位框/签名行）
│   ├── compose_from_text.py          ← Pillow 双栏对比图：用户截图截断/模糊时，从源文字重排合成（Pitfall #30）
│   ├── check_title_digest.py         ← 标题/摘要字节校验（≤30B/≤54B）
│   └── wx-proxy.js                 ← 微信代理服务器
└── assets/examples/                ← 小姚风格校准样图(5张)
```

## 风格路由决策表

只保留两种写作风格，简化路由：

| 选题关键词 | 写作风格文件 | 叠加 |
|---|---|---|
| AI工具/课程/工作流/变现/n8n/飞书/线索/获客/客服/销售/自动化 | `n8n-wechat-full-prompt.md` | — |
| 政策解读/企业深度分析/个人视角叙事 | `writing-style.md`（khazix-writer） | — |
| AI企业应用/B端/SaaS/Agent落地/ROI/采购/供应商风险 | `writing-style.md` | + `enterprise-windvane.md` |

## 生产流程（13步 Checklist）

**核心原则**：全自动执行，异常才上报，主人只看结果。

输出目录：`output/{date}-{slug}/`（slug: 2-4 words kebab-case）

```
公众号生产 Progress:
- [ ] Step 1: 配比轮转判断 → state.json (round_state)
      按 content_ratio 轮转（默认60%-30%-10%）。读 config.json round_state 判断当前该写哪类。
- [ ] Step 2: 爆款调研（必做） → research.md
      从 content_directions 提取关键词，限定最近7天，搜索3-5条爆款标题。
      选题防撞：扫 covered_topics，重叠则换方向。
      详见 references/writing-style.md 的调研策略。
- [ ] Step 3: 选题评分
      五维评分（5分制）：生存焦虑(30%)+需求具体(20%)+可复制(25%)+画像匹配(15%)+数据支撑(10%)
      AI企业应用/B端选题 → 7维评分：读 references/enterprise-windvane.md
      决策：≥4.0直接写，3.5-3.9写但排后，<3.5淘汰。
- [ ] Step 4: 文章原型判断
      调查实验型/产品体验型/现象解读型/工具分享型/方法论分享型/enterprise-windvane型
      查 references/writing-style.md 原型表。
- [ ] Step 4.5: P2 功能/数据/渠道预清点 ⚠️ REQUIRED
      写之前先问/自查 3 类素材（不要写完才被打回）：
      1. **数据**：所有要写的百分比/工时/月省/转化率/效果数字——是否有真实来源？
         没有就用定性表述（"大半天"/"通常"），或加"按你账号实测"前置定语。
      2. **功能/产品**：要写的"飞书多维表格""RAG""可视化 UI""自动审核"——用户真的做出来了吗？
         没做就改模糊表述（"飞书机器人推送"代替"飞书多维表格选题池"）。
      3. **渠道/CTA**：要写的"加微信""闲鱼链接""资料包二维码"——用户当前渠道状态如何？
         用户说"明天才挂闲鱼" → 当天 CTA 不能写闲鱼链接，写"先聊"。
         触发：用 `clarify` 一句话确认；用户没明确时输出"我假设 X，如果错告诉我"清单。
      输出格式（不是元数据，是 prompt 喂给 Writer）：
      ```
      ## 本篇真实可用素材（来自用户/调研）
      - 数据：1 个号日发 1-2 篇（行业常识）、用户账号实测工时（待实测）
      - 功能：服务器控制台 ✅、飞书机器人 ✅、ai-gzh-platform Skill 库 ✅、飞书多维表格 ❌（没做）
      - 渠道：个人微信「...」（✅ 可写）；闲鱼链接（❌ 明天才挂）

      ## 不得写入（替代为）
      - "飞书多维表格选题池" → "飞书机器人推送草稿"
      - "1 人 3 号变 1 人 5 号" → 删掉
      - "闲鱼 ¥199 一次性" → "加微信先聊"
      ```
- [ ] Step 5: 内容撰写 → article.md
      查上方「风格路由决策表」选风格文件。约1200字（n8n-blogger 风格1000-1500字）。
      写作硬规则（**仅 khazix-writer 风格**）：禁小标题/冒号/破折号/双引号(用「」)/emoji；口语化转场；CTA公式。
      **n8n-blogger 风格另议**：保留表格、❌/✅ 标记、破折号、英文双引号等 B 端爆文常见标点，只跑 Cleaner 的禁词表（赋能/闭环/颠覆式/颗粒度/抓手/底层逻辑/值得注意的是/综上所述/首先其次最后/总体而言/不容忽视）。
      写作前必须先看 references/<style-file>.md 决定走哪条规则，不要无脑套 khazix 的硬规则。
      **⚠️ execute_code 沙箱读不到 env** → 调 generate_image.py 必须用 terminal()。
- [ ] Step 6: 五层自检（必做）  → qa-report.md
      L1 禁用词+禁用标点零命中 | L2 口语化≥5词组 | L3 观点有支撑 | L4 像真人写的
      **L5 反虚构（2026-07-06 用户硬偏好，正式提升为五层之一）**：
        ① 数字/百分比/工时/业务数据 全部有真实来源，无源 = 删/改模糊；
        ② 没做的产品/功能/Skill 不能写进文章；
        ③ 渠道/CTA 必须反映用户当前状态（用户说"先不挂闲鱼"则当天不能写闲鱼链接）；
        ④ 截图位/AI 配图位必须输出"哪个用户做/哪个 AI 做"分工清单（参考 references/n8n-wechat-full-prompt.md 「素材位分工」节）。
        详见 `references/n8n-wechat-full-prompt.md` 顶部「用户硬偏好」节。
      enterprise-windvane 模式追加 Step 6.5 风向标结构自检（见 references/enterprise-windvane.md）
- [ ] Step 7: 标题打磨 ⚠️ REQUIRED
      标题公式：[主体]+[场景/数字]+[解决什么问题]。
      硬约束：title ≤ 30 字节，digest ≤ 54 字节（UTF-8，中文3B/字）。
      写完立刻实测：python3 scripts/check_title_digest.py --title "标题" --digest "摘要"
- [ ] Step 8: 落脚点检查
      读者拿走能直接用的是什么？步骤+截图/提示词模板/可抄作业方案 ✅ | 纯功能介绍 ❌
- [ ] Step 9: 配图生成 → imgs/ + prompts/*.md
      读 config.json image_style，按对应风格生成。
      先写 prompt file 到 prompts/NN-{type}-{slug}.md，再调 generate_image.py。
      详见 references/visual-templates.md
      generate_image.py: python3 scripts/generate_image.py --prompt "..." --size "1792x768" --output "imgs/cover.png"
- [ ] Step 9.5: 用户素材盘点与分配 ⚠️ REQUIRED（多轮收图后）
      见 `references/user-asset-ingestion.md` 4 步流程：
      ① vision_analyze 逐张盘点 → ② 3 类分类（当前文核心 / 姊妹篇延伸 / 不可用）
      → ③ 输出位置分配表 → ④ 全部嵌入 HTML（真实素材不要虚线框）
- [ ] Step 10: HTML转换 → html/{slug}-微信粘贴版-v1.html + {slug}-推草稿版-v1.html
      双HTML模式（必做）：见 references/two-html-pattern.md
      **两个 HTML 不能复用**：
        - 微信粘贴版：用 `md_to_html.py`（浏览器样式 + base64 内嵌图），用户自己粘贴到公众号后台
        - 推草稿版：用 `references/wechat-native-html-template.md` 的 `md_to_wechat_native()`（**全行内 style + 微信原生标签** + 相对路径 imgs/）
      **为什么不能复用**：微信草稿箱编辑器是结构化编辑器，会过滤 `<style>` 块、丢 `class=""`、丢 `data-src`——浏览器版推过去会丢虚线框/微信号块/图片。详见 push-draft-pitfalls.md 坑 10。
      **推草稿版反例**（手机端实测 2026-07-06）：不能用 `<ul>/<ol>/<li>`（微信会插入空 li）、不能用 `<thead>/<tbody>` 嵌套。改用 `<p>● 内容</p>` + position absolute 模拟列表，表格改"卡片化"（表头 `<p>━━━ A|B|C ━━━</p>` + 行 `<p style="background:...;">A | B | C</p>`）。详见 push-draft-pitfalls.md 坑 13。
      **字号规范**（手机端 14-15px 偏小）：正文 16-17px / line-height 2.0（不要 1.75），H1 22-24px / H2 19-20px / H3 17-18px。
      推草稿前必跑：compress_images.py → HTML 引用 .jpg 不含封面 → check_title_digest.py
- [ ] Step 11: 资料包创建（可选，feishu.enabled=true时）
      飞书doc分两步写入（POST /documents → POST /blocks/{id}/children），按30/batch分批。
      顺序约束：飞书doc必须在HTML之前创建（CTA链接嵌入doc_id）。
      详见 references/push-draft-pitfalls.md 坑5-6

      **⚠️ 资料包内容规范**：资料包是公众号文章的**补充材料**，不是复制版。
      资料包应包含：
      - 核心结论速览（3-5条关键数据点）
      - 详细案例/服务商对比清单（文章中提到但未展开的内容）
      - 避坑指南/选型建议
      - 实操Checklist（读者可直接使用的清单）
      - 常见问题FAQ
      - 延伸阅读/参考资料

      **⚠️ 权限设置**：创建文档后必须设置公开权限，否则公众号CTA链接读者打不开。
      ```python
      PATCH /open-apis/drive/v1/permissions/{doc_id}/public?type=docx
      Body: {"external_access_entity": "open", "link_share_entity": "anyone_readable"}
      ```
- [ ] Step 12: 推草稿到公众号（可选，wechat_proxy.enabled=true时）
      传输层详见 `wechat-official-account` skill（两个静默损坏bug + wx-proxy部署 + 错误码表）。
      预处理3步：compress_images.py → HTML不嵌cover → check_title_digest.py
      python3 scripts/push_draft.py --title "标题" --digest "摘要" --html 推草稿版.html --cover cover.jpg --images imgs/*.jpg
      推完自动验证：拉draft/get确认中文字符>1000且\u=0。失败自动删草稿+诊断Bug#1/Bug#2。

      **⚠️ WX_PROXY_SERVER 必须 export**：`source ~/.hermes/.env` 后必须 `export WX_PROXY_SERVER`，否则 Python 子进程拿不到。
      完整命令：`source ~/.hermes/.env && export WX_PROXY_SERVER WX_PROXY_PORT WX_PROXY_TOKEN WX_APPID WX_APPSECRET && python3 scripts/push_draft.py ...`
- [ ] Step 13: 交付通知
      推送全部产出物：article.md + HTML×2 + 配图 + 资料包链接 + CTA关键词。
      更新 state.json: {"step":13,"pushed":true}

- [ ] Step 14: 多平台分发（可选，aitoearn MCP 可用时）
      加载 `aitoearn-multisite` skill + 读取 `references/multiplatform-content-conversion.md`。

      **转化不是改格式，是换语言体系说话。**

      14.1 提炼母核：从article.md提取1句话核心观点+3个支撑论据。
      14.2 按平台转译（不是复制粘贴，是用目标平台的原生语言重新讲述）：
      - 小红书（xhs）：标题≤20字，正文≤1000字，emoji+清单体+标签，图文轮播6-9张
      - 抖音（douyin）：标题≤30字，正文≤1000字，口语化+冲突感，轮播6-12张
      - 视频号（wxSph）：标题≤16字，正文≤1000字，口播+字幕+金句
      - 快手（KWAI）：标题≤30字，仅视频
      - B站（bilibili）：标题≤79字，简介≤249字，仅视频
      14.3 生成视觉资产：**用归藏 guizang-social-card-skill**（已安装，~/.hermes/skills/guizang-social-card-skill/）
          - Swiss网格风（IKB Blue）适合AI/工具/效率赛道
          - 每页选不同recipe（S01封面/S05误区/S02对比/S11要点/S06流程/S07总结）
          - 优先用真实截图，AI生图只做封面
          - ⚠️ 不要手搓HTML轮播图，归藏skill已解决排版问题
          - 详见 references/multiplatform-content-conversion.md「视觉渲染」节
      14.4 用AiToEarn发布：MCP工具 createChannelPublishFlow → publishChannelTaskNow

      ⚠️ 前置条件：用户需在 aitoearn.cn 绑定各平台账号。
      ⚠️ 首次使用需确认 AiToEarn MCP 已配置（见 aitoearn-multisite skill）。
```

### state.json Checkpoint 机制

每步完成后更新 `output/{date}-{slug}/state.json`：

```json
{
  "step": 5,
  "slug": "ai-consumer-policy",
  "title": null,
  "style": "writing-style.md",
  "images": [],
  "html_paste": null,
  "html_draft": null,
  "pushed": false
}
```

中断后重新进入时：先读 `state.json` → 从 step+1 恢复，不从头来。

## 合规红线

- 禁止无数据来源的百分比
- 禁止极限词（最好/第一/唯一等）
- CTA禁止诱导关注（"关注后领取"❌，"回复XX获取"✅）
- **发布前必须经主人确认**

## Reference 路由表（按需加载）

| 需要什么 | 加载文件 |
|---|---|
| 首次配置流程 | `references/setup-walkthrough.md` |
| 执行门禁细则 | `references/execution-gate.md` |
| khazix-writer 写作风格 | `references/writing-style.md` |
| n8n 完整两段式 prompt | `references/n8n-wechat-full-prompt.md` |
| 企业风向标结构增强 | `references/enterprise-windvane.md` |
| 自定义IP定义引导 | `references/ip-definition-guide.md` |
| 配图视觉模板 | `references/visual-templates.md` |
| 小姚IP定义 | `references/xiaoyao-ip.md` |
| 小姚风格DNA | `references/style-dna.md` |
| 小姚prompt模板 | `references/prompt-template.md` |
| 小姚构图模式 | `references/composition-patterns.md` |
| 配图QA检查 | `references/qa-checklist.md` |
| **推草稿版 HTML 适配（行内样式模板）** | **`references/wechat-native-html-template.md`**（推草稿版必须全内联 style + 微信原生标签，与浏览器粘贴版分两个文件生成） |
| 推草稿踩坑 | `references/push-draft-pitfalls.md` |
| 双重UTF-8编码陷阱 | `references/push-draft-double-encoding-pitfall.md` |
| 常见 Live Failure | `references/live-failures.md` |
| n8n 工作流调试 | `references/n8n-integration-pitfalls.md` |
| 本地降级 HTML | `references/local-fallback-html-pack.md` |
| System Prompt 参考 | `references/system-prompt.md` |
| 公开仓库发布检查 | `references/public-release-checklist.md` |
| 多平台分发 | `aitoearn-multisite` skill（独立 skill） + `references/multiplatform-content-conversion.md`（转化方法论+视觉规范+HTML轮播pipeline） |
| **用户素材盘点与分配** | **`references/user-asset-ingestion.md`（多轮收图后必走）** |

## Pitfalls 速查

> **设计铁律（用户硬偏好 2026-07-06 升级）**：**所有**需要用户替换/补充/确认的素材位（截图/二维码/对比图/产品图/CTA 块）**统一用虚线框 + 醒目文字标签**——读者一眼能看出"这个位置需要人"。截图位用橙色虚线（#F59E0B + #FFFBEB），AI 配图位用蓝色虚线（#2563EB + #EFF6FF），微信号 CTA 块用蓝色实线边框（#2563EB + #F0F7FF）。用户原话："那个虚线框蛮好看的 可以在以后所有的图片都加一个虚线框"。

1. **标题字节超限** → 写完立刻跑 `check_title_digest.py`，每汉字3B
2. **execute_code 读不到 env** → 调 `generate_image.py` 用 `terminal()` 不用 `execute_code`
3. **推草稿 HTML 不压缩** → 先 `compress_images.py` 转 JPG，推草稿版不含封面
4. **飞书 doc 一次写超50个block** → 按30/batch分批
5. **L1自检「这意味着」漏检** → `content.count(w)>0` 不是 `w in content`
6. **GPT Image 2 偶有英文字母混入** → 记录即可，不重生成
7. **只产一个HTML版本** → 永远产两个（微信粘贴版+推草稿版）
8. **表头分隔行被渲染** → 过滤 `all(set(c)<=set("-: ") for c in row)`
9. **MiniMax Token Plan 2056** → vision_analyze 等 LLM 调用返回 rate_limit_error，视觉 QA 被阻塞时记录到验收表「visual QA: ⚠️ 跳过（Token Plan 用量上限）」，不阻塞 HTML/交付。
10. **飞书 block_type 编号错误** → 飞书 docx API block_type 不是自增整数，必须查 `references/feishu-block-pitfall.md` 速查表。写入前先用 1 个 block 测试格式，通过再批量（1770001 invalid param）。
11. **WX_PROXY_SERVER 未设置** → `push_draft.py` 报 `Invalid URL 'http://:8787/...'`，host 为空。修法：`~/.hermes/.env` 添加 `WX_PROXY_SERVER=本机IP`，运行时 `source .env && export WX_PROXY_SERVER`。
12. **飞书资料包与公众号文章重复** → 资料包是补充材料（服务商对比/避坑指南/实操清单/FAQ），不是文章复制版。Step 11 必须独立设计内容结构。
13. **飞书文档权限未开放** → 创建后默认仅组织内可见，需调用 `PATCH /drive/v1/permissions/{token}/public` 设置 `link_share_entity: anyone_readable`，否则公众号 CTA 链接读者打不开。
14. **引导内容硬编码作者品牌名** → 新用户 clone 后在引导/示例中看到作者实际公众号名。发布前 `grep -rn '实际品牌名' SKILL.md references/`，全部替换为"你的品牌名"通用占位符。详见 `references/public-release-checklist.md` 第5条。
15. **视觉规范未标注来源** → 用户明确反感把二手总结当官方规则。任何视觉规范（字号/留白/布局）必须标注来源和可信度。区分"平台官方规则✅"vs"行业经验总结⚠️"。详见 `references/multiplatform-content-conversion.md` 视觉规范节。
16. **多平台分发改尺寸不改内核** → 把公众号文章截图发小红书或读一遍发抖音是无效搬运。必须按平台"原生语言"重新讲述母核。详见 `references/multiplatform-content-conversion.md` 转化三步法。
17. **GPT Image 2 中文文字渲染不稳定** → prompt里写"Large bold Chinese title '别再靠阅读分成赚钱了'"，AI可能渲染成英文。GPT Image 2对长中文句子的渲染不可靠。**对策**：① AI生图只做纯视觉背景（渐变/纹理/产品图），文字用代码叠加；② 或用归藏guizang-social-card-skill走HTML渲染路线（文字100%准确）；③ 短中文词（2-4字）比长句子渲染成功率高。
18. **generate_image.py 静默失败** → 脚本exit code=1但无输出。原因：可能是Python环境或import问题。**直接用requests调API更可靠**：`source ~/.env && export $(grep GPT_IMAGE2_API_KEY ~/.hermes/.env) && python3 -c "import requests,base64,json,os; ..."`。详见 `references/multiplatform-content-conversion.md`「AI生图」节。
19. **n8n-blogger 风格被混成 khazix-writer 语气（2026-07-06 用户原话："你好像是用的卡兹克的写法"）** → 结构（表格/❌✅/反问）能套用，但语气必须冷峻。**自检**：搜"我帮你""你团队里""别担心"，出现就改。详见 `references/n8n-wechat-full-prompt.md` 顶部「用户硬偏好」节第 3 条。
20. **n8n 标题"没头没尾"（2026-07-06 用户原话）** → 标题必须有「数字+时间+动作+结果」四要素，缺一个就改。详见 `references/n8n-wechat-full-prompt.md` 顶部第 4 条。
21. **AI 生图 API 单次请求超时（60s+）常见**（2026-07-06 实测） → 脚本默认 300s timeout + 3 retries，但仍可能 5+ 分钟才返回。**对策**：用 background=true 跑图像生成，主流程不阻塞。**批量生成时用 for 循环串行**（并发会触发 API 限流）。
20. **检查脚本意外修改源文件** → 写「检查/自检」脚本时，**只读不写**。如果脚本既检查又 `replace()` 修改文件，每次跑都会覆盖你手工的修正（比如破折号 `——` 被替换成 `,`、中英符号被改写），而且报错"修不好"是因为脚本在反复回滚。**修法**：检查脚本只 print 结果；要做清洗就用单独脚本，且只跑一次。教训：2026-07-06 写"对禁词+标点"检查脚本时，把 `prose.replace('——', '，')` 放进了 checker，每次跑都把签名行 `——` 改成 `，`。
21. **snap chromium 渲染本地 HTML 必须走 HTTP** → snap 安装的 chromium 拒绝 `file://` 协议（ERR_FILE_NOT_FOUND），但能正常访问 `http://localhost:xxxx`。**修法**：用 `python3 -m http.server 8766`（避开端口冲突）起个临时服务，HTML 放 cwd 下，再用 chromium 访问 `http://localhost:8766/xxx.html`。DrissionPage 同样的限制。教训：2026-07-06 渲染预览时反复 ERR_ACCESS_DENIED，最后起 http.server 才出图。
22. **占位框的颜色语义** → 渲染时用两种占位框视觉区分：**截图位 = 橙色虚线（#F59E0B 边 + #FFFBEB 底）**；**AI 配图位 = 蓝色虚线（#2563EB 边 + #EFF6FF 底）**。读者一眼能看出"哪个要人来补、哪个等机器生成"。详见 `scripts/md_to_html.py` 的 `render_placeholder_box()`。
23. **素材位分工没说清（2026-07-06 用户原话："到底是需要我提供真实的截图还是 有些地方是可以直接让gpt-image-2产出图的呀"）** → 当文章有 ≥ 3 个 SCREENSHOT 占位符时，agent **必须**额外输出一张「素材位分工清单」表（哪几个用户做、哪几个 AI 做、何时交）发到聊天，不能只把占位符嵌 HTML 就完事。详见 `references/n8n-wechat-full-prompt.md` 「素材位分工」节。
24. **5 张图 base64 内嵌 ≈ 8MB，触顶飞书发送通道（2026-07-06 实测）** → 微信粘贴版默认 4 张 1792x1024 图 ≈ 1.5MB；如改 5 张（封面+4 Step），base64 内嵌后 HTML 涨到 **7.96 MB**。飞书消息体上限 **4MB**（send_message/IM text 通道会失败），文件附件上限 **10MB**（可发）。**修法**：5+ 张图版本必须走 `feishu-send-attachment` 脚本（`msg_type=file`），不能 send_message 走 IM 通道。详见 `references/two-html-pattern.md` 「5 张图边界」节。
25. **`for` 循环跑多张 AI 生图 → 整批被 SIGTERM 一次性 kill（2026-07-06 实测）** → Pitfall #21 已记录"串行 for 循环"，但没记录 kill-batch 失败模式：把 3+ 张图的 `python3 generate_image.py` 调用塞进一个 for 循环，外层 shell 进程一旦被 SIGTERM（OOM/user-stop），**所有未完成图片全部丢失**，没有进度残留。**修法**：① 单进程只跑 1 张图（background + notify_on_complete），跑完再起下一张；② 或用 `nohup` + 写日志文件，便于中断后从日志恢复；③ `proc_*` session_id 记录每张图的进度。**反例**：2026-07-06 一次 for 循环跑 3 张图，被 SIGTERM -15 杀进程，3 张图全部未完成。
26. **`execute_code` 沙盒无状态（2026-07-06 实测）** → Pitfall #2 记录了"读不到 env"，但没记录更广的"`execute_code` 每次都是新进程，所有 import 和变量都要重新定义"问题。`from hermes_tools import ...` 这种 import 在同一次 assistant turn 内的多次 execute_code 调用**不会**保留——下次调用必须重 import。**修法**：① 把多步逻辑塞进**一次** execute_code 调用的同一个脚本里跑完；② 跨 turn 持久化用 write_file 落盘；③ 渐进式补丁（step 1 调一次，step 2 再调一次）会反复 NameError。
27. **渠道/CTA 不反映用户当前状态（2026-07-06 用户原话："先不挂闲鱼 先让他们联系我 我明天挂闲鱼"）** → 用户在"挂闲鱼前"的状态下，文章 CTA 不能写"闲鱼 ¥199 一次性"。L5 反虚构第 ③ 条已覆盖但这里再强调：**写 CTA 前用 clarify 确认 3 件事**——(a) 闲鱼是否已挂？没挂→ 写"加微信"；(b) 微信二维码是否就绪？没就绪→ 写微信号文字块；(c) 飞书资料包是否已建？没建→ CTA 链接留空。教训：2026-07-06 跑出文章后用户说"先不挂闲鱼"，已写好的闲鱼 CTA 整段作废要重写。
28. **多步交付中途反复问"完成了吗"=反模式（2026-07-06 用户原话："还没完成吗" / "你直接搞完 然后发给我 别卡了"）** → 跑多步流水线（图→HTML→截图占位→发飞书）时，**不要中途停下来问"现在到了哪一步"**——用户能看文件系统和飞书消息，他/她问你时说明他自己也烦了。**正确动作**：(1) 把每一步的**自检**写进脚本里跑，跑完就过；(2) 中间状态用"已完成 X / 还差 Y"一句话压缩汇报，不展开；(3) 只在**真阻塞**（API 全挂/凭证缺失/请求被拒）时停下来问。**反例**：2026-07-06 我连发 2 次"还没完成吗/继续呀"被问后才发现——所有产物其实在第 1 次就生成完了，只是没自我验证就停了。
29. **占位素材用「用户微信号 + 蓝色边框块」代替二维码（2026-07-06 实测）** → 用户给微信号但没给二维码时，文末 CTA 不要写"扫一扫"，改写：
```html
<span class="wechat-id">微信号：<strong>Yao934025938</strong></span>
```
样式：`display:block; background:#f0f7ff; border:2px solid #2563EB; border-radius:6px; padding:12px 16px; margin:16px 0; color:#2563EB; font-size:17px;` 一眼看到。**触发**：用户说"不留二维码了"+"我的微信号是 XXX"。**反例**：只把微信号当 inline 文字加粗——读者扫不到、记不住、最后就流失。
30. **用户提供的截图截断 → 用 Pillow 从源文字重排合成（2026-07-06 实测）** → 当用户给"风格对比图"但右半部分被截断，**不要**让用户重新截。**正确动作**：用 Pillow `ImageDraw.text()` 把左右两份文字内容按统一版式（顶部黑底标题栏 + 左右栏头 + 底部参数对比条）合成 1 张干净图（典型 1400×1500，250KB 左右）。**优势**：① 排版统一、左右密度对齐；② 截图不全/低分辨率/UI 噪音全消失；③ 输出是设计稿级别，比手机截图更专业。**代码骨架**：
```python
from PIL import Image, ImageDraw, ImageFont
font = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
canvas = Image.new("RGB", (1400, 1500), "#fafafa")
draw = ImageDraw.Draw(canvas)
draw.rectangle([0, 0, 1400, 100], fill="#1f2329")
draw.text((40, 28), "风格学习前后对比", fill="#ffffff", font=ImageFont.truetype(font, 36))
# 左栏 header / 右栏 header / 双栏正文 / 底部参数条
```
**适用场景**：用户截图被截/模糊/包含 UI 噪音的所有"对比图/数据图/教程图"。

31. **用户给的图必须全嵌，不能只挑 1 张（2026-07-06 用户原话："我的几张截图 没有都放进去啊"）** → 收到用户发的 N 张图，**必须**先做 4 步流程（见 `references/user-asset-ingestion.md`）：① vision_analyze 逐张盘点 → ② 3 类分类（当前文核心 / 姊妹篇延伸 / 不可用）→ ③ 输出位置分配表 → ④ 全部嵌入 HTML。**真实素材图不要虚线框**——它是已就位的图。**反例**：用户给了 5 张真实素材图（推草稿日志 / 资料包主图 / 资料包封面 / 飞书聊天 / 交付清单）+ 2 张风格对比图，agent 只用 1 张合成的风格对比图做 Step 3 配图，**剩下 5 张全部没用**。用户质问后才补嵌。**教训**：用户给的图 = 用户认可的资产，**全部嵌**才符合"已交付的真实感"。

详见 `references/live-failures.md`

32. **`push_draft.py` 缺 `import urllib.request`（2026-07-06 实测）** → 脚本顶部 `import` 列表只有 `json, sys, os, re, subprocess`，没 `urllib.request`。后果：推后验真失败时调 `delete_draft()` 抛 `NameError: name 'urllib' is not defined`，**坏草稿留在草稿箱**（没删掉）。修法：脚本 L4 改为 `import json, sys, os, re, subprocess, urllib.request`。

33. **推草稿验真阈值 `chinese > 1000` 误杀（2026-07-06 实测）** → 阈值 1000 偏严。`verify_draft` 拉回的 content 含 `<strong>` `<code>` 等 HTML 标签，正则 `[\u4e00-\u9fff]` 不会算标签属性里的中文，导致推后实际 5 张图 + 1828 字正文 → content 算下来只有 982 < 1000，触发删草稿逻辑。**修法**：阈值改为 `chinese > 800`（保留 200 字安全垫，不漏检真实损坏）。

34. **PNG base64 接近 2MB 限制（2026-07-06 实测）** → 5 张 1792x1024 PNG base64 内嵌 = ~8MB（HTML 体积），但推草稿时**公众号 content 字段限制 ~2MB**（不是 HTML 体积），即使 base64 替换成 CDN URL 后，content 长度仍可能接近 2MB。Pitfall #3 已提 `compress_images.py`，但**新规则**：推草稿版 HTML 必须用相对路径（不嵌 base64），且所有图预先跑 `compress_images.py` 转 JPG q80（每张 1.2MB → 200KB）。

35. **微信草稿箱 `/cgi-bin/draft/get` 不带 media_id 拉列表返回空数组（2026-07-06 实测）** → 想列出现有草稿时，**必须**逐个传 `media_id` 才能拉到；不带参时返回 `{"news_item": []}` 让你误以为草稿箱是空的。**修法**：要"清重复草稿"时，从最近推送日志里抄 media_id 逐个 `draft/get` 验真，存在就 `draft/delete`。或者直接用 `draft/count`（如果有）拿总数。

36. **视觉 QA 用 vision_analyze 看到 emoji 渲染成方框（误以为 bug）** → vision 工具看 `<div class="sshot-tag">📸 待补充：...</div>` 时，emoji `📸` 有时渲染成"⊠"或方框——**这是 fontconfig 问题，不是 HTML bug**。在浏览器里 emoji 正常显示。判断标准：看 vision 报告里 "栏头图标问题" 时，**先用浏览器/移动端打开 HTML 验证**再决定是否修。

37. **CTAs 顺序"先不挂闲鱼→加微信→闲鱼挂"必须反映在所有产物（2026-07-06 用户原话：\"先不挂闲鱼 先让他们联系我 我明天挂闲鱼\"）** → Pitfall #27 已记录，但这里强化：CTA 改动必须**同步**到 (a) article.md、(b) 两个 HTML、(c) 飞书资料包。漏一个就是版本不一致。**修法**：CTA 变更时把产物清单打出来逐个确认。

38. **多步交付完成度 = 自我验证 + 单条汇报（2026-07-06 用户原话两次"还没完成吗"/"你直接搞完"）** → Pitfall #28 已记录。补充：**跑完每步立刻 self-verify**（文件存在 / size / content 关键字），把"已生成 v6 HTML 1.39MB / 6 图 4 截图占位 / 推草稿成功 media_id=..."压缩成 3 行汇报。**反模式**：跑完一步停下来等用户问，被问才汇报——每个停顿都让用户怀疑"卡住了"。



每次正式交付必须输出：

| 项 | 结果 |
|---|---|
| skill | ai-gzh-platform |
| config | configured / blocked |
| article workflow | 13步已执行 / 哪步阻塞 |
| image model | 实际 model |
| image endpoint | 已实测 2xx / 阻塞 |
| image files | cover + n 张正文图 |
| visual QA | 通过 / 哪张失败 |
| article QA | L1-L4 通过 / 哪层失败 |
| title bytes | x / 30 |
| digest bytes | x / 54 |
| HTML | 微信粘贴版 + 推草稿版 / 阻塞 |
| optional publish | 飞书/公众号草稿是否执行 |
