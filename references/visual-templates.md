# 配图视觉模板

> 支持5种预设配图风格 + 自定义，通过config.json的`image_style`字段切换

## 风格选项速查

| 风格ID | 风格名称 | 特点 | 适用场景 |
|--------|----------|------|----------|
| `baoyu-notion` | Notion知识卡 | 圆润字体、圆角便签、低饱和蓝绿橙 | 通用干货、方法论、知识整理 |
| `xiaoyao-illustrations` | 小姚手绘配图 | 手绘线稿、纯白底、橙灰红批注、小姚IP | AI提效、自动化、工具链、系统搭建 |
| `flat-illustration` | 扁平插画 | 扁平矢量、色彩明快、图形简洁 | 生活、育儿、轻松话题 |
| `handdrawn-notes` | 手绘笔记 | 手写体+手绘图标+纸张质感 | 学习、教育、方法论 |
| `minimal-infographic` | 极简信息图 | 纯图标+数字+极简线条 | 数据、行业报告、专业分析 |
| `custom` | 自定义 | 用户自填style_prompt_prefix | 任意 |

## 风格一：Notion知识卡（默认）

### 风格基底

```
Notion-like editorial knowledge card, 轻松圆润字体版,
白底或极浅暖灰底、大留白,
黑灰主线、低饱和蓝/绿/橙点缀,
圆角卡片/便签/编辑批注/轻手绘圈注箭头,
手机端可读
```

## 封面图 Prompt 模板

```
生成一张横版Notion风格知识卡封面图，只需要一张。

主题：「{标题}」

结构：标题区占画面主视觉，标题文字巨大可读拼写完全正确，下方2-4个圆角便签标签以轻手绘箭头串联（{模块标签列表}），标签内容提炼自文章核心步骤/要点。

风格：Notion-like编辑知识卡+轻松圆润字体版，白底、大留白、黑灰主线、低饱和蓝绿橙点缀、圆角卡片/便签/编辑批注/轻手绘圈注箭头。

品牌标签：{brand_tag_position}「{brand_name}」

严禁：企业PPT、深色科技风、厚重商业海报、复杂3D、霓虹、高饱和渐变、英文/伪文字/乱码、普通白底素卡、moodboard、网格排版、展示板、样机、说明文字、过程稿、多余大段可读文字
```

### 变量说明

| 变量 | 说明 | 示例 |
|------|------|------|
| `{标题}` | 文章标题，完整填入 | 干了三年的基础岗，公司不招了 |
| `{模块标签列表}` | 2-4个核心步骤/要点，用→连接 | 初级岗消失→重新定价→转型路径 |
| `{brand_name}` | 品牌名，从config.json读取 | 你的品牌名 |
| `{brand_tag_position}` | 品牌标签位置 | 右下角 |

### 模块标签提炼规则

- 从文章正文提取2-4个核心步骤/要点
- 每个标签4-6个字，简洁有力
- 用→或箭头串联，体现流程/递进关系
- 颜色分配：第一个低饱和蓝/绿，中间低饱和蓝，最后一个暖橙

### 固定参数

- **size**：`1792x768`（2.35:1横版）
- **model**：从config.json读取image_api.model

### 重试规则

- 出现多余大段文字：追加「严格禁止在标题和标签之外添加任何可读文字」后重试
- 标题拼写错误：去掉问号/感叹号后重试
- 风格跑偏：追加「必须是白底Notion-like编辑知识卡风格，严禁深色背景、严禁3D光泽字体、严禁企业PPT风格」后重试

---

## 信息图 Prompt 模板

生成[主题：明确、具体]信息图，目标读者为[人群]。
结构：标题区 + 3-5个模块（每模块含图标、短标题、1-2句说明，模块间逻辑：可用箭头、颜色区分或连接线提示信息流或关系）。
图表类型：[流程图/对比图/关系图/时间线]。
风格：Notion-like 编辑知识卡 + 轻松圆润字体版，白底或浅灰底、大留白、黑灰主线、低饱和蓝/绿/橙点缀、圆角卡片/便签/编辑批注/轻手绘圈注箭头、手机端可读。
品牌标签：{brand_tag_position}「{brand_name}」
输出：信息层级清晰、可读性高的中文信息图。

严禁：企业PPT、深色科技风、厚重商业海报、复杂3D、霓虹、高饱和渐变、英文/伪文字/乱码

### JSON 进阶模板（推荐 Agent 调用）

```json
{
  "type": "Infographic",
  "topic": "[主题]",
  "audience": "[目标读者]",
  "structure": {
    "title_area": "[标题]",
    "layout": "[布局描述]",
    "modules": [
      {"title": "[模块1标题]", "icon": "[图标]", "text": "[1-2句说明]"},
      {"title": "[模块2标题]", "icon": "[图标]", "text": "[1-2句说明]"}
    ]
  },
  "style": {
    "aesthetic": "Notion-like editorial knowledge card, 轻松圆润字体版",
    "colors": "白底/极浅暖灰底，黑灰主线，低饱和蓝绿橙点缀",
    "background": "纯白或极浅暖灰"
  },
  "constraints": "禁止企业PPT、深色科技风、厚重商业海报、复杂3D、霓虹、高饱和渐变、英文/伪文字/乱码"
}
```

### 固定参数

- **size**：`1024x1820`（竖版，约1:1.8）
- **model**：从config.json读取image_api.model

### 避坑指南

- 控制模块数量：3-5个，多了画面混乱
- 文案克制：每模块1-2句，不把长段正文塞进画面
- 标签要短，组件关系要清楚

---

## 图片生成脚本

