# 多平台内容转化方法论

> 公众号长文（母稿）→ 小红书/抖音/视频号/B站/知乎（子稿）的完整转化框架。

## 核心原则

**转化不是改格式，是换语言体系说话。**

每个平台有"原生语言"——用户刷到内容时的场景和预期决定了你的内容格式。

| 平台 | 用户预期 | 原生语言 | 禁忌 |
|---|---|---|---|
| 公众号 | 深度阅读 | 长段落+论述+数据 | 标题太短、没深度 |
| 小红书 | "有用"+"好看" | emoji+短句+清单体+标签 | 长段落、没有emoji |
| 抖音 | "情绪"+"节奏" | 口语化+冲突感+互动引导 | 书面语、没有互动 |
| 视频号 | 信任+社交推荐 | 口播+字幕+金句贴片 | 太花哨、没有信任感 |
| B站 | 深度+有趣 | 长视频+弹幕互动+梗 | 太正式、没有人格 |
| 知乎 | 专业+数据 | 论述+引用+案例 | 太口语、没论据 |

## 母核提炼框架

每篇文章提取一个"母核"——最想让读者记住的一句话。

**提炼方法**：回答一个问题——"这篇文章最想让读者记住的一个观点、一个方法或一个资源是什么？"

母核 = 所有转化内容的"种子"。不同平台用不同方式讲同一个母核。

**示例**：
- 原文：2000字讲Medium+GEO+affiliate
- 母核："Medium的真正价值不是阅读分成，而是DR95域名权重。用AI写科普发Medium，被AI引擎引用后自动产生被动佣金。"

## 转化三步法

### Step 1：提炼母核
从article.md中提取1句话核心观点 + 3个支撑论据。

### Step 2：匹配平台格式（转译）
用目标平台用户听得懂、喜欢听的语言重新讲述母核。

**小红书转译规则**：
- 标题：痛点/否定式 + 数字（≤20字）
- 正文：清单体 + emoji分段 + 每段3-5行
- 结尾：互动引导（评论）+ 收藏引导
- 标签：10个，核心词+长尾词+场景词
- 轮播图：6-9张，每页1个核心观点

**抖音转译规则**：
- 标题：冲突感 + 数字（≤30字）
- 正文：极短句，3-5行/段
- 开头：3秒钩子（否定/疑问/反常识）
- 结尾：互动引导（评论区置顶）
- 轮播图：6-12张，字号要大（滑动时一眼看到）
- 口播脚本：60秒内，钩子→核心→互动

**知乎转译规则**：
- 保留深度，换个开头（从场景/案例切入）
- 补充数据和引用
- 结尾可放链接

**朋友圈转译规则**：
- 1-2句金句 + 1张图
- 不要长文，要"观点碎片"

### Step 3：生成视觉资产
每篇子稿需要配套的视觉卡片（轮播图）。

## 视觉规范（⚠️ 来源标注）

### 硬规则（平台官方，可信 ✅）

| 平台 | 封面比例 | 像素 | 标题字数 |
|---|---|---|---|
| 小红书 | 3:4 竖版 | 1080×1440 | ≤20字 |
| 抖音 | 9:16 竖版 | 1080×1920 | ≤30字 |
| 视频号 | 6:7 竖版 | 1080×1260 | ≤16字 |
| B站 | 16:9 横版 | 1920×1080 | ≤79字 |
| 公众号 | 2.35:1 横版 | 900×383 | ≤30字节 |

### 软规则（行业经验总结，需验证 ⚠️）

以下规则来自花叔(huasheng.ai)调研报告、uBrand、创客贴等二手来源，**非平台官方文档**：

- 小红书封面字号：主标题80-120px，副标题40-60px
- 留白：四周8%安全区
- 标题占页面40-50%宽度
- 每页只讲1个核心观点
- 配色：同一笔记所有图片保持一致（固定2-3色）
- 字体：单张图最多2-3种字体

**⚠️ 使用建议**：这些是起点，不是标准。最可靠的做法是找5-10个同领域优秀账号，截图拆解，提炼经过市场验证的规范。

