# AI公众号内容平台

> 从选题到交付的公众号内容全闭环系统。兼容 Coze / Hermes / OpenClaw / 任意 Agent 平台。

## 这是什么

一套完整的 AI 公众号内容生产 Skill，装上就能用。不依赖特定平台。

**13 步生产流程**：配比轮转 → 爆款调研 → 选题评分 → 文章原型 → 内容撰写 → 四层自检 → 标题校验 → 落脚点检查 → 配图生成 → HTML 排版 → 飞书资料包 → 推草稿 → 交付

## 功能一览

| 模块 | 能力 |
|------|------|
| 选题系统 | 配比轮转 + 爆款调研 + 五维/七维评分 + 选题防撞 |
| 写作引擎 | 两种风格：khazix-writer（口语化、断裂段）/ n8n-wechat-full-prompt（B端爆文、Writer+Cleaner 两段式） |
| 质检系统 | 四层自检：硬规则→风格→内容→活人感 |
| 配图生成 | 6+1 种风格：baoyu-notion / xiaoyao-illustrations / hand-drawn / minimal-flat / isometric-3d / custom / **custom-ip（自定义IP形象）** |
| HTML排版 | 10 种配色方案，微信兼容全内联样式 |
| 推草稿 | 通过 wx-proxy 代理自动推到公众号草稿箱，**含推后验证+自动诊断**（可选） |
| 飞书资料包 | 自动创建飞书文档作为 CTA 钩子（可选） |
| 自定义IP | 引导用户定义自己的 IP 角色，生成专属配图（可选） |

## 快速开始（3 分钟）

### 1. Clone 到你的 Agent skills 目录

```bash
cd ~/.hermes/skills/   # 或你 Agent 的 skills 目录
git clone https://github.com/yaoywei/ai-gzh-platform.git
```

### 2. 首次使用引导

装好后对你的 Agent 说：

```
帮我用 ai-gzh-platform 写一篇公众号文章
```

Agent 会自动检测到 `config.json` 不存在，启动 **Phase 0 引导流程**：

1. **自动读取**你的用户画像、环境变量、已有配置
2. **自动填充**能确定的字段（品牌名、内容方向、读者画像）
3. **交互引导**（clarify）问你 2-3 个问题：排版风格、配图风格、API 模块
4. **实测验证**每个 API 端点，不通的不开
5. **交付汇总表**告诉你"我替你选了什么 + 依据 + 立即可用范围"

整个过程不超过 3 分钟，不用手动编辑任何配置文件。

### 3. 开始生产

引导完成后，直接对 Agent 说：

```
用 ai-gzh-platform 生产今天的公众号内容
```

Agent 会按 13 步 SOP 自动执行，中间产物（article.md、HTML、配图、qa-report）存到 `output/{date}-{slug}/` 目录。

## 推草稿到公众号（可选，需额外配置）

推草稿需要一个 **wx-proxy 代理服务器**。原因：

1. **安全**：AppSecret 只存在服务器端，不暴露在客户端代码
2. **绕过 Bug**：微信 `/cgi-bin/draft/add` 端点对非代理 IP 有双重 UTF-8 编码 bug，只有通过代理才能避免
3. **稳定 IP**：代理服务器 IP 固定，只需白名单一次

### 部署步骤

**前提**：你需要一台有公网 IP 的 Linux 服务器（云服务器即可），且该 IP 已加入公众号 IP 白名单。

#### Step 1：在服务器上部署 wx-proxy

```bash
# SSH 到你的服务器
ssh user@your-server-ip

# 一键部署（自动安装 Node.js、生成 Token、配置 systemd）
curl -fsSL https://raw.githubusercontent.com/yaoywei/ai-gzh-platform/main/scripts/wx-proxy-deploy.sh | sudo bash
```

部署完成后会输出 3 个值：

```
PUBLIC_IP:  1.2.3.4
PORT:       8787
TOKEN:      xxxxxxxxxxxxxxxxxx
```

记下这 3 个值。