使用 `scripts/generate_image.py` 调用GPT Image 2 API：

```bash
python scripts/generate_image.py \
  --prompt "你的prompt内容" \
  --size "1792x768" \
  --output "imgs/cover-v2.png"
```

脚本从config.json读取API endpoint和model，从环境变量读取API Key。


---

## 风格二：小姚手绘配图（xiaoyao-illustrations）

> 基于Ian Xiaohei手绘线稿+小柠Illustrations框架改造，人形角色小姚为固定视觉IP
> 使用此风格时需先加载 `dayao-illustrations` 技能获取完整参考文件

### 风格基底

```
Pure white background, clean hand-drawn line art with slightly wobbly pen lines,
fresh neat friendly product-sketch feeling, lots of empty white space,
sparse handwritten Chinese annotations in warm orange, dark grey, and occasional red,
warm tech-builder and automation feeling,
no gradients, no shadows, no paper texture, no complex background,
no commercial vector poster style, no PPT infographic look,
no childish chibi style, no realistic UI
```

### 小姚IP核心特征（每张图必须包含）

```
小姚 / Xiao Yao, young Chinese male product architect and AI automation builder.
Spiky short black hair (炸毛短发), black square-frame glasses (黑框方眼镜),
warm-orange hoodie #F97316 (橙色卫衣), dark grey casual pants,
white canvas sneakers, small wrench/data-line pin on hoodie.
Leans slightly forward with determined energy.
小姚 must perform the core conceptual action, not decorate the scene.
```

### 正文配图 Prompt 模板

```
Generate one standalone 16:9 horizontal Chinese article illustration.
Visual DNA:
Pure white background. Clean hand-drawn line art with slightly wobbly pen lines. Fresh, neat, friendly, product-sketch feeling. Lots of empty white space. Sparse handwritten Chinese annotations in warm orange, dark grey, and occasional red. Keep the illustration clear and lightweight, with a warm tech-builder and automation feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector poster style, no PPT infographic look, no childish chibi style, no realistic UI.
Recurring IP character required:
小姚 / Xiao Yao, a young Chinese male product architect and AI automation builder. He has spiky short black hair (炸毛短发), black square-frame glasses (黑框方眼镜), a warm-orange hoodie #F97316 (橙色卫衣), dark grey casual pants, white canvas sneakers, and a small wrench/data-line pin on his hoodie. He leans slightly forward with determined energy. 小姚 must perform the core conceptual action, not decorate the scene. Make 小姚 action-oriented, pragmatic, unstoppable, slightly stubborn but in a charming real-life way, and technically capable. Do not make him a generic anime boy, idol, mascot, child, or abstract creature.
Theme:
{正文配图主题}
Structure type:
{结构类型}
Core idea:
{核心意思}
Composition:
{具体画面描述}
Suggested elements:
{元素1} / {元素2} / {元素3}
Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4}
Color use:
Use black-brown for main line art, hair, and text. Use warm orange #F97316 for 小姚's hoodie, main flow arrows, and warm highlights. Use dark grey for pants, secondary elements. Use red only for key warnings/problems/results. Keep colors sparse and clean.
Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, dense explainer, commercial poster, or cute mascot page. Invent a fresh visual metaphor.
```

### 封面图适配（小姚版）

```
生成一张横版手绘风格封面图，只需要一张。

主题：「{标题}」

结构：标题区占画面主视觉，标题文字手写风巨大可读拼写完全正确。画面右侧小姚正在操作与主题相关的工具（{小姚动作描述}），左侧留白区域放标题文字。下方2-4个手写标签用橙色箭头串联（{模块标签列表}）。

风格：纯白背景、清爽手绘线稿、大量留白、橙灰红手写批注。小姚穿橙色卫衣、黑框方眼镜、炸毛短发，正在做核心动作。

品牌标签：{brand_tag_position}「{brand_name}」

严禁：企业PPT、深色科技风、厚重商业海报、复杂3D、霓虹、高饱和渐变、英文/伪文字/乱码、幼稚可爱、流程图感
```

### 构图模式（8种）

| 类型 | 适用场景 | 小姚动作示例 |
|------|----------|-------------|
| Workflow | 输入→处理→输出 | 拉线连接系统模块 |
| 系统局部 | 3-5核心模块 | 接线/拧螺丝/贴标签 |
| 前后对比 | 混乱vs有序 | 左边烦右边搞定 |
| 角色状态 | 卡住→跑起来 | 四阶段连续动作 |
| 概念隐喻 | 工厂/机器/黑盒 | 操作手摇机器/修理 |
| 方法分层 | 框架/层级/栈 | 搭建/校准/贴标签 |
| 地图路线 | 路径/旅程 | 牵数据线沿路走 |
| 小漫画分镜 | 过程/吐槽 | 看报错→拆→接→跑 |

### 固定参数

- **size**：`1792x1024`（16:9横版，从config.json读取image_api.illustration_size）
- **model**：从config.json读取image_api.model
- **封面size**：`1792x768`（2.35:1横版，从config.json读取image_api.cover_size）

### QA检查要点

- ✅ 小姚有方形眼镜+炸毛短发+橙色卫衣+深灰裤子
- ✅ 小姚在做核心动作，不是装饰
- ✅ 纯白背景，大量留白
- ✅ 最多5-8个短中文标注
- ✅ 橙色为主强调色，红色仅用于问题/提醒
- ❌ 左上角有标题 → 局部编辑删除
- ❌ 小姚像普通二次元 → 强调product architect特征重试
- ❌ 太像PPT/流程图 → 换隐喻重新生成