## 3张图覆盖全平台

实操博主总结的最小覆盖方案：

```
1. 竖版 1080×1440（3:4）→ 小红书封面/正文
2. 竖版 1080×1920（9:16）→ 抖音封面/视频号
3. 横版 1920×1080（16:9）→ 公众号封面/B站封面
```

一个设计稿裁出3个尺寸，5分钟搞定。

## 轮播图结构模板

### 知识/教程类（小红书）
```
封面（大标题+hook，痛点/否定式）
→ 核心观点1（数据支撑）
→ 核心观点2（案例/对比）
→ 核心观点3（方法/步骤）
→ 实操清单/模板
→ 金句页（记忆锚点）
→ CTA页（互动引导+收藏引导）
```

### 抖音图文
```
封面（超大字+冲突感）
→ 数据冲击（核心数字放大）
→ 对比/概念（SEO→GEO式对比）
→ 路径/步骤（简洁编号）
→ 金句页（视觉最重）
→ 互动页（评论区引导）
```

## 视觉渲染：用归藏skill，不要手搓HTML

**关键教训（2026-07-05实测）**：自己写HTML渲染轮播图是"穷人版"。归藏的 `guizang-social-card-skill` 已经解决了所有排版问题——2套视觉系统、28个版式骨架、10套配色、11个品类适配规则。

### 为什么用归藏skill而不是手搓

| 维度 | 手搓HTML | 归藏skill |
|---|---|---|
| 视觉系统 | 自己定义配色 | 瑞士网格风+杂志风，经过验证 |
| 字体 | 系统默认 | Inter + Noto Sans SC + IBM Plex Mono |
| 字号层级 | 随意定 | 严格规则："越大越轻"（大标题weight 200-400） |
| 留白 | 浪费空间或太挤 | 网格控制，内容≥75%画布 |
| 版式 | 每张都一样 | 每页用不同recipe（S01/S05/S02等） |
| 品类适配 | 无 | 11类自动路由（产品测评/截图教程/数据回顾等） |

### 两条视觉线（用户明确要求）

**用户原话**："不要搞什么花里胡哨的赛博科技的，要么极简要么实拍/截图"

- **极简信息图（主力80%）**：白底+大标题+数据截图，瑞士网格风
- **实拍/截图（辅助20%）**：真实工具界面+标注说明

**❌ 禁止**：赛博科技风（深色+荧光色+光效）、过度装饰、一眼AI的插画

### 归藏skill已安装路径

```
~/.hermes/skills/guizang-social-card-skill/
```

**使用方法**：
1. 内容转换用LLM（提炼母核→按平台语言重写）
2. 视觉渲染用归藏skill（选recipe→填内容→Playwright截图）
3. 发布用AiToEarn

### 适合我们的recipe（AI/工具/效率赛道）

| Recipe | 用途 | 适合场景 |
|---|---|---|
| S01 Accent Cover | 封面 | 大标题+元数据条 |
| S02 Two Signals | 对比 | SEO vs GEO、方案A vs B |
| S03 Data Layer | 数据卡片 | 工具属性、案例拆解 |
| S04 Interface Mock | 界面展示 | 工具截图、UI演示 |
| S05 Trap/Warning | 误区 | 常见错误、避坑 |
| S06 Pipeline | 流程 | 步骤、工作流 |
| S07 Takeaway Ledger | 总结 | 金句+CTA |
| S08 Image Hero | 图片封面 | 有强图时用 |
| S09 KPI Tower | 数据对比 | 3-4个数字并排 |
| S11 Numbered Statement | 编号要点 | 数据+论据 |
| S12 Matrix Grid | 矩阵 | 工具对比表 |

### Swiss配色方案（4选1，每篇笔记只用1个）

| 配色 | 适合 |
|---|---|
| IKB Blue（克莱因蓝） | AI工具、科技、产品更新 |
| Lemon Yellow | 数据、增长、活力 |
| Lemon Green | 效率、自动化、绿色科技 |
| Safety Orange | 警告、对比、紧迫感 |