#### Step 2：在公众号后台添加 IP 白名单

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 左侧菜单 → 设置与开发 → 基本配置
3. IP 白名单 → 添加 Step 1 输出的 `PUBLIC_IP`

#### Step 3：配置环境变量

在你 Agent 运行的机器上，把以下变量加入 `~/.hermes/.env`（或其他平台的环境变量）：

```bash
# 公众号凭据
WX_APPID=你的AppID
WX_APPSECRET=你的AppSecret

# wx-proxy 连接信息（Step 1 输出的值）
WX_PROXY_SERVER=1.2.3.4
WX_PROXY_PORT=8787
WX_PROXY_TOKEN=xxxxxxxxxxxxxxxx
```

#### Step 4：验证连通性

```bash
# 在 Agent 机器上执行
curl -sS "http://1.2.3.4:8787/cgi-bin/token?grant_type=client_credential&appid=你的AppID&secret=你的AppSecret" \
  -H "X-Publish-Token: xxxxxxxxxxxxxxxxxx"
```

返回 `{"access_token":"...","expires_in":7200}` 即为成功。

#### Step 5：启用推草稿

在首次引导时选择"全部启用"，或手动编辑 `config.json`：

```json
{
  "wechat_proxy": {
    "enabled": true
  }
}
```

### 推草稿流程（自动）

启用后，Agent 执行 Step 12 时自动：

1. `compress_images.py` → PNG 转 JPG（控制在 2MB 以内）
2. `check_title_digest.py` → 标题≤30B / 摘要≤54B
3. `push_draft.py` → 上传图片 → 替换 HTML → 创建草稿 → **自动验证**
4. 验证内容：中文字符>1000、无 `\uXXXX` 乱码、无 `æè` 乱码、图片 URL 正常
5. 验证失败 → 自动删除坏草稿 → 诊断 Bug#1（ensure_ascii）或 Bug#2（双重UTF-8）

## 自定义 IP 形象（可选）

如果你想要自己的配图角色（像小姚一样），在首次引导时选 `custom-ip` 配图风格。

Agent 会引导你走 5 步：

1. **拆结构**：Agent 读小姚 IP 体系，理解结构
2. **定义 IP**：5 个问题（性别职业 / 外形识别点 / 主色调 / 性格 / 道具）
3. **写 prompt**：自动生成英文外形描述 + 中文标签的 prompt 模板
4. **改构图**：按职业生成动作池和构图模式
5. **校准样图**：用 image API 生成 5-8 张样图存到 `assets/examples/`

完成后你的配图会稳定生成带有你 IP 形象的正文配图。

## 配置参考

### 环境变量

| 变量名 | 说明 | 何时需要 |
|--------|------|----------|
| `GPT_IMAGE2_API_KEY` | GPT Image 2 API Key | 配图生成 |
| `WX_APPID` | 微信 AppID | 推草稿 |
| `WX_APPSECRET` | 微信 AppSecret | 推草稿 |
| `WX_PROXY_SERVER` | wx-proxy 服务器 IP | 推草稿 |
| `WX_PROXY_PORT` | wx-proxy 端口（默认 8787） | 推草稿 |
| `WX_PROXY_TOKEN` | wx-proxy 鉴权 Token | 推草稿 |
| `FEISHU_APP_ID` | 飞书 App ID | 飞书资料包 |
| `FEISHU_APP_SECRET` | 飞书 App Secret | 飞书资料包 |

### HTML 排版风格（10选1）

| id | 中文名 | 适合 |
|---|---|---|
| `classic-blue` | 经典青蓝 | 通用干货、教程、知识卡片 |
| `tech-blue` | 科技蓝 | AI、SaaS、企业服务（推荐） |
| `business-purple` | 商务紫 | 咨询、管理、B端解决方案 |
| `warm-orange` | 温暖橙 | 个人IP、成长、陪伴型内容 |
| `mint-green` | 薄荷绿 | 效率工具、轻教程 |
| `rose-red` | 玫瑰红 | 女性成长、消费、情绪价值 |
| `midnight-blue` | 深夜蓝 | 深度分析、趋势判断 |
| `minimal-gray` | 极简灰 | 严肃评论、方法论 |
| `forest-green` | 森林绿 | 长期主义、组织管理 |
| `milk-tea` | 奶茶棕 | 生活方式、副业 |

