---
name: ai-gzh-platform
description: AI公众号内容生产平台。一键安装完整的公众号内容生产系统，包含选题调研、爆款分析、内容撰写、归藏材质插画配图、base64内嵌HTML、推草稿到公众号、多平台分发。当用户说安装公众号平台、搭建公众号系统、写公众号文章、按SOP写内容、生产今天的公众号内容、走内容流程、写篇推文时触发。
version: 4.0.0
author: 大姚
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wechat, content, gpt-image, publishing, automation, multiplatform]
    category: productivity
---

# AI公众号内容生产平台 v4

## ⚠️ 使用前必读（2026-07-17 v4 启动版 · 师傅专属）

**本 skill 服务师傅的「大姚AI提效」公众号 v4 启动：**

- **一句话定位**：1 个人用 AI + 自动化，搭出能顶 1 个团队的工作流
- **1 类生存画像**：月入 1-3 万内容/运营/小团队负责人 → 想从「我一个人干活」变成「我顶一个团队」
- **5 个栏目**：一人作战室 / 工作流拆解 / 真实项目复盘 / 新工具上生产线 / 自动化赚钱实验
- **5 段式结构**：卡 → 拆 → 工具 → 结果和坑 → 读者能拿走
- **8 工具栈**：Hermes / Coze / n8n / 飞书 / Obsidian / WorkBuddy / Codex / 中转站 / 公众号
- **字数**：1500-1800 字（**不是 ≥2500**）
- **默认 CTA**：关键词钩子（"回复 6 步"）→ 9.9 SOP → 99 元/年知识库
- **4 阶梯产品**：9.9 / 99元/年 / 199元/次 / 1999元

写每篇前必须：① 选题过 v4 1 类画像 ② 严格 5 段式 ③ 字数 1500-1800 ④ 文末钩子用 5 步动线模板

详见 `references/v4-定位-1句话公式.md`

> Preflight → 00规则取料 → 08精选池选题 → 写作 → 归藏配图 → base64内嵌HTML → Postflight → 推草稿 → 发布队列同步

## When to Use

触发：用户说"写公众号文章 / 用 ai-gzh-platform / 生产公众号内容 / 走内容流程 / 写篇推文"时。

## 首次安装

如果 `config.json` 不存在或 `setup_status != "configured"`，**禁止直接生成文章**。

```bash
cd ~/.hermes/skills/ai-gzh-platform
bash install.sh
```

install.sh 自动完成：
- pip install Pillow + requests
- npm install -g lark-cli
- git clone guizang-material-illustration + guizang-social-card-skill
- 引导运行 `scripts/init_config.py`（交互式生成 config.json）

手动配置：
```bash
cp config.example.json config.json
# 编辑 config.json 填入实际值
python3 scripts/init_config.py  # 交互式向导
```

详见 `references/setup-walkthrough.md`

## 排版风格（11选1，默认鲲鹏蓝）

| id | 中文名 | 适合 |
|---|---|---|
| `kunpeng-blue` | **鲲鹏蓝（默认）** | 技术方案、行业分析、咨询感内容 |
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

配置方式：`config.json` → `html_template.style_name`，颜色定义在 `html_styles` 段。

## 配图风格

**统一使用归藏材质插画**（guizang-material-illustration skill）。

配图清单（最少4张）：

| 配图 | 生成方式 | 说明 |
|---|---|---|
| 封面素材 | GPT Image 2 直出 | 21:9 横版，公众号头条封面 |
| 配图1 | GPT Image 2 + 归藏材质prompt | Pipeline/流程风格 |
| 配图2 | GPT Image 2 + 归藏材质prompt | Chart/数据风格 |
| 配图3 | GPT Image 2 + 归藏材质prompt | Before/After 对比 |
| 配图4（可选） | GPT Image 2 + 归藏材质prompt | Layer Stack/门槛风格 |

**必须读取**：`guizang-material-illustration` skill 的 SKILL.md（配图 prompt 模板）。

**⚠️ 文件命名规范**：图片文件名必须包含中文关键词，否则 `摸鱼小李 skill` 无法匹配嵌入。格式：`配图-<中文关键词>-<英文slug>.png`。

## 生产流程（Harness 模式）

```
┌─────────────────────────────────────────────────┐
│  Phase 0: Preflight（门禁检查）                   │
│  python3 scripts/preflight.py                    │
│  检查：config/GPT Image 2/飞书/工具依赖          │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 1: 选题与调研                              │
│  爆款调研 → 选题评分 → 风格路由                   │
│  输出：research.md + state.json                   │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 2: 内容撰写                                │
│  读取：风格路由决策表 → 对应 writing style        │
│  输出：article.md                                 │
│  硬约束：≥2500字/≥2表格/≥3配图标记/禁用词0       │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 3: 配图生成                                │
│  归藏材质插画 + GPT Image 2                       │
│  输出：imgs/*.png                                 │
│  最少4张（封面+3张材质插画）                      │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 4: HTML 生成（v4.1 摸鱼小李）             │
│  npx gzh-design-skill render                      │
│    --input article.md --theme 摸鱼绿             │
│  输出：6 套主题 HTML 选 1，复制到公众号后台       │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 5: Postflight（验证）                      │
│  python3 scripts/postflight.py --output-dir xxx   │
│  检查：字数/禁用词/表格/配图/HTML/段落/峰值      │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 6: 交付                                    │
│  发送：HTML文件 + 封面图                          │
│  输出：验收表                                     │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 7（可选）: 推草稿到公众号                   │
│  需 wechat_proxy.enabled=true                     │
│  python3 scripts/push_draft.py ...                │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Phase 8（可选）: 多平台分发                       │
│  需 aitoearn MCP                                  │
│  加载 aitoearn-multisite skill                    │
└─────────────────────────────────────────────────┘
```

