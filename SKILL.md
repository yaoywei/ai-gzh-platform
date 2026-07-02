---
name: ai-gzh-platform
description: AI公众号内容生产全平台技能。一键安装完整的公众号内容生产系统，包含选题调研、爆款分析、内容撰写(khazix-writer风格)、四层自检、配图生成(GPT Image 2，支持6种风格含小姚手绘)、HTML排版、推草稿到公众号、飞书资料包创建。当用户说安装公众号平台、搭建公众号系统、装公众号技能、配置AI公众号内容平台、写公众号文章、按SOP写内容、生产今天的公众号内容、走内容流程、写篇推文时触发。
---

# AI公众号内容平台

> 一键安装 → 自动生产，从选题到交付的公众号内容全闭环系统。兼容 Coze / Hermes / OpenClaw / 任意 Agent 平台。

## 零依赖说明

- 脚本使用双环境兼容：`try: from coze_workload_identity import requests` → `except: import requests`
- API Key 通过环境变量注入，不硬编码，不绑定特定平台
- 配置全外置到 `config.json`，首次使用时填写

## 首次安装

首次使用时，优先运行：`python scripts/init_config.py`。如果不能运行脚本，则手动按以下步骤完成配置。**遇到 🛑 标记的步骤，暂停向用户收集信息后再继续。**

### 🛑 第0步：首次使用必须完成风格选择

如果 `config.json` 不存在，或 `config.json.setup_status == "needs_user_choice"`，**禁止直接生成文章**。先向用户收集配置，尤其是排版风格和配图风格。

**一次最多问3个问题**。优先问这3个：

1. **品牌和方向**：公众号/品牌名是什么？主要写哪2-4个方向？
2. **读者画像**：主要写给谁？如果不确定，给 P1/P2/P3 三档粗画像即可。
3. **样式选择**：排版风格选哪一个？配图风格选哪一个？

如果用户说"你帮我选 / 按画像配 / 默认推荐"，使用：

- `html_template.style_name = "tech-blue"`（科技蓝）：适合 AI、SaaS、企业服务、技术产品
- `image_style.name = "baoyu-notion"`：稳妥通用，封面 + 信息图

如果用户明确要个人IP/系列角色，再选：

- `image_style.name = "xiaoyao-illustrations"`（小姚手绘）

#### 排版风格（10选1）

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

#### 配图风格（6选1）

| id | 中文名 | 适合 |
|---|---|---|
| `baoyu-notion` | Notion知识卡 | 稳妥通用；封面 + 2张信息图 |
| `xiaoyao-illustrations` | 小姚手绘 | 原创IP人格化；封面 + 3-5张正文配图 |
| `hand-drawn` | 手绘风格 | 轻松、陪伴感、低压教程 |
| `minimal-flat` | 极简扁平 | SaaS、流程图、工具教程 |
| `isometric-3d` | 等距3D | 系统架构、自动化平台、科技感展示 |
| `custom` | 自定义prompt | 已有品牌视觉规范，需要填写 `style_prompt_prefix` |

**必需配置：**
1. **品牌名称 (`brand_name`)**：公众号名称/品牌名，如「大姚AI提效」
2. **内容方向 (`content_directions`)**：2-4个方向关键词，如 `["AI提效", "职场成长"]`
3. **目标受众 (`target_audience`)**：P1/P2/P3三档画像描述
4. **HTML排版风格 (`html_template.style_name`)**：上表10选1
5. **配图风格 (`image_style.name`)**：上表6选1
6. **图片生成能力 (`image_api.enabled`)**：是否启用；启用才需要 endpoint + API Key

**可选配置（不需要则跳过后续相关步骤）：**
7. 微信公众号推草稿 → 需提供AppID + AppSecret + 服务器IP
8. 飞书资料包 → 需提供 App ID + App Secret

#### 第0.5步：从用户画像补齐配置（"知道的就别问了"模式）

用户说"按我画像配 / 你直接选 / 不知道的再问我"时，走这套：

