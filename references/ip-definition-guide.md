# 自定义 IP 形象定义引导（5 步法）

> 来源：用户公众号文章《我把开源的小黑配图 Skill，改成了我自己的 IP 风格》
> 方法论：做 AI 配图不是写一个万能 prompt，而是搭一套视觉生产体系。

## 什么时候触发

用户在首次配置 Phase 0c 选了 `custom-ip` 配图风格时，或者用户主动说"我想定义自己的 IP 形象 / 我要自己的配图角色 / 帮我做一个 IP"时。

## 核心理念

不是写一句 prompt，而是搭一整套视觉规则：IP 设定 + 风格 DNA + prompt 模板 + 构图规则 + 校准样图。

参考实现：小姚 IP（`references/xiaoyao-ip.md` + `style-dna.md` + `prompt-template.md` + `composition-patterns.md` + `assets/examples/` 5 张校准图）。

## 5 步流程

### Step 1: 拆结构（agent 自动完成，不问用户）

先让 agent 读现有的小姚 IP 体系，理解一个好的配图 Skill 由几部分组成：

```
SKILL.md          → 定义 Skill 干什么、什么时候用
IP 设定文件        → 角色长什么样、性格是什么、在图里做什么
风格 DNA           → 画面是白底、手绘、清爽、还是科技感
prompt 模板        → 真正生成图片时的提示词
构图规则           → 角色怎么参与画面、图怎么组织
QA 检查            → 生成后判断图片是否跑偏
校准样图           → 5-8 张覆盖不同场景的参考图
```

agent 读完这些文件后，就知道接下来要帮用户生成什么。

### Step 2: 定义 IP 角色（跟用户交互收集）

用 clarify 逐步问，每个问题给推荐选项 + "其他"：

**第 1 问：性别 + 职业**
- 选项：`男/产品架构师` / `女/程序员` / `女/运营人` / `男/设计师` / `其他`
- 这个决定角色的整体气质和动作类型

**第 2 问：外形识别点 3-5 个**
- 提示用户："想想你的 IP 角色长什么样？给 3-5 个关键特征，别人看到这些特征就能认出你的角色。"
- 例子：
  - 小姚：黑色炸毛短发 + 黑色方形框眼镜 + 暖橙色卫衣 #F97316 + 深灰休闲裤 + 白帆布鞋
  - 小柠：圆框眼镜 + 双麻花辫 + 柠檬黄衬衫 + 牛仔背带裤 + 蓝色发夹
- **关键**：这些识别点越多出现在图里，IP 识别度越高

**第 3 问：主色调**
- 选项：`暖橙#F97316` / `柠檬黄` / `科技蓝#2563EB` / `薄荷绿` / `玫瑰红` / `其他`
- 主色调用于角色服装 + 画面重点元素 + 箭头/流程线

**第 4 问：性格关键词 3-5 个**
- 引导："你的 IP 是什么性格？这决定它在图里的表情和动作气质。"
- 例子：
  - 小姚：强执行、停不下来、先跑起来再说、务实干练、有点倔
  - 可选推荐：`务实/强执行/幽默` / `温暖/细腻/有耐心` / `酷/极简/不废话` / `活泼/好奇/爱折腾` / `其他`

**第 5 问：常用道具 3-5 个**
- 引导："你的 IP 在图里会用什么工具？这决定它在画面里的动作类型。"
- 例子：
  - 小姚：扳手、螺丝刀、数据线、便签、工具箱、笔记本电脑
  - 可选推荐：`笔记本电脑/便签/数据线` / `咖啡杯/手机/笔记本` / `画笔/调色板/设计稿` / `其他`

→ agent 收集完 5 个答案后，自动生成 `references/my-ip.md`。

### Step 3: 写生图 prompt 模板（agent 自动生成）

基于用户 IP 定义，照 `prompt-template.md` 的格式生成 `references/my-ip-prompt.md`。

**核心技巧（用户文章原文）**：
- 角色外形尽量用**英文**写清楚 → 稳定视觉描述
- 中文标签保持**短**一点 → 画面里不乱
- 英文负责："Xiao Ning is a young Chinese IT professional female, with round-frame glasses, twin braids, blue hair clip, lemon yellow shirt, denim overalls."
- 中文负责：需求调研、测试联调、上线发布

模板结构（照小姚 prompt-template.md 改）：
```
Generate one standalone 16:9 horizontal Chinese article illustration.
Visual DNA:
{风格 DNA，照 my-style-dna.md}
Recurring IP character required:
{IP 英文名}, {英文外形描述}. {性格描述}. {禁止画成什么样}.
Theme:
{正文配图主题}
Structure type:
{结构类型}
Core idea:
{这张图要表达的核心意思}
Composition:
{具体画面}
Chinese handwritten labels:
{标注词}
Color use:
{颜色使用规则}
Constraints:
{构图约束}
```

### Step 4: 改构图规则（agent 自动生成）

基于用户 IP 的职业和性格，生成适合的动作池和构图模式。

**动作池生成规则**：
- 程序员 → 写代码、修 bug、贴便签、整理需求、连接模块、调参数、看数据
- 产品经理 → 画原型、拆需求、接线、推模块、给模块编号
- 设计师 → 画稿、调色、排版、比稿、改稿
- 运营人 → 贴标签、整理数据、看趋势、接用户反馈
- 通用 → 建、连、拆、接、推、拧、贴、标、查、修、叠、部署、递出

照 `composition-patterns.md` 的 8 种构图类型，根据 IP 职业微调，生成 `references/my-composition-patterns.md`。

### Step 5: 生成校准样图

用 image API 生成 5-8 张校准样图，覆盖：
1. 正面站姿（展示完整外形）
2. 侧面动作（展示动作气质）
3. 坐姿工作场景
4. 核心 IP 动作（最能代表职业的动作）
5. 复杂构图（多元素场景）
6. 极简构图（单一动作 + 大量留白）

每张图先写 prompt file 到 `prompts/`，再调 `generate_image.py` 生成，存到 `assets/examples/`。

**这些样图不是炫技，是视觉校准**。以后继续生成图片时，就有明确的参考方向。

## 完成检查清单

生成完用户 IP 后，agent 做一次完整检查：
- [ ] `references/my-ip.md` 存在且含角色定义/外形/颜色/性格/道具/禁止
- [ ] `references/my-ip-prompt.md` 存在且含完整 prompt 模板
- [ ] `references/my-composition-patterns.md` 存在且含动作池和构图模式
- [ ] `assets/examples/` 有 5+ 张校准样图
- [ ] prompt 模板没有残留小姚/小黑的角色特征
- [ ] 中文标签短（2-8 字）
- [ ] 英文外形描述清晰稳定
- [ ] 样图都是 16:9 横版
- [ ] IP 在每张图里都承担核心动作（不是站旁边看）

## 给用户的交付报告

```
✅ 你的 IP 形象已定义

## 你的 IP
| 项 | 值 |
|---|---|
| 名字 | {用户给的名字或 agent 建议的} |
| 职业 | {性别+职业} |
| 识别点 | {3-5个外形特征} |
| 主色调 | {颜色} |
| 性格 | {3-5个关键词} |
| 道具 | {3-5个常用道具} |

## 生成的文件
- references/my-ip.md（IP 设定）
- references/my-ip-prompt.md（prompt 模板）
- references/my-composition-patterns.md（构图规则）
- assets/examples/（N 张校准样图）

## 从此以后
你的公众号配图会稳定生成带有你 IP 形象的正文配图，不再每次从零乱画。
```