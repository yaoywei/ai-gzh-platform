# AI公众号内容平台

> 一键安装的公众号内容生产系统。从选题到交付全自动闭环，兼容 Coze / Hermes / OpenClaw / 任意 Agent 平台。

## 这是什么

一套完整的AI公众号内容生产SOP，打包成可复用技能。装上就能用，不依赖特定平台。

**生产流程**：选题调研 → 爆款分析 → 内容撰写 → 四层自检 → 配图生成 → HTML排版 → 推草稿 → 交付

## 功能一览

| 模块 | 能力 |
|------|------|
| 选题系统 | 配比轮转 + 爆款调研 + 五维评分 + 选题防撞 |
| 写作引擎 | khazix-writer风格（口语化、断裂段、无小标题） |
| 质检系统 | 四层自检：硬规则→风格→内容→活人感 |
| 配图生成 | 6种风格：baoyu-notion / xiaoyao-illustrations(小姚手绘) / hand-drawn / minimal-flat / isometric-3d / custom |
| HTML排版 | 10种配色方案，微信兼容全内联样式 |
| 推草稿 | 通过代理服务器自动推到公众号草稿箱（可选） |
| 飞书资料包 | 自动创建飞书文档作为CTA钩子（可选） |

## 小姚手绘IP

内置原创IP角色「小姚」——年轻男性产品架构师，穿橙色卫衣+黑框方眼镜+炸毛短发，暖橙#F97316品牌色。

包含完整的IP定义、风格DNA、构图模式、prompt模板和5张校准样图。

## 安装方式

### 方式一：Coze 技能商店

在扣子商店搜索「AI公众号内容平台」安装。

### 方式二：手动安装（任意平台）

1. 下载或 clone 本仓库
2. 将文件放到 Agent 的 skills 目录下：

```
skills/ai-gzh-platform/
├── SKILL.md
├── config.example.json
├── references/
│   ├── writing-style.md
│   ├── visual-templates.md
│   ├── xiaoyao-ip.md
│   ├── style-dna.md
│   ├── prompt-template.md
│   ├── composition-patterns.md
│   ├── qa-checklist.md
│   └── system-prompt.md
├── scripts/
│   ├── generate_image.py
│   ├── push_draft.py
│   └── wx-proxy.js
└── assets/examples/    ← 5张小姚校准样图
```

3. 复制 `config.example.json` 为 `config.json`，填写你的配置
4. 注入环境变量（见下方配置说明）

也可以直接运行首次配置向导：

```bash
python scripts/init_config.py
```

向导会要求选择排版风格、配图风格和可选能力，并生成本地 `config.json`。

## 配置说明

第一次使用不要直接编辑到能跑为止，先完成一次"选择向导"。

### 首次使用选择向导

复制模板：

```bash
cp config.example.json config.json
```

如果 `setup_status` 仍是 `needs_user_choice`，先回答下面三组问题：

1. 公众号/品牌名 + 2-4个内容方向
2. P1/P2/P3 读者画像
3. 排版风格 + 配图风格

不确定时推荐：`tech-blue` + `baoyu-notion`。如果要做系列个人IP，再选 `xiaoyao-illustrations`。

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `brand_name` | 品牌名 | 大姚AI提效 |
| `content_directions` | 内容方向关键词 | ["AI提效", "职场成长"] |
| `target_audience` | 目标用户画像P1/P2/P3 | 见config.example.json |
| `html_template.style_name` | 排版风格id，见下方10选1 | tech-blue |
| `image_style.name` | 配图风格id，见下方6选1 | baoyu-notion |
| `image_api.enabled` | 是否启用图片生成；默认false | false |

图片、飞书、公众号推草稿都默认关闭。只有 API/凭证实测通过后，才把对应 `enabled` 改成 `true`。

### 环境变量

| 变量名 | 说明 | 必须 |
|--------|------|------|
| `GPT_IMAGE2_API_KEY` | GPT Image 2 API Key | ✅ |
| `WX_PROXY_SERVER` | 微信代理服务器IP（推草稿用） | 推草稿时 |
| `WX_PROXY_TOKEN` | 代理鉴权Token | 推草稿时 |
| `WX_APPID` | 微信AppID | 推草稿时 |
| `WX_APPSECRET` | 微信AppSecret | 推草稿时 |
| `FEISHU_APP_ID` | 飞书App ID | 飞书资料包时 |
| `FEISHU_APP_SECRET` | 飞书App Secret | 飞书资料包时 |

### 各平台环境变量注入方式

| 平台 | 方式 |
|------|------|
| Coze | skill凭证系统自动注入 |
| Hermes | secrets 配置面板 |
| OpenClaw | .env 文件 |
| 其他 | 系统环境变量 |

## HTML排版风格（10选1）

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

## 配图风格（6选1）

| 风格 | 说明 |
|------|------|
| `baoyu-notion` | Notion知识卡风格，稳妥通用，封面+2张信息图 |
| `xiaoyao-illustrations` | 小姚手绘风格，适合原创IP系列，封面+3-5张正文配图 |
| `hand-drawn` | 手绘风格，适合轻松陪伴型内容 |
| `minimal-flat` | 极简扁平风格，适合SaaS、流程图、工具教程 |
| `isometric-3d` | 等距3D风格，适合系统架构、自动化平台展示 |
| `custom` | 自定义prompt前缀，需要填写 `image_style.style_prompt_prefix` |

## 脚本说明

### generate_image.py

调用 GPT Image 2 API 生成图片，双环境兼容。

```bash
python scripts/generate_image.py --prompt "你的prompt" --size "1792x768" --output "imgs/cover.png"
```

### push_draft.py

通过代理服务器自动推草稿到微信公众号。

```bash
python scripts/push_draft.py --title "标题" --html "article.html" --cover "cover.jpg" --images img1.jpg img2.jpg
```

### wx-proxy.js

微信API代理服务器，部署在你的服务器上，避免暴露AppSecret。

```bash
node wx-proxy.js
```

## 依赖

- Python 3.8+
- requests（`pip install requests`，Coze环境已预装）
- Node.js（仅wx-proxy.js需要）

## 合规红线

- 禁止无数据来源的百分比
- 禁止极限词（最好/第一/唯一等）
- CTA禁止诱导关注
- 发布前必须确认

## License

MIT