1. **读画像档**：`~/.hermes/USER.md` + 当前会话的 USER PROFILE 注入 + `AGENTS.md` 中的命名约定（如 "大姚=AI 名"）
2. **diff** 上述画像 vs `config.example.json` 已有的字段，能直接复用的就复用：`target_audience`（P1/P2/P3）、`brand_name`、`content_directions`、配色方案常常已经在 example 里
3. **填入 config.json**，每填一项写一行 `"picked": "<依据>"` 注释，方便用户回查
4. **只问真正缺的**：通常是"我猜不到的偏好"（如 html_template 风格 10 选 1 的选择）、未知的 API Key、未部署的可选能力
5. **给一个汇总表**：列出我替你选了哪些 + 选了什么的依据 + 还缺什么（按"必填 / 可选"分组）

**禁忌**：
- ❌ 把"我不知道"伪装成"我替你选了默认"——不确定的就明说"待核验"
- ❌ 把"我替你选"包装成"agent 智能判断"——直接说"这是 example.json 的默认值 / 这是你 USER.md 写的"
- ❌ 一次问超过 3 个问题——能填的先填，剩下的批量问

### 第0.8步：启用前必须实测（verify-before-enable）

填完 config.json 后，**不要立刻把 `image_api.enabled` / `feishu.enabled` / `wechat_proxy.enabled` 设成 `true`**。先做最小验证：

| 字段 | 验证方法 | 通过标准 |
|------|----------|----------|
| `image_api` | POST `{endpoint}` + `Authorization: Bearer ${KEY_ENV}` + 1 token 提示词 | HTTP 2xx + 返回 url 或 b64_json |
| `feishu` | POST `https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal` + app_id/secret | `code: 0` + token 长度 > 30 |
| `wechat_proxy` | GET `{server_ip}:{port}/health` | 200 OK |

**401 的典型原因**（按概率排序）：
1. `.env` 里的 Key 属于**另一个第三方平台**（zhongzhuan 的 Key 拿去调 sharehub，反之亦然）——常见陷阱是 `OPENAI_API_KEY` 这个名字看似通用，实际是某个特定平台的
2. Key 过期或被撤销
3. endpoint 路径错了（漏 `/v1`、多加 `/v1`）
4. 模型名不在该平台支持列表里

**验证失败时**：把 `enabled` 改回 `false`，告知用户哪个 Key 不匹配，并提示"如果图 API 有独立 Key，请提供；或保持 disabled 先跑文字链路"。

**详见**：`references/setup-walkthrough.md`（一个完整的"填 config → 注入 env → 验证 → 启用"工作流示例，含实测陷阱和回复模板）

### 第1步：创建config.json

将 `config.example.json` 复制为 `config.json`，再按第0步的选择填入用户配置。关键字段：

- `setup_status`：配置完成后改为 `configured`；未配置时保持 `needs_user_choice`
- `brand_name`：用户品牌名
- `content_directions`：用户方向关键词数组
- `target_audience.P1/P2/P3`：用户画像描述
- `html_template.style_name`：用户选择的排版风格 id
- `html_template.primary_color/accent_color/background_color`：从所选排版风格复制
- `image_style.name`：用户选择的配图风格 id
- `image_style.style_prompt_prefix`：仅 `custom` 风格必填
- `image_api.enabled`：默认 `false`；只有实测通过后才改 `true`
- `wechat_proxy.enabled`：默认 `false`；只有实测通过后才改 `true`
- `feishu.enabled`：默认 `false`；只有实测通过后才改 `true`

**公开仓库只提交 `config.example.json`，不要提交真实 `config.json`。**

### 第2步：注入环境变量

根据用户使用的平台，用对应方式注入环境变量：

| 平台 | 注入方式 |
|------|----------|
| Coze | skill凭证系统自动注入 |
| Hermes | secrets 配置面板 |
| OpenClaw | .env 文件 |
| 其他 | 系统环境变量 |

必须注入的环境变量（根据config.json中`key_env`字段对应）：
- `GPT_IMAGE2_API_KEY`：GPT Image 2 的 API Key
- `WX_PROXY_SERVER` / `WX_PROXY_TOKEN` / `WX_APPID` / `WX_APPSECRET`（如需推草稿）
- `FEISHU_APP_ID` / `FEISHU_APP_SECRET`（如需飞书资料包）

### 第3步：确认文件完整

检查以下目录和文件是否存在：