**我们默认用 IKB Blue。**

## 内容质量标准：什么样的图文内容符合要求

### 核心认知（归藏原话）

> "图文卡片和PPT完全是另一种生物：竖屏、信息流里1秒钟决定停不停下、靠图说话而不是靠字。"

> "AI在'自由版面设计'上现在还是平庸的，给它一个被验证过的骨架，它的任务就从'设计'降级成'填充'，成品稳定性立刻上来。"

> "我宁可它少用AI，也不想它把AI用成那个让所有图文卡片长得都像姐妹的元凶。"

### 封面类型选择（花叔调研）

| 类型 | 特征 | 适合我们 | 互动优势 |
|---|---|---|---|
| **纯文字封面** | 关键词突出+信息量暗示 | ✅ 教程、干货 | 收藏驱动 |
| **前后对比** | 两图强烈反差 | ✅ 用AI前vs用AI后 | 冲击力强 |
| **截图+标注** | 真实界面+说明 | ✅ 工具评测 | 信任感 |
| **数据冲击** | 超大数字 | ✅ 行业趋势 | 震撼 |

### 图片来源优先级

```
用户自己的截图/照片（最推荐——最不"AI感"）
  → 免费图库（Pexels/Unsplash/Flickr CC，自动记录版权）
    → 截图美化（套设备边框+材质背景）
      → AI生图（最后手段，带风格约束词避免一眼AI）
```

### 轮播结构模板

**知识/教程类（我们的主力）**：
```
封面（大标题+hook，S01 Accent Cover）
  → 痛点/误区（S05 Trap Rows）
  → 核心概念（S02 Two Signals对比）
  → 数据支撑（S11 Numbered Statement或S09 KPI Tower）
  → 实操路径（S06 Pipeline）
  → 案例拆解（S03 Data Layer）
  → 总结+CTA（S07 Takeaway Ledger）
```

## 现成工具清单

| 工具 | 做什么 | 适合 |
|---|---|---|
| **归藏 guizang-social-card-skill** | 文章→3:4轮播图（已安装） | **主力：视觉渲染** |
| **扣子空间** (space.coze.cn) | 输入主题→文案+AI生图+排版→成品 | 一站式快速出图 |
| **薯图宝** (picbatch.com) | 批量生成小红书图文，自定义模板 | 批量生产 |
| **Mew Design** (mew.design) | URL/内容→AI自动拆分→多页轮播 | 快速原型 |
| **简单设计** (jiandan.link) | 一句话生成封面图 | 封面快速出图 |

## HTML轮播图→截图 pipeline（备用方案，归藏skill不可用时）

### 流程
1. 写一个HTML文件，包含所有卡片（每张卡一个`<div class="card">`）
2. 用Python HTTP Server本地托管
3. Playwright打开页面，逐个card元素截图
4. 输出PNG文件

### 代码模板
```python
from playwright.sync_api import sync_playwright
import os

os.makedirs('cards', exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/usr/bin/chromium-browser',
        args=['--no-sandbox', '--disable-gpu']
    )
    page = browser.new_page(viewport={'width': 1200, 'height': 1600})
    page.goto('http://localhost:8765/xhs-cards.html')

    cards = page.query_selector_all('.card')
    for i, card in enumerate(cards):
        card.screenshot(path=f'cards/card_{i+1}.png')

    browser.close()
```

### HTML设计规范
- 每张卡固定尺寸：`width: 1080px; height: 1440px;`（小红书3:4）
- 背景色统一：深色主题用`#2D2D2D`，渐变用`linear-gradient`
- 字号层级：Hero(120-180px) > 标题(56-72px) > 正文(36-44px) > 辅助(28-32px)
- 强调色不超过3种（推荐：主色白+强调橙#FF6B35+数据红#FF4444）
- 卡片内用`flex-direction: column; justify-content: center; align-items: center;`居中
- 需要左对齐的用`align-items: flex-start`