### 配图风格（7选1）

| id | 说明 |
|---|---|
| `baoyu-notion` | Notion知识卡，稳妥通用（推荐） |
| `xiaoyao-illustrations` | 小姚手绘IP，适合原创IP系列 |
| `hand-drawn` | 手绘风格，轻松陪伴感 |
| `minimal-flat` | 极简扁平，SaaS/流程图 |
| `isometric-3d` | 等距3D，系统架构展示 |
| `custom` | 自定义 prompt 前缀 |
| `custom-ip` | 引导定义你自己的 IP 角色 |

## 文件结构

```
ai-gzh-platform/
├── SKILL.md                        ← Skill 主文件（路由索引 + 13步 workflow）
├── README.md                       ← 本文件
├── config.example.json             ← 配置模板
├── references/
│   ├── writing-style.md            ← khazix-writer 写作风格
│   ├── n8n-wechat-full-prompt.md   ← n8n 公众号完整提示词（Writer+Cleaner）
│   ├── enterprise-windvane.md      ← B端企业应用结构增强
│   ├── visual-templates.md         ← 配图视觉模板
│   ├── ip-definition-guide.md      ← 自定义IP形象5步引导
│   ├── xiaoyao-ip.md               ← 小姚IP定义（参考实现）
│   ├── style-dna.md / prompt-template.md / composition-patterns.md
│   ├── execution-gate.md           ← 执行门禁
│   ├── setup-walkthrough.md        ← 首次配置详细流程
│   ├── live-failures.md            ← 常见故障速查
│   ├── push-draft-pitfalls.md      ← 推草稿踩坑记录
│   ├── two-html-pattern.md         ← 双HTML模式
│   └── ...（共20个reference文件）
├── scripts/
│   ├── generate_image.py           ← GPT Image 2 生成（含重试）
│   ├── push_draft.py               ← 微信推草稿（含推后验证+诊断）
│   ├── check_title_digest.py       ← 标题/摘要字节校验
│   ├── compress_images.py          ← PNG→JPG 压缩
│   ├── init_config.py              ← CLI 配置向导（备用）
│   └── wx-proxy.js                 ← 微信代理服务器
└── assets/examples/                ← 小姚校准样图（5张）
```

## 写作风格

### khazix-writer（默认）

"有见识的普通人在认真聊一件打动他的事。"

- 长短句交替、口语化停顿、故意打破论述
- 禁小标题、禁冒号破折号双引号
- 四层自检：L1 硬规则 → L2 风格 → L3 内容 → L4 活人感

### n8n-wechat-full-prompt

B端公众号爆文写手，Writer + Cleaner 两段式。

- 标题数字暴击、结论前置、表格对比、❌/✅踩坑清单
- Cleaner 只做去 AI 味，不改数据/工具名/结构
- 适合：AI工具/课程/工作流/变现/n8n/飞书类选题

### enterprise-windvane（叠加层）

叠加在 khazix-writer 上，用于 B 端企业应用内容。

- 7 维选题评分（比基础多：冲突张力 + 转化承接）
- 正文 7 段结构：现象→错因→变量→对照表→SOP→风险→CTA
- B 端降噪词典（暴利→高ROI、割韭菜→供应商锁定）

## 合规红线

- 禁止无数据来源的百分比
- 禁止极限词（最好/第一/唯一等）
- CTA 禁止诱导关注（"关注后领取"❌，"回复XX获取"✅）
- 发布前必须经主人确认

## 依赖

- Python 3.8+
- requests（`pip install requests`）
- PIL/Pillow（配图压缩用，`pip install Pillow`）
- Node.js 18+（仅 wx-proxy.js 部署需要）

## License

MIT