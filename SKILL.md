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

首次使用时，按以下步骤完成配置。**遇到 🛑 标记的步骤，暂停向用户收集信息后再继续。**

### 🛑 第0步：收集用户配置

安装前先向用户逐项收集以下配置：

**必需配置：**
1. **品牌名称 (brand_name)**：公众号名称/品牌名，如「大姚AI提效」
2. **内容方向 (content_directions)**：2-4个方向关键词，如 ["AI提效", "职场成长"]
3. **目标受众 (target_audience)**：P1/P2/P3三档画像描述
4. **HTML排版风格**：10选1 → 经典青蓝、科技蓝、商务紫、温暖橙、薄荷绿、玫瑰红、深夜蓝、极简灰、森林绿、奶茶棕
5. **配图风格**：6选1 → baoyu-notion(默认)、xiaoyao-illustrations(小姚手绘)、hand-drawn、minimal-flat、isometric-3d、custom(自定义prompt)
6. **图片生成API**：GPT Image 2的endpoint地址 + API Key

**可选配置（不需要则跳过后续相关步骤）：**
7. 微信公众号推草稿 → 需提供AppID + AppSecret + 服务器IP
8. 飞书资料包 → 需提供App ID + App Secret

### 第1步：创建config.json

将 `config.example.json` 复制为 `config.json`，填入用户提供的配置。关键字段：

- `brand_name`：用户品牌名
- `content_directions`：用户方向关键词数组
- `target_audience.P1/P2/P3`：用户画像描述
- `image_api`：GPT Image 2 API地址和Key环境变量名
- `html_template.style_name`：用户选择的排版风格
- `image_style.name`：用户选择的配图风格
- `wechat_proxy.enabled`：是否启用推草稿
- `feishu.enabled`：是否启用飞书资料包

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
│   └── system-prompt.md        ← Agent System Prompt参考
├── scripts/
│   ├── generate_image.py       ← GPT Image 2生成脚本
│   ├── push_draft.py           ← 微信推草稿脚本
│   └── wx-proxy.js             ← 微信代理服务器
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

如 `feishu.enabled=true`，创建飞书资料包：确定CTA关键词 → 整理资料模板 → 创建飞书文档 → 更新HTML的CTA链接。

### Step 12：推草稿到公众号（可选）

如 `wechat_proxy.enabled=true`，通过代理自动推草稿。运行 `python scripts/push_draft.py`。如代理不通，提示用户手动操作。

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