## 飞书内容中台（16 表）

- **Base Token**: `TejybyBY0a4Q5bsOYmucwzVTnwf`
- **Base URL**: https://pcnhyp285wrm.feishu.cn/base/TejybyBY0a4Q5bsOYmucwzVTnwf
- **操作身份**: `--as bot`

### 核心数据表（7 张）

| 表名 | Table ID | 用途 |
|---|---|---|
| 00｜Hermes取料规则 | `tblGmclVtJWsrzUQ` | 取料条件/禁用条件/Hermes动作 |
| 01｜外部资料库 | `tblKhjvH1gd12OHh` | 飞书文件夹 300+ 文件索引 |
| 02｜流程拆解库 | `tbliBzDSxrXqNcFt` | 技术流程/工作流/部署步骤 |
| 03｜问题与痛点库 | `tbluJ4dzXodscL8a` | 面试题/FAQ/用户痛点 |
| 04｜观点反常识原子库 | `tblos5Xt14CM8phY` | 行业趋势/观点判断/方法论 |
| 05｜改造方案库 | `tblk14J0YUVYWfEg` | 原方案→新方案的改造记录 |
| 06｜实战案例库 | `tblMfktmt48QO3Ik` | 具体项目案例/落地实践 |
| 07｜选题生产表 | `tblXdtaMSR96uhbb` | 选题排期/写作状态/发布跟踪 |

### 生产流水线表（9 张）

| 表名 | Table ID | 用途 |
|---|---|---|
| 08｜精选生产池 | `tbljsqpHs7l9N0Er` | 从原子中精选→生产文章的流水线 |
| 09｜发布队列 | `tblXhlOuHFuBAGTF` | 文章排期发布管理 |
| 10｜扩展采集入口 | `tbl5CfYGmX72pHc3` | 新发现的素材来源录入 |
| 11｜源资料精洗索引 | `tblJC15jTqSpYaPb` | 源资料的清洗计划和状态 |
| 12｜云盘删除验收表 | `tblGlyT6d4eyubR6` | 云盘文件删前验收确认 |
| 13｜可独立取料原子库 | `tbl1bxlcfUJd5rXR` | Hermes 可直接使用的高质量原子 |
| 14｜题材组合模板 | `tblYthCfyozMquPW` | 选题的组合配方和文章结构模板 |
| 15｜视觉素材库 | `tbldAE1lDtns5SVs` | 图片/截图/视觉素材管理 |
| 16｜跨平台适配表 | `tblzd6LInkRTC2oh` | 公众号→小红书/知乎/抖音等平台的适配内容管理 |

### 数据流

```
素材库(01-06) ──拆解──→ 13可独立取料原子库
                            ↓
00取料规则 ──约束──→ assemble_atoms.py ←── 14题材模板
                            ↓
                    08精选生产池 ──同步──→ 09发布队列
                            ↓
                    写作 → 配图 → HTML → 推草稿
                            ↓
                    16跨平台适配表（小红书/知乎/抖音等）
```

## Phase 0: Preflight（门禁检查）

每次执行前**必须**跑门禁：

```bash
source ~/.hermes/.env && export GPT_IMAGE2_API_KEY
python3 scripts/preflight.py --check-atoms
```

门禁检查项（v4 新增 16 表检查）：
1. config.json 核心字段（brand_name / style_name / setup_status）
2. 飞书 16 表 table_id 全部已配置
3. 飞书 Base 连通性
4. GPT_IMAGE2_API_KEY 存在且有效
5. 微信代理（可选，wechat_proxy.enabled 时检查）
6. 工具依赖（Pillow / requests / lark-cli）
7. 关键表数据量（00规则/13原子/14模板/08精选/09发布）

门禁检查项：
1. config.json 核心字段（brand_name / style_name / setup_status）
2. GPT_IMAGE2_API_KEY 存在且有效
3. 飞书连接（可选，feishu.enabled 时检查）
4. 微信代理（可选，wechat_proxy.enabled 时检查）
5. 工具依赖（Pillow / requests / lark-cli）
6. 排版风格存在

**门禁不通过不执行**。修复问题后重跑。

## Phase 1: 选题与取料（harness 模式）

v4 核心变化：选题从 08 精选生产池取，取料从 13 原子库按 00 规则取。

### 自动取料流程

```bash
# 从 08 精选生产池选一条 P0 选题，自动组装原子
python3 scripts/assemble_atoms.py --topic "关键词"
# 或指定 record_id
python3 scripts/assemble_atoms.py --pool-id recXXXX
```

脚本自动完成：
1. 读取 00 取料规则（14 条约束）
2. 从 08 精选生产池选题（按关键词或 record_id）
3. 从 14 题材组合模板读取原子配方
4. 从 13 可独立取料原子库按规则取料（A/B 证据等级优先）
5. 从 15 视觉素材库取关联素材
6. 输出 atoms.json

### 08→09 发布队列同步

```bash
# 将 08 的 P0 可写选题同步到 09 发布队列
python3 scripts/sync_publish_queue.py
# 预览模式
python3 scripts/sync_publish_queue.py --dry-run
```

### 文章类型判断（先于风格路由）

| 用户说的 | 文章类型 | 写法 |
|---|---|---|
| 「帮我引流/展示服务/吸引客户」 | **引流文** | 痛点→案例→做了什么→效果→交付清单→CTA。读者看完要觉得「我也需要这个」 |
| 「写一篇技术文章/记录改造过程」 | 技术文 | 问题→方案→实现→踩坑→代码。面向同行/技术人员 |
| 「按SOP写内容/生产今天的公众号」 | 标准内容文 | 按风格路由走 |

