# Harness 迁移指南：从 Checklist 到脚本化门禁

> 当一个内容生产 skill 的 checklist 步骤超过 10 步、且 agent 每次都要手动跑每一步时，迁移到 Harness 模式。

## 迁移信号

- SKILL.md 有 10+ 步 checklist，agent 每次执行都要逐条过
- 质量检查（字数/禁用词/格式）靠 agent 人工判断，不是脚本自动验证
- HTML/输出文件有多个变体（粘贴版/推草稿版），逻辑散落在 SKILL.md 里
- 门禁检查（API key/依赖/配置）每次都是 agent 手动确认

## 迁移步骤

### 1. 提取门禁 → preflight.py

把 SKILL.md 中"开始前必须检查"的项目变成脚本：
- config 字段验证（必填/选填分别标记）
- API key 存在性检查（从 env 或 ~/.hermes/.env 读取）
- 外部工具依赖检查（lark-cli/ffmpeg/Pillow 等）
- 连通性测试（可选模块跳过而非失败）

输出：`✅/❌` 表格 + exit code 0/1。门禁不通过不执行。

### 2. 提取验证 → postflight.py

把"交付前自检"的项目变成脚本：
- 文章：字数/禁用词/双引号/表格数/配图标记数
- 图片：文件数/文件大小/命名规范
- HTML：文件存在/base64 内嵌数/文件大小
- 标题：字节校验（UTF-8 中文 3B/字）

输出：同 preflight 的 `✅/❌` 表格格式。

### 3. 合并输出 → build_html.py

如果有多种输出变体（粘贴版/推草稿版），统一到一个脚本：
- 读 config.json 的 style/template 配置
- 支持 base64 内嵌（单文件自包含）和相对路径（推草稿用）两种模式
- 图片自动匹配（按文件名关键词 → 配图标记映射）

### 4. 重写 SKILL.md

13步 checklist → 7 Phase 流程图 + 每个 Phase 的入口命令：
```
Phase 0: preflight.py      ← 脚本自动
Phase 1: 调研/选题          ← agent 决策
Phase 2: 写作              ← agent 执行
Phase 3: 配图              ← agent 执行
Phase 4: build_html.py     ← 脚本自动
Phase 5: postflight.py     ← 脚本自动
Phase 6: 交付              ← agent 执行
```

可选 Phase（推草稿/多平台分发）放在后面，不影响主流程。

### 5. 保留旧脚本

`md_to_html.py` 等旧脚本保留不删，标注"保留兼容"。新流程用 `build_html.py`。

## 关键设计决策

| 决策 | 选择 | 原因 |
|---|---|---|
| 配置来源 | config.json（不硬编码） | 新用户只改 config.json 即可 |
| 风格系统 | html_styles dict + style_name | 一个 build_html.py 支持 N 种风格 |
| 图片匹配 | 文件名关键词映射 | 简单可靠，不依赖 EXIF/metadata |
| 门禁失败 | exit 1 + 不执行 | agent 不需要判断，脚本说了算 |
| 旧脚本 | 保留不删 | 平滑过渡，不破坏已有流程 |