### 踩坑记录
- **Playwright file:// 协议失败**：chromium sandbox模式下file://可能报ERR_FILE_NOT_FOUND。解决：用HTTP Server本地托管，不要用file://协议
- **文件权限**：write_file创建的文件默认`-rw-------`，Playwright可能读不到。解决：先`chmod 644`
- **中文字体**：确保CSS font-family包含`"PingFang SC", "Noto Sans SC", "Microsoft YaHei"`，否则中文显示为方块
- **emoji渲染**：chromium对emoji支持良好，但服务器环境可能缺少emoji字体。如emoji显示为方块，需`apt install fonts-noto-color-emoji`

## JasonMar 方法论（飞书文章参考）

来源：https://my.feishu.cn/wiki/AOQ2wtlAbiZiq9k2HUPc8UHrnUs

核心洞察：**"把视觉规则写死，把内容变量放开。"**

具体做法：
1. 先拆一张封面的结构：标题位置、字体层级、重点词强调、背景色、主视觉、图标风格、留白、CTA位置
2. 把这些写成固定规范
3. AI生成图片在统一规则下稳定出图

规则越稳定，批量生成越靠谱。

## AI生图实测经验（2026-07-05）

### GPT Image 2 中文渲染限制

**问题**：prompt写"Large bold Chinese title '别再靠阅读分成赚钱了'"，AI渲染成英文"全球供应链重构下的中国制造新机遇"。

GPT Image 2对长中文句子（>4字）的渲染极不稳定。短中文词（2-4字如"DR95"、"Medium"）成功率高，长句子几乎必翻车。

**对策**：
1. **AI生图只做纯视觉背景**（渐变、纹理、产品截图、抽象图形），文字用HTML/CSS代码叠加 → 文字100%准确
2. **用归藏guizang-social-card-skill**走HTML渲染路线 → 文字100%准确 + 专业排版
3. 如果坚持AI生图，prompt全部用英文描述视觉风格，不提中文文字内容

### generate_image.py 直接调用（备用）

当 `generate_image.py` 脚本静默失败(exit=1, no output)时，直接用requests调API：

```python
import os, json, requests, base64

config = json.load(open(os.path.expanduser("~/.hermes/skills/ai-gzh-platform/config.json")))
api = config["image_api"]
key = os.getenv(api["key_env"])  # GPT_IMAGE2_API_KEY
endpoint = api["endpoint"]       # https://api.zhongzhuan.chat/v1/images/generations
model = api["model"]             # gpt-image-2

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
payload = {"model": model, "prompt": "your prompt here", "n": 1, "size": "1024x1536"}

r = requests.post(endpoint, json=payload, headers=headers, timeout=300)
img_bytes = base64.b64decode(r.json()["data"][0]["b64_json"])
with open("output.png", "wb") as f:
    f.write(img_bytes)
```

⚠️ 必须用 `terminal()` 执行（`execute_code` 沙箱读不到 env）。
⚠️ `source ~/.env` 后需要 `export GPT_IMAGE2_API_KEY`，否则子进程拿不到。

### 支持的尺寸

| 尺寸 | 比例 | 用途 |
|---|---|---|
| 1024×1024 | 1:1 | 方形封面 |
| 1024×1536 | 2:3 | 接近小红书3:4 |
| 1536×1024 | 3:2 | 横版封面 |
| 1792×768 | 2.35:1 | 公众号封面 |
| 1024×1820 | ~9:16 | 抖音/视频号 |

## 参考来源

| 来源 | 内容 | 可信度 |
|---|---|---|
| JasonMar 飞书文章 | 视觉规则写死+内容变量放开 | ⚠️ 个人方法论 |
| 花叔(huasheng.ai) | 小红书轮播图视觉调研报告 | ⚠️ 一个人的调研 |
| Tugan.ai | 基于原文转换效果优于基于描述转换 | ⚠️ 工具厂商观点 |
| uBrand / 创客贴 | 设计规范建议 | ⚠️ 设计工具厂商 |
| 多篇实操博主 | 3张图覆盖全平台 | ⚠️ 行业惯例 |
| 平台官方文档 | 尺寸/字数限制 | ✅ 官方规则 |