**关键区分**（2026-07-11 用户原话纠正）：用户说「写公众号内容」且上下文涉及「帮XX公司做了XX」时，默认是**引流文/服务展示**，不是技术复盘。自检：读者看完会不会想「我也需要这个」？不会=还是太技术。引流文不需要写脚本代码、行数统计、技术细节——要写业务价值、具体效果、怎么联系。

### 风格路由决策表

| 选题关键词 | 写作风格文件 | 叠加 |
|---|---|---|
| AI自动化/工作流/内容中台/选题/拆解/改造/实战复盘 | **`dayao-writing-prompt.md`**（默认） | — |
| AI工具/课程/变现/n8n/飞书/线索/获客/客服/销售 | `n8n-wechat-full-prompt.md` | — |
| 政策解读/企业深度分析/个人视角叙事 | `writing-style.md`（khazix-writer） | — |
| AI企业应用/B端/SaaS/Agent落地/ROI/采购 | `writing-style.md` | + `enterprise-windvane.md` |
| 引流文/服务展示/案例引流/帮企业定制 | `lead-gen-writing-style.md` | — |

| **默认路由**：用户说「写公众号内容」且没有明确指定风格时，用引流文风格(`lead-gen-writing-style.md`)。理由：用户7/14纠正过一次——他说「先帮我写今天的工众号内容」，agent用了dayao实战复盘体，用户说「这篇不是用的我的那个引流的写的吗」。大姚的公众号主要目的是引流获客，不是技术分享。只有用户明确说「写技术文/实战复盘」时才用dayao-writing-prompt。

**配图风格**：统一使用归藏材质插画（guizang-material-illustration skill），不要用通用GPT Image 2 prompt。生成配图前必须读取该skill的visual-style.md和prompt-patterns.md。

**截图要求**：飞书表格、HTML渲染、卡片渲染都用真实输出截图，不要mock-up。Playwright截真实HTML（中文文件名cp成英文名），lark-cli拉真实数据。

**正文质量**：写之前先读最近2-3篇引流文的article.md，学习具体数字/案例展开/交付清单/角色价值。写完和历史文章对比，不能比历史最佳差。

### ⚠️ 引流文 ≠ 技术文档（2026-07-11 用户原话纠正）

**用户原话：「啥玩意 不行 太差了 效果」**

第一次写引流文时，agent 按技术文档思路写——堆表格、列脚本行数、讲代码实现。用户直接否了。

**根因**：没搞清楚「文章是给谁看的」。引流文的读者是**企业老板/运营负责人**，不关心脚本行数和代码实现。关心「能不能帮我解决问题」「值不值得花钱找你做」。

**自检**：读者看完会不会想「我也需要这个」？不会 = 还是太技术。

**触发判断**：用户说「引流/获客/展示服务能力/案例包装/帮企业做XX/写给客户看」→ 必须用 `references/lead-gen-article-guide.md`，不要用 n8n-blogger 或 khazix-writer。

### 调研（必做）

1. 从 content_directions 提取关键词，限定最近7天，搜索3-5条爆款标题
2. 选题防撞：扫 covered_topics，重叠则换方向
3. 五维评分（5分制）：生存焦虑(30%)+需求具体(20%)+可复制(25%)+画像匹配(15%)+数据支撑(10%)
4. 决策：≥4.0直接写，3.5-3.9写但排后，<3.5淘汰

### v4 1 类生存画像过滤（2026-07-17 新增）

任何选题**必须**先过 v4 1 类生存画像，否则不写。

- **画像**：月入 1-3 万内容/运营/小团队负责人
- **5 类必选**：内容运营 / 小团队负责人 / 个人 IP 副业
- **过滤规则**：
  - 画像匹配 ≥ 80% → 直接进选题库
  - 50-80% → 改写切入角度（从「企业老板/技术深度」改成「1 个小老板/可复用工具」）
  - <50% → 淘汰

详见 `references/v4-定位-1句话公式.md` + `references/5-分词速查表.md`

详见 `references/real-research-methodology.md`（次幂数据+知识星球+B站/知乎四线并行调研）

### P2 功能/数据/渠道预清点 ⚠️ REQUIRED

写之前先问/自查 3 类素材：
1. **数据**：所有要写的百分比/工时/月省/转化率——是否有真实来源？
2. **功能/产品**：要写的功能——用户真的做出来了吗？
3. **渠道/CTA**：要写的链接/二维码——用户当前渠道状态如何？

输出格式（喂给 Writer）：
```
## 本篇真实可用素材
- 数据：xxx
- 功能：xxx ✅ / xxx ❌（没做）
- 渠道：xxx ✅ / xxx ❌（明天才挂）

## 不得写入（替代为）
- "xxx" → "xxx"
```

## Phase 2: 内容撰写

**必须读取的文件**（按风格路由决策表选对应文件）：
1. 风格路由表选出来的 writing style 文件
2. `atoms.json`（如果有原子化数据）或 Phase 1 的 research.md
3. 对应的 prompt 模板

**写作硬约束**：
- 所有事实/数据必须有真实来源，不得编造
- 禁用词零命中：赋能/闭环/颠覆式/颗粒度/抓手/底层逻辑/综上所述/值得注意的是
- 双引号零命中（用「」代替）
- **字数：1500-1800 字**（v4 启动版实测：完读率 55-65%；超过 2500 掉到 30-40%）
- **5 段式结构必含**（v4 启动版）：卡 → 拆 → 工具 → 结果和坑 → 读者能拿走
- **v4 双风格路由**（2026-07-17）：
  - v4 5 段式默认 → 一人作战室 / 工作流拆解 / 真实复盘 / 新工具 / 自动化赚钱 5 栏目
  - 原版 6 段引流文（痛点→案例→做了什么→效果→交付清单→CTA）→ 仅写企业服务展示时用