```
skills/ai-gzh-platform/
├── SKILL.md                    ← 本文件
├── config.example.json         ← 配置模板
├── references/
│   ├── writing-style.md        ← khazix-writer写作风格
│   ├── visual-templates.md     ← 配图视觉模板(6种风格)
│   ├── xiaoyao-ip.md           ← 小姚IP定义
│   ├── style-dna.md            ← 小姚风格DNA
│   ├── prompt-template.md      ← 小姚prompt模板
│   ├── composition-patterns.md ← 小姚构图模式
│   ├── qa-checklist.md         ← 配图QA检查清单
│   ├── system-prompt.md        ← Agent System Prompt参考
│   └── push-draft-pitfalls.md  ← 推草稿踩坑记录（45002/45003/45004/40007 等错误码）
├── scripts/
│   ├── init_config.py          ← 首次配置向导（选择排版/配图/可选能力）
│   ├── generate_image.py       ← GPT Image 2生成脚本
│   ├── push_draft.py           ← 微信推草稿脚本
│   ├── wx-proxy.js             ← 微信代理服务器
│   └── compress_images.py      ← PNG→JPG 压缩（避免 45002 content size out of limit）
└── assets/examples/            ← 小姚风格校准样图(5张)
```

---

## 生产流程（13步）

配置完成后，每次生产文章按以下流程执行。核心原则：**全自动执行，异常才上报，主人只看结果。**

### Step 1：配比轮转判断

每3篇为一轮，按 `content_ratio` 轮转（默认60%-60%-30%）。读取 `config.json` 中 `round_state`，判断当前该写哪类内容，轮转后更新 `round_state`。

- **引流文(60%)**：生存级痛点场景，开头直接进场景，落脚读者焦虑
- **专业文(30%)**：改善级工具教程，观察+现象+反差开头，落脚具体方法
- **转化文(10%)**：关系级产品露出，学员故事开头，落脚产品价值

### Step 2：爆款调研（必做）

标题占爆款70%比重，写作前必做调研。

1. 从 `config.json` 的 `content_directions` 提取2-3组关键词，限定最近7天
2. 策略：先搜1个泛词看大盘 → 再搜2-3个精准词找细分赛道
3. 筛选低粉爆款：阅读量明显高于日常、非头部大号、近7天发布
4. 记录3-5条爆款标题，提取关键词和结构
5. 跨关键词对比：爆款密度最高 → 优先选

**选题防撞**：调研前扫 `covered_topics`，重叠则换方向。

### Step 3：选题评分

五维评分（5分制）：生存焦虑(30%) + 需求具体(20%) + 可复制(25%) + 画像匹配(15%) + 数据支撑(10%)

决策：≥4.0直接写，3.5-3.9写但排后，<3.5淘汰。

### Step 4：文章原型判断

判断属于哪种原型，每种写法重心不同：

| 原型 | 写法重心 |
|------|----------|
| 调查实验型 | 过程叙事+发现层层递进 |
| 产品体验型 | 场景演示+真实感受 |
| 现象解读型 | 观察→好奇→研究→升维 |
| 工具分享型 | 个人故事铺垫→工具展示→效果惊艳 |
| 方法论分享型 | 每节有可执行行动+坦诚学习曲线 |

### Step 5：内容撰写

按 `references/writing-style.md` 中的khazix-writer风格撰写，约1200字。

**写作硬规则**：
- 禁止小标题（非分条目结构）、禁止冒号、禁止破折号、禁止双引号（用「」）、禁止emoji
- 口语化转场句衔接板块
- CTA公式：转发+给谁+社交价值+资料包钩子+选择题互动

### Step 6：四层自检（必做）

写完正文后必须跑四层自检，不通过则修改后重检。详见 `references/writing-style.md`。

| 层级 | 通过标准 |
|------|----------|
| L1 硬性规则 | 禁用词+禁用标点零命中 |
| L2 风格一致性 | 口语化≥5个词组、开头节奏达标 |
| L3 内容质量 | 观点有支撑、非教科书式科普 |
| L4 活人感 | 整体像真人写的 |

### Step 7：标题打磨

标题优先级：爆款调研结果 > 标题公式 > 通用判断

标题公式：[主体] + [场景/数字] + [解决什么问题]

**硬约束**：`title ≤ 30 字节`（中文 UTF-8 = 3 字节/字符，10 个汉字内）。超了会被微信公众号草稿 API 拒（errcode 45003），不是"字符数"是"字节数"。详细见 `references/push-draft-pitfalls.md`。

### Step 8：落脚点检查

读者拿走能直接用的是什么？必须明确。步骤+截图、提示词模板、可抄作业方案 ✅ | 纯功能介绍 ❌

