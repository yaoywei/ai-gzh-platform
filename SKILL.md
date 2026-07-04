---
name: ai-gzh-platform
description: AI公众号内容生产全平台技能。一键安装完整的公众号内容生产系统，包含选题调研、爆款分析、内容撰写(khazix-writer风格)、四层自检、配图生成(GPT Image 2，支持6种风格含小姚手绘)、HTML排版、推草稿到公众号、飞书资料包创建。当用户说安装公众号平台、搭建公众号系统、装公众号技能、配置AI公众号内容平台、写公众号文章、按SOP写内容、生产今天的公众号内容、走内容流程、写篇推文时触发。
version: 2.0.0
author: 大姚
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wechat, content, gpt-image,publishing, automation]
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
│   └── public-release-checklist.md  ← 公开仓库发布前隐私检查清单
├── scripts/
│   ├── init_config.py              ← 首次配置向导
│   ├── generate_image.py           ← GPT Image 2生成（含指数退避重试）
│   ├── push_draft.py               ← 微信推草稿（必须走 wx-proxy）
│   ├── compress_images.py          ← PNG→JPG 压缩
│   ├── check_title_digest.py       ← 标题/摘要字节校验（≤30B/≤54B）
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
- [ ] Step 5: 内容撰写 → article.md
      查上方「风格路由决策表」选风格文件。约1200字（n8n-blogger 风格1000-1500字）。
      写作硬规则：禁小标题/冒号/破折号/双引号(用「」)/emoji；口语化转场；CTA公式。
      **⚠️ execute_code 沙箱读不到 env** → 调 generate_image.py 必须用 terminal()。
- [ ] Step 6: 四层自检（必做）  → qa-report.md
      L1 禁用词+禁用标点零命中 | L2 口语化≥5词组 | L3 观点有支撑 | L4 像真人写的
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
- [ ] Step 10: HTML转换 → html/{slug}-微信粘贴版-v1.html + {slug}-推草稿版-v1.html
      双HTML模式（必做）：见 references/two-html-pattern.md
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
| 双HTML模式 | `references/two-html-pattern.md` |
| 推草稿踩坑 | `references/push-draft-pitfalls.md` |
| 双重UTF-8编码陷阱 | `references/push-draft-double-encoding-pitfall.md` |
| 常见 Live Failure | `references/live-failures.md` |
| n8n 工作流调试 | `references/n8n-integration-pitfalls.md` |
| 本地降级 HTML | `references/local-fallback-html-pack.md` |
| System Prompt 参考 | `references/system-prompt.md` |
| 公开仓库发布检查 | `references/public-release-checklist.md` |

## Pitfalls 速查

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

详见 `references/live-failures.md`

## 验收表

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