- ≥2 个表格、≥3 个配图标记
- 正文段落每段 ≤ 3 行（v4 加严，原 ≤4 行）
- 工具段必须给「可抄的命令」（参考知识库 v0.1 §4.5 硬约束）
- 翻车日记必须真实（v5 1548 字阅读 100 / 次幂 404 / A 版猝死限流 / 菜单栏塞满）
- 禁用清单（知识库 v0.1 §4.3）：
  - 禁用词：赋能/闭环/颠覆式/抓手/底层逻辑/降维打击/打通/永动机/能量场/显化/调频/唯一/引领/颠覆
  - 禁用符号：⭐ emoji / 双引号「""」/ 分割线 `---`
  - 禁用结构：三段式加粗总结 / 公式化反问 / 鸡汤式升华
  - 禁用 AI 套路：「作为一个 AI」/ 滥用比喻 / 发明新名词
- 信息峰值密度：每 300 字 ≥ 1 个峰值（金句/数据/小案例/对比/反常识），详见 `references/information-density.md`
- 标题 ≤ 30 字节，摘要 ≤ 54 字节

**标题公式**：[主体]+[场景/数字]+[解决什么问题]

**标题流程（v4 新增）**：
1. 读取 `references/title-formulas.md`（9 种标题方法 + 5 问自检）
2. 用「AI 批量出题 Prompt」一次性出 10 个标题
3. 过 5 问自检（目标用户有点击欲？有利益点？有数字/对比？身份标签精准？情绪词得当？）
4. 过字节校验：
```bash
python3 scripts/check_title_digest.py --title "标题" --digest "摘要"
```

**输出**：`output/{date}-{slug}/article.md`

## Phase 3: 配图生成

**必须读取**：`guizang-material-illustration` skill 的 SKILL.md（配图 prompt 模板）

配图生成命令：
```bash
source ~/.hermes/.env && export GPT_IMAGE2_API_KEY

# 封面图（21:9 横版，公众号头条封面）
python3 scripts/generate_image.py --prompt "PROMPT" --size "1792x768" --output imgs/封面-cover.png

# 正文配图（1.9:1，归藏材质插画风格）
python3 scripts/generate_image.py --prompt "PROMPT" --size "1792x1024" --output imgs/配图-xxx.png
```

**⚠️ 文件命名规范**：`配图-<中文关键词>-<英文slug>.png`，中文关键词必须能被 `摸鱼小李 skill` 的命名规则匹配到。

**生图失败时的降级顺序**：
1. 直接调 `generate_image.py`（zhongzhuan.chat 中转通常稳定）
2. `delegate_task` 派子代理生图
3. 告知用户"图片生成失败"，先交付 article.md + 无图 HTML 骨架
4. ❌ 绝不用旧选题的图片冒充

## Phase 4: HTML 生成（v4.1 启动版·摸鱼小李接管）

**v4.1 启动版改用摸鱼小李 `gzh-design-skill` 做排版**（不内置 HTML 生成器，避免 AGPL 传染）。

### 安装

```bash
npx skills add https://github.com/isjiamu/gzh-design-skill
```

### 使用流程

1. 师傅写完 `article.md`（v4.1 5 段式 + 1500-1800 字）
2. 跑摸鱼小李 skill：
   ```bash
   npx gzh-design-skill render --input article.md --theme 摸鱼绿
   ```
3. 6 套主题选一（按师傅 v4 1 类画像）：
   - **摸鱼绿**（默认）→ 工具/盘点/测评
   - 留白禅意 → 深度随笔
   - 石墨极简 → 设计/科技评论
4. 输出 HTML 复制到公众号后台

**AGPL 说明**：摸鱼小李原 skill 是 AGPL-3.0（衍生品必须开源）。师傅**不 fork 不修改原代码**，只"调用"它的输出，AGPL 风险为 0。

详见摸鱼小李官方文档：https://github.com/isjiamu/gzh-design-skill

### 主题选择建议（v4 1 类画像适配）

| 主题 | 适配场景 |
|------|---------|
| 摸鱼绿（默认） | 工具盘点、自动化实操、AI 提效（推荐首选）|
| 留白禅意 | 深度思考、个人成长、心法类 |
| 石墨极简 | 严肃评论、行业分析、方法论 |
| 红白 | 强观点输出、争议话题 |

## Phase 5: Postflight（验证）

```bash
python3 scripts/postflight.py --output-dir output/{date}-{slug}
```

验证项：
1. article.md 存在且字数 ≥2500
2. 禁用词零命中、双引号零命中
3. 数据表格 ≥2个（≥4行数据行）
4. 配图标记 ≥3个
5. 图片文件 ≥4张且 >100KB
6. HTML 文件存在且内嵌 ≥3张 base64 图片
7. 正文段落每段 ≤4 行（超限输出具体行号）
8. 信息峰值密度每 300 字 ≥1 个（⚠️ 警告，不阻断交付）

**验证不通过不交付**。修复问题后重跑。

## Phase 6: 交付

**加载**：`feishu-send-attachment` skill（通过飞书 im/v1 API 发送真实文件卡片）

发送给用户：
1. 完整 HTML 文件（base64 内嵌）— 用 `msg_type=file` 发送
2. 封面图（单独发送，用于公众号后台上传）— 用 `msg_type=image` 发送

❌ 不要用 `MEDIA:/path` 文本方式发文件——飞书会显示为纯文本字符串。

输出验收表：

| 项 | 结果 |
|---|---|
| skill | ai-gzh-platform v3 |
| config | configured / blocked |
| 排版风格 | style_name |
| article workflow | Phase 0-5 已执行 / 哪步阻塞 |
| image model | gpt-image-2 |
| image files | cover + n 张正文图 |
| article QA | 禁用词/双引号/字数/表格/配图标记 |
| title bytes | x / 30 |
| digest bytes | x / 54 |
| HTML | xxxKB, x张内嵌图 |
| optional publish | 推草稿/多平台分发是否执行 |