### Step 9：配图生成

读取 `config.json` 中 `image_style`，按对应风格生成。详见 `references/visual-templates.md`。

**baoyu-notion（默认）**：封面(1792×768) + 2张信息图(1024×1820)

**xiaoyao-illustrations（小姚手绘）**：
- 先读取 `references/xiaoyao-ip.md`、`references/style-dna.md`、`references/prompt-template.md`、`references/composition-patterns.md`
- 封面(1792×768) + 3-5张正文配图(1792×1024)
- 参照 `assets/examples/` 下的校准样图

生成脚本：`python scripts/generate_image.py --prompt "..." --size "1792x768" --output "imgs/cover.png"`

### Step 10：HTML转换

将正文+配图转为微信兼容HTML，全内联样式。读取 `config.json` 中 `html_template` 的配色方案。

输出：`[主题]-微信粘贴版-v1.html`
使用：Chrome打开 → Cmd+A全选 → Cmd+C复制 → 公众号后台Cmd+V粘贴

### Step 11：资料包创建（可选）

如 `feishu.enabled=true`，创建飞书资料包：确定CTA关键词 → 整理资料模板 → 创建飞书文档 → **保存 doc_id**（后续 HTML CTA 区需要嵌入 `https://feishu.cn/docx/{doc_id}`）。

**顺序约束**：飞书 doc 必须在 HTML 生成之前创建（因为 HTML CTA 链接要嵌入 doc_id）。

**⚠️ 关键步骤：飞书 doc 必须分两步写入**

1. `POST /open-apis/docx/v1/documents` 传 `title` → 返回 `document_id`（**只创建空文档，正文为空**）
2. `POST /open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children` 写入 blocks 数组
3. 单次 children 数组**最多 50 个 block**，超过要分批（按 30/batch 安全）
4. 验证：`GET /docx/v1/documents/{document_id}/raw_content` → content 长度 > 500

block_type 速查：`2`=text, `3`=heading1, `4`=heading2, `12`=bullet, `22`=divider

详见 `references/push-draft-pitfalls.md` 坑 5-6。

### Step 12：推草稿到公众号（可选）

如 `wechat_proxy.enabled=true`，通过代理自动推草稿。运行 `python scripts/push_draft.py`。如代理不通，提示用户手动操作。

**推草稿前必跑 3 步预处理**（不跑必踩坑，详见 `references/push-draft-pitfalls.md`）：

1. **压缩配图**：`python scripts/compress_images.py output/<date>-*/`（PNG → JPG q80，3MB → 300KB）
2. **HTML 不嵌 cover**（封面走 thumb_media_id，HTML 里嵌入会触发 45002 content size out of limit）
3. **校验字节数**：`title ≤ 30 字节`、`digest ≤ 54 字节`（中文 UTF-8 = 3 字节/字符，不是字符数！）

**常见错误码速查**：
- `40007` invalid media_id → 缺 thumb_media_id
- `45002` content size out of limit → HTML > 2MB，跑 `compress_images.py` 或移除 cover
- `45003` title size out of limit → title > 30 字节
- `45004` description size out of limit → digest > 54 字节

**⚠️ 中文乱码陷阱（最严重）**：草稿箱显示 `\u6211\u505a` 等转义字符而不是中文 → 根因是 `push_draft.py` L27 的 `json=data` 触发了 `ensure_ascii=True`。**已修复**：改用 `data=json.dumps(data, ensure_ascii=False).encode("utf-8")`。**每次推完必跑验证脚本**（见 `references/push-draft-pitfalls.md` 坑 1）：拉 draft 内容，确认中文字符数 > 1000 且 `\u` 出现次数 = 0。

### Step 13：交付通知

推送全部产出物：文章正文(.md) + HTML排版版(.html) + 配图 + 资料包链接 + CTA关键词。

## 合规红线

- 禁止无数据来源的百分比
- 禁止极限词（最好/第一/唯一等）
- CTA禁止诱导关注（"关注后领取"❌，"回复XX获取"✅）
- **发布前必须经主人确认**

## 判断库速查

**选题有效**：场景+AI解决 ✅ | 纯工具推荐 ❌
**标题有效**：场景+数字+方法 ✅ | AI的N个技巧 ❌
**落脚点有效**：步骤+截图 ✅ | 纯功能介绍 ❌
