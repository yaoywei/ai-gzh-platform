# 生图提示词模板

每张图单独生成。根据正文内容替换变量，不要把多张图拼在一起。

```text
Generate one standalone 16:9 horizontal Chinese article illustration.
Visual DNA:
Pure white background. Clean hand-drawn line art with slightly wobbly pen lines. Fresh, neat, friendly, product-sketch feeling. Lots of empty white space. Sparse handwritten Chinese annotations in warm orange, dark grey, and occasional red. Keep the illustration clear and lightweight, with a warm tech-builder and automation feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector poster style, no PPT infographic look, no childish chibi style, no realistic UI.
Recurring IP character required:
小姚 / Xiao Yao, a young Chinese male product architect and AI automation builder. He has spiky short black hair (炸毛短发), black square-frame glasses (黑框方眼镜), a warm-orange hoodie #F97316 (橙色卫衣), dark grey casual pants, white canvas sneakers, and a small wrench/data-line pin on his hoodie. He leans slightly forward with determined energy. 小姚 must perform the core conceptual action, not decorate the scene. Make 小姚 action-oriented, pragmatic, unstoppable, slightly stubborn but in a charming real-life way, and technically capable. Do not make him a generic anime boy, idol, mascot, child, or abstract creature.
Theme:
{正文配图主题}
Structure type:
{结构类型：Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}
Core idea:
{这张图要表达的核心意思}
Composition:
{具体画面：小姚在哪里、正在做什么、主要物件是什么、信息如何流动}
Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}
Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {标注词4} / {可选标注词5}
Color use:
Use black-brown for main line art, hair, and text. Use warm orange #F97316 for 小姚's hoodie, main flow arrows, and warm highlights. Use dark grey for pants, secondary elements, and system components. Use red only for key warnings/problems/results. Keep colors sparse and clean.
Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, dense explainer, commercial poster, or cute mascot page. Do not copy prior examples or reuse known case compositions unless explicitly requested; invent a fresh visual metaphor for this specific article. It should be clear but not instructional, friendly but not childish, clever but clean.
```

## 图像编辑提示

去掉左上角标题：
```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean white background, matching the surrounding blank paper. Preserve everything else exactly: character, labels, paths, line style, composition, aspect ratio, and image quality. Do not add any new text or objects.
```

增强角色参与感：
```text
Regenerate this illustration with the same core meaning and simple layout, but make 小姚 more central to the conceptual action. 小姚 should be doing the building, connecting, fixing, labeling, sorting, or deploying work that makes the idea visible, not standing beside the diagram. Preserve his key IP traits: square-frame glasses, spiky short black hair, warm-orange hoodie #F97316, dark grey casual pants, and white canvas sneakers. Keep it clean, sparse, hand-drawn, pragmatic, and not childish.
```