## Phase 7（可选）: 推草稿到公众号

需要 `wechat_proxy.enabled=true`。

预处理3步：compress_images.py → HTML 不含 cover → check_title_digest.py

```bash
source ~/.hermes/.env && export WX_PROXY_SERVER WX_PROXY_PORT WX_PROXY_TOKEN WX_APPID WX_APPSECRET
python3 scripts/push_draft.py --title "标题" --digest "摘要" --html 推草稿版.html --cover cover.jpg --images imgs/*.jpg
```

推完自动验证：拉 draft/get 确认中文字符>800 且 \u=0。失败自动删草稿。

**⚠️ WX_PROXY_SERVER 必须 export**：`source ~/.hermes/.env` 后必须 `export WX_PROXY_SERVER`。

详见 `references/push-draft-pitfalls.md`

## Phase 8（可选）: 多平台分发

**小红书专项**：已有独立 skill `ai-xhs-platform`，包含6大标题公式（数据验证版）、4种写作风格、postflight自动校验。触发"转小红书"时优先加载该skill，不要用通用的多平台分发流程。

通用分发流程（非小红书平台）：
加载 `aitoearn-multisite` skill + 读取 `references/multiplatform-content-conversion.md`。

14.1 提炼母核：从 article.md 提取1句话核心观点+3个支撑论据
14.2 按平台转译（不是复制粘贴，用目标平台原生语言重新讲述）
14.3 生成视觉资产：用归藏 guizang-social-card-skill
14.4 用 AiToEarn 发布：createChannelPublishFlow → publishChannelTaskNow

## 合规红线

- 禁止无数据来源的百分比
- 禁止极限词（最好/第一/唯一等）
- CTA禁止诱导关注（"关注后领取"❌，"回复XX获取"✅）
- **发布前必须经主人确认**

### v4 产品阶梯合规（2026-07-17 新增）

文章里如果提到产品/服务，必须按以下阶梯：

- **9.9 元**：9.9 SOP 单文档（引流品）
- **99 元/年**：知识库 + 微信答疑群 + 持续更新（核心信任品，**7/22 上线**）
- **199 元/次**：1v1 诊断（升级品）
- **1999 元**：AI 自动化体系搭建（高客单）

**禁止**：
- 模糊价格（"几十块"、"几百元"）
- 模糊产品（"我们的服务"、"私聊咨询"）
- 1v1 私聊 CTA（默认用关键词钩子）

详见 `references/产品阶梯-9.9-99-199-1999.md`

## Reference 路由表（按需加载）

| 需要什么 | 加载文件 |
|---|---|
| **引流文/服务展示写作** | **`references/lead-gen-article-guide.md`** |
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
| 摸鱼小李排版 skill（v4.1 新增） | `npx gzh-design-skill`（独立安装，原 skill 是 AGPL-3.0） |
| 推草稿踩坑 | `references/push-draft-pitfalls.md` |
| 双重UTF-8编码陷阱 | `references/push-draft-double-encoding-pitfall.md` |
| 常见 Live Failure | `references/live-failures.md` |
| n8n 工作流调试 | `references/n8n-integration-pitfalls.md` |
| 本地降级 HTML | `references/local-fallback-html-pack.md` |
| System Prompt 参考 | `references/system-prompt.md` |
| 公开仓库发布检查 | `references/public-release-checklist.md` |
| 真实素材调研方法论 | `references/real-research-methodology.md` |
| 多平台分发 | `aitoearn-multisite` skill + `references/multiplatform-content-conversion.md` |
| 用户素材盘点与分配 | `references/user-asset-ingestion.md` |
| 原子化内容管线 | `references/atomized-content-pipeline.md` |
| Harness 迁移指南 | `references/harness-migration-guide.md`（从 checklist 迁移到脚本化门禁的方法论） |
| **大姚实战复盘体（默认）** | **`references/dayao-writing-prompt.md`**（AI自动化工作流实战，5种文章类型） |
| **引流文写作风格** | **`references/lead-gen-writing-style.md`**（kunpeng白皮书风，场景式标题+8章节结构） |
| **标题公式库（v4 新增）** | **`references/title-formulas.md`**（9种标题方法+5问自检+AI批量出题prompt+引流文vs技术文差异） |
| **信息峰值密度（v4 新增）** | **`references/information-density.md`**（每300字≥1峰值，5种峰值类型+排版强化+postflight集成） |
| **2026-07-11 踩坑记录** | **`references/pitfalls-session-2026-07-11.md`**（#53-56 IMG_KEYWORDS/文件名/引流文路由/HTML截图，#59-62 GPT Image 2超时/引流文角度差异化/不提客户公司名/真实图片vs概念图，共10条） |
| **2026-07-13 16表迁移踩坑** | Pitfalls #56-58（kunpeng/ai-gzh独立Base/v2取料逻辑/发布队列同步条件） |
| **2026-07-14 踩坑记录** | **`references/pitfalls-session-2026-07-14.md`**（#63-67：杂志感深色调/归藏配图风格/引流文默认路由/推草稿流程/Playwright中文文件名） |
| **v4 一句话公式（2026-07-17 新增）** | `references/v4-定位-1句话公式.md` |
| **5 段式结构 prompt（v4 新增）** | `references/5-段式结构-prompt.md` |
| **5 步引流动线钩子模板（v4 新增）** | `references/5-步引流动线-钩子模板.md` |
| **5 分词速查表（v4 新增）** | `references/5-分词速查表.md` |
| **标题 A/B 公式 v4（v4 新增）** | `references/标题AB公式-v4.md` |
| **27 篇知识库索引（v4 新增）** | `references/27-篇知识库索引.md` |
| **v4 产品阶梯 9.9/99/199/1999（v4 新增）** | `references/产品阶梯-9.9-99-199-1999.md` |
| **v6.1 范文（v4 新增）** | `references/v6.1-范文.md` |
| **重做版选题库 v4.1（2026-07-18 新增）** | `references/选题库-重做版-v4.1-第二批精选.md` |

