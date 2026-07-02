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

## 配置说明

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `brand_name` | 品牌名 | 大姚AI提效 |
| `content_directions` | 内容方向关键词 | ["AI提效", "职场成长"] |
| `target_audience` | 目标用户画像P1/P2/P3 | 见config.example.json |
| `html_template.style_name` | 排版风格10选1 | 科技蓝 |
| `image_style.name` | 配图风格6选1 | xiaoyao-illustrations |
| `image_api.endpoint` | GPT Image 2 API地址 | https://api.openai.com/v1/images/generations |

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

经典青蓝 · 科技蓝 · 商务紫 · 温暖橙 · 薄荷绿 · 玫瑰红 · 深夜蓝 · 极简灰 · 森林绿 · 奶茶棕

## 配图风格（6选1）

| 风格 | 说明 |
|------|------|
| baoyu-notion | Notion知识卡风格（默认），封面+2张信息图 |
| xiaoyao-illustrations | 小姚手绘风格，封面+3-5张正文配图 |
| hand-drawn | 手绘风格 |
| minimal-flat | 极简扁平风格 |
| isometric-3d | 等距3D风格 |
| custom | 自定义prompt前缀 |

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