## 文件结构

```
skills/ai-gzh-platform/
├── SKILL.md                        ← 本文件
├── config.example.json             ← 配置模板
├── config.json                     ← 用户配置
├── install.sh                      ← 一键安装脚本
├── references/                     ← 参考文档（42个 v4.1）
├── scripts/
│   ├── preflight.py                ← Phase 0 门禁检查
│   ├── init_config.py              ← 首次配置向导（v4.1 移除排版风格）
│   ├── generate_image.py           ← GPT Image 2 生成
│   ├── check_title_digest.py       ← 标题/摘要字节校验
│   ├── compress_images.py          ← PNG→JPG 压缩
│   ├── postflight.py               ← Phase 5 质量验证（v4.1: 1500-1800字+≤3行）
│   ├── push_draft.py               ← Phase 7 推草稿
│   ├── compose_from_text.py        ← Pillow 合成对比图
│   ├── assemble_atoms.py           ← 自动取料（00规则→13原子库）
│   ├── sync_publish_queue.py       ← 08→09 发布队列同步
│   └── wx-proxy.js                 ← 微信代理服务器
└── assets/examples/                ← 校准样图
```

## 师傅今日必查（v4 启动版）

每次写公众号文章前：

```
□ 1 分钟 读 references/v4-定位-1句话公式.md（确认写给 1 类生存画像）
□ 1 分钟 读 references/5-分词速查表.md（确认选题命中 5 分词）
□ 5 分钟 读完 references/5-段式结构-prompt.md（写时严格按 5 段）
□ 1 分钟 读 references/5-步引流动线-钩子模板.md（写文末前复制模板）
□ 30 分钟 写 article.md（严格卡 1500-1800 字）
□ 10 分钟 配图（封面 + 3 配图）
□ 5 分钟 HTML 生成 + Phase 5 Postflight
□ 5 分钟 发布 + 文末钩子粘贴
□ 1 分钟 09 库记录
```

总耗时约 60 分钟/篇。

## Pitfalls 速查（70条）

> **设计铁律**：所有需要用户替换/补充/确认的素材位统一用虚线框 + 醒目文字标签。
> **session级踩坑**：`references/pitfalls-session-2026-07-11.md`（#53-56 IMG_KEYWORDS/文件名/引流文路由/HTML截图，#59-60 GPT Image 2超时/引流文角度差异化）
> **session级踩坑**：`references/pitfalls-session-2026-07-14.md`（#63-67 杂志感深色调/归藏风格/引流文默认/推草稿流程/Playwright中文文件名）

1. **标题字节超限** → 写完立刻跑 `check_title_digest.py`
2. **execute_code 读不到 env** → 调脚本用 `terminal()` 不用 `execute_code`
3. **推草稿 HTML 不压缩** → 先 `compress_images.py` 转 JPG
4. **飞书 doc 一次写超50个block** → 按30/batch分批
5. **L1自检「这意味着」漏检** → `content.count(w)>0` 不是 `w in content`
6. **GPT Image 2 偶有英文字母混入** → 记录即可，不重生成
7. **只产一个HTML版本（v1/v2规则，v3已改变）** → v1/v2 永远产两个（微信粘贴版+推草稿版）。v3 默认 build_html.py 产出单文件 base64 内嵌 HTML，推草稿版按需额外生成。见 Pitfall #46。
8. **表头分隔行被渲染** → 过滤 `all(set(c)<=set("-: ") for c in row)`
9. **MiniMax Token Plan 2056** → vision 被阻塞时记录，不阻塞交付
10. **飞书 block_type 编号错误** → 查 `references/feishu-block-pitfall.md`
11. **WX_PROXY_SERVER 未设置** → `source .env && export WX_PROXY_SERVER`
12. **飞书资料包与公众号文章重复** → 资料包是补充材料，不是复制版
13. **飞书文档权限未开放** → 创建后设 `link_share_entity: anyone_readable`
14. **引导内容硬编码作者品牌名** → 发布前 `grep` 检查
15. **视觉规范未标注来源** → 区分"平台官方规则✅"vs"行业经验总结⚠️"
16. **多平台分发改尺寸不改内核** → 必须按平台原生语言重新讲述
17. **GPT Image 2 中文文字渲染不稳定** → AI生图只做纯视觉背景，文字用代码叠加
18. **generate_image.py 静默失败** → 直接用 requests 调 API 更可靠
19. **n8n-blogger 风格被混成 khazix-writer 语气** → 搜"我帮你""你团队里"，出现就改
20. **n8n 标题"没头没尾"** → 标题必须有「数字+时间+动作+结果」四要素
21. **AI 生图 API 单次请求超时常见** → background=true 跑图，串行 for 循环
22. **检查脚本意外修改源文件** → 检查脚本只读不写
23. **素材位分工没说清** → ≥3个 SCREENSHOT 时输出分工清单
24. **5 张图 base64 内嵌 ≈ 8MB** → 走 `feishu-send-attachment` 的 `msg_type=file`
25. **for 循环跑多张 AI 生图被 SIGTERM kill** → 单进程只跑1张图
26. **execute_code 沙盒无状态** → 每次都要重 import
27. **渠道/CTA 不反映用户当前状态** → 写 CTA 前用 clarify 确认
28. **多步交付中途反复问"完成了吗"** → 自推到底，只在真阻塞时停
29. **占位素材用微信号代替二维码** → 用蓝色边框块，不是 inline 文字
30. **用户截图截断** → Pillow 从源文字重排合成
31. **用户给的图必须全嵌** → 4步流程：盘点→分类→分配→全嵌
32. **push_draft.py 缺 import urllib.request** → 脚本顶部补齐
33. **推草稿验真阈值 chinese>1000 误杀** → 阈值改为 800
34. **PNG base64 接近 2MB 限制** → 推草稿版用相对路径，先 compress_images.py
35. **draft/get 不带 media_id 返回空数组** → 逐个传 media_id 拉
36. **vision_analyze 渲染 emoji 成方框** → fontconfig 问题，浏览器里正常
37. **CTA 变更必须同步所有产物** → article.md + 两个 HTML + 飞书资料包
38. **多步交付完成度 = 自我验证 + 单条汇报**
39. **md_to_html.py 不转换 markdown 图片语法** → 手动替换为 base64/相对路径
40. **md_to_html.py 无 --input/--output 参数** → 自动扫描 output/ 最新目录
41. **次幂数据 API 返回 data.items 非 data.articles**
42. **泛泛文章=废稿** → 写之前必须做真实素材调研，没有具体工具名/真实成本的文章用户一眼看出是AI编的
43. **postflight禁用词误报（2026-07-11 实测，修复待验证）** → 文章里列举禁用词本身（如「禁用词零命中：赋能/闭环/颠覆式」）会被 postflight.py 检出为命中。**修法**：① 写文章时不要在正文中直接列出禁用词，用「X/Y/Z等黑话」替代；② postflight.py 应在禁用词检查前先 `re.sub(r'```.*?```', '', content, flags=re.DOTALL)` 剥离代码块再检查。**⚠️ 注意**：v4 postflight.py 的禁用词检查目前仍检查原始 content，代码块剥离尚未应用——agent 下次改 postflight.py 时应顺手加上。
44. **「唯一」是禁用词（2026-07-11 实测）** → 「config.json是唯一真相来源」被 postflight 检出。改用「单一配置源」「核心配置源」。禁用词完整列表：赋能/闭环/颠覆式/颗粒度/抓手/底层逻辑/综上所述/值得注意的是/唯一/引领/颠覆。
45. **config.json字段迁移：brand_name → brand.brand_name（2026-07-11 v3升级）** → 旧版 config.json 用 `brand_name` 在根级别，新版用 `brand.brand_name` 嵌套。升级时 init_config.py 会自动迁移，但手动编辑 config.json 时注意不要混用新旧格式。
46. **v3单HTML是默认（2026-07-11 重新定义）** → Pitfall #7「永远产两个HTML」是v1/v2的规则。v3 默认 build_html.py 产出单文件 base64 内嵌 HTML（一个文件搞定）。推草稿版仍需额外生成（md_to_html.py 或 build_html.py --draft-mode），但不再是默认行为。
47. **snap chromium 渲染本地 HTML 必须走 HTTP（2026-07-11 实测）** → snap 安装的 chromium 拒绝 `file://` 协议（ERR_ACCESS_DENIED/ERR_FILE_NOT_FOUND），但能正常访问 `http://localhost:xxxx`。**修法**：`python3 -m http.server 8777 --bind 127.0.0.1` 起临时服务，chromium 访问 `http://127.0.0.1:8777/xxx.html`，截图完 `kill` 服务进程。此限制同样影响 agent-browser。见 pitfall #21。
48. **postflight 表格计数 bug（2026-07-11 实测）** → postflight.py 的表格行检测正则 `^\|.+\|$` 在某些 markdown 渲染器输出的表格中可能匹配不到（行首有空格、或表格行被包裹在其他标签中）。不影响核心验证（字数/禁用词/配图标记），但如果 postflight 报「0行数据」而文章实际有表格，先手动确认再信任脚本结果。
49. **引流文写成技术文档被用户否（2026-07-11 用户原话：「啥玩意 不行 太差了 效果」）** → 第一次写引流文时堆了脚本行数、代码细节、技术架构。用户说「不是 我是想用帮鲲鹏翼航定制公众号自动发布流程 做一个帮我自己引流的公众号内容」。**根因**：没区分「文章类型」。引流文的读者是企业老板，不关心技术实现。**修法**：① 写之前先判断文章类型（引流文/技术文/标准内容文）；② 引流文必须用 `references/lead-gen-article-guide.md`；③ 自检：读者看完会不会想「我也需要这个」？
50. **标题「数字暴击式」不适合引流文（2026-07-11 实测）** → 「7步替代13步」「1259行代码+42条踩坑」这种数字标题对技术人员有吸引力，但对企业老板没有。老板关心的是「我的公众号为什么停更」而不是「你用了几个脚本」。引流文标题用**场景式/痛点式**：「公众号停更3个月，不是因为没人写」「1个人管3个公众号，怎么做到的」。
51. **两种HTML风格混淆（2026-07-11 实测）** → 引流文和技术文的HTML效果截图应该用不同文章的。技术文用改造后的系统产出的HTML（展示排版效果），引流文用鲲鹏翼航等客户案例的HTML（展示服务成果）。截图前先确认用哪篇文章的HTML。
52. **snap chromium 截图必须走 HTTP 服务（2026-07-11 实测）** → 与 Pitfall #47 同源。截公众号HTML效果图时：① `python3 -m http.server 8777 --bind 127.0.0.1` 起临时服务；② `chromium --headless --no-sandbox --screenshot=/path.png --window-size=800,900 \"http://127.0.0.1:8777/path.html\"`；③ 截关键部分（标题区/表格区/配图区/CTA区），不用截全页；④ 截完 `kill` 服务进程。URL中的中文文件名需要先 `cp` 成英文名再访问。
53. **build_html.py IMG_KEYWORDS 缺配图5/6（2026-07-11 实测）** → IMG_KEYWORDS 字典只有配图1-4和正文素材，没有5和6的条目。后果：配图5和6的marker匹配不到对应图片文件，HTML里只有封面+配图1-4（5张），缺2张。**修法**：在 `scripts/build_html.py` 的 `IMG_KEYWORDS` 里补上 `"配图5"` 和 `"配图6"` 的关键词列表。**自检**：生成HTML后检查内嵌图片数是否等于配图marker数+1（封面），不等就是有漏匹配。此 bug 已在 2026-07-11 修复。
54. **图片文件名必须含「配图N」才能被编号精确匹配（2026-07-11）** → build_html.py 的 embed_image 先按编号匹配：从marker提取「配图N」→ 在IMG_KEYWORDS找关键词 → 在文件名里搜。如果文件名不含「配图N」也不含任何关键词，就匹配不上。**命名规范**：`配图N-<描述>.png`，如 `配图5-鲲鹏文章效果.png`、`配图6-Before-After对比.png`。
56. **kunpeng 和 ai-gzh 必须用独立 Base** → kunpeng 指向鲲鹏翼航无人机 Base（`Sfx7bgm...`），ai-gzh 指向大姚AI内容中台 16 表 Base（`TejybyBY...`）。绝不能把一个 skill 的 config 改成另一个的 Base——改完必须验证 `base_token` 和 `brand.company_name` 是否匹配。（2026-07-13 实测）

57. **assemble_atoms.py v2 从 13 表取料** → v1 从旧表按类型拉，v2 按 00 取料规则从 13 可独立取料原子库取。13 表原子有完整证据等级/使用边界/Hermes使用状态。取料逻辑：Hermes使用状态=可直接取料 + 证据等级 A/B + 按类型分组每种取1条确保多样性 + 至少1条边界原子。禁止只取单一类型。（2026-07-13 实测）

58. **sync_publish_queue.py 同步条件** → 从 08 精选生产池同步到 09 发布队列的条件：素材状态=可写 + 优先级含"P0" + 生产状态不是已入发布队列/已发布。同步后自动更新 08 表生产状态为"已入发布队列"。按标题防重复。（2026-07-13 实测）

55. **用户发的HTML文件要截图替换配图（2026-07-11 实测）** → 用户发来一个HTML文件说「应该是这份」，意思是配图5应该用这个文件的截图，不是之前截的别的文章。收到用户指定的HTML文件后：① 复制到 output 目录；② 起 HTTP 服务；③ chromium 截图；④ 替换对应配图文件；⑤ 重新生成 HTML。不要用「已经截好了」来跳过——用户指定的文件就是他想要的。

59. **小红书分发走独立skill（2026-07-13 实测）** → 公众号→小红书的分发不要用通用的多平台分发流程（aitoearn-multisite），要用专门的 `ai-xhs-platform` skill。通用流程的"改格式不改内核"不够——小红书需要6大公式、风格路由、postflight自动校验等独立逻辑。公众号长文写完后，Phase 8 触发"转小红书"时加载 `ai-xhs-platform`。

60. **16｜跨平台适配表是新增的第17张表（2026-07-13）** → 原16表Base新增了 `tblzd6LInkRTC2oh`（16｜跨平台适配表），用于存储公众号→各平台的适配内容。字段：来源选题(关联08)、目标平台、适配标题、适配正文、平台标签/话题、封面提示词、适配状态、发布链接、阅读/播放、点赞、收藏、评论、数据备注。09发布队列的"发布渠道"也已扩展为8个选项（+知乎/抖音/视频号/B站）。
63. **用户说「写公众号内容」时默认用引流文风格（2026-07-14 用户纠正）** → 用户说「先帮我写今天的工众号内容」，agent用了dayao实战复盘体，用户说「这篇不是用的我的那个引流的写的吗」。根因：风格路由决策表的默认路由写的是dayao-writing-prompt，但用户的公众号主要目的是引流获客。修法：默认路由改为lead-gen-writing-style，只有用户明确说「技术文/实战复盘」时才用dayao。
64. **配图必须用归藏材质插画风格（2026-07-14 用户纠正）** → 用通用GPT Image 2 prompt生成配图，用户说"生图的风格怎么也被修改了 按照之前的生图风格来啊 归藏的"。修法：生成配图前必须读取guizang-material-illustration skill的visual-style.md和prompt-patterns.md，按模板写prompt。
65. **模拟截图不行，必须真实系统截图（2026-07-14 用户纠正）** → 用HTML+CSS模拟飞书表格界面，用户说"这个真实截图效果不行"。修法：真实截图=Playwright截取实际运行的系统界面。HTML渲染→起HTTP服务+Playwright截图。中文文件名先cp成英文名。
66. **引流文正文质量要对齐历史最佳（2026-07-14 用户纠正）** → 用户说"正文内容好像没有7月11号哪篇写的好"。修法：写之前先读最近2-3篇的article.md，学习具体数字/案例展开/交付清单/角色价值。写完和历史文章对比。

68. **标题必须走4步流程（2026-07-16 新增）** → 以前只跑 check_title_digest.py 校验字节。v4 新增完整标题流程：① 读 title-formulas.md 选公式 → ② 用 AI 批量出题 Prompt 出 10 个标题 → ③ 过 5 问自检 → ④ 过字节校验。不要跳过直接写标题——标题决定打开率，投入产出比最高。

69. **信息峰值密度纳入写作硬约束（2026-07-16 新增）** → 每 300 字至少 1 个信息峰值（金句/数据/小案例/对比/反常识）。postflight v4 自动检查（Step 7，⚠️ 警告不阻断）。写作时主动每段自检，不要等 postflight 报警。详见 `references/information-density.md`。

70. **postflight v4 从 6 步扩展到 8 步（2026-07-16）** → 新增 Step 6（段落行距，阻断）和 Step 7（信息峰值密度，警告）。段落行距检查排除标题/表格/代码块/列表/引用块/配图标记，只检查正文段落。SKILL.md 的验证项从 6 条扩展到 8 条。
