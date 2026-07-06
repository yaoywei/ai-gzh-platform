# 微信原生 HTML 模板（推草稿版专用）

> 推草稿版 HTML 必须用微信原生格式（**全行内样式 + 微信支持的标签**），不能复用 `md_to_html.py` 产出的浏览器版。
>
> 详见 `references/push-draft-pitfalls.md` 坑 10。

## 什么时候用

Step 10 产第二个 HTML 时用本模板（`{slug}-推草稿版-v1.html`）。

第一个 HTML（`{slug}-微信粘贴版-v1.html`）继续用 `md_to_html.py` —— 浏览器版样式只在用户自己浏览器里看时才有效，推到微信草稿箱会丢样式。

## 核心规则（必满足 4 条）

1. **全内联样式**：每个元素自己写 `style="..."`
2. **无 `<style>` 块**：head 里的 `<style>` 全部移到 body style 或每个元素
3. **无 `class=""` / `id=""`**：用纯结构化标签
4. **`src` 不能用 `data-src`**：直接 `<img src="...">`

## 完整 transform 代码

```python
import re
from pathlib import Path

def md_to_wechat_native(md: str, img_jpg_dir: str = "imgs/jpg") -> str:
    """Markdown → 微信原生 HTML（行内 style + 微信支持的标签）

    img_jpg_dir: 推草稿版图片相对路径目录（push_draft.py 会替换为 CDN URL）
    """
    # 1. SCREENSHOT → 虚线占位（行内 style 块，微信原生 p 标签）
    def sshot_repl(m):
        desc = m.group(1).strip()
        short = desc[:30] + ("..." if len(desc) > 30 else "")
        return (
            f'<p style="margin: 12px 0; padding: 12px; border: 2px dashed #f59e0b; '
            f'border-radius: 6px; background-color: #fffbeb; font-size: 14px; '
            f'color: #78350f; line-height: 1.6;">'
            f'<span style="color: #b45309; font-weight: 600; font-size: 13px; '
            f'display: block; margin-bottom: 6px;">📸 待补充：{short}</span>'
            f'{desc}'
            f'</p>'
        )
    md = re.sub(r'\[SCREENSHOT:\s*([^\]]+)\]', sshot_repl, md)

    # 2. 图片占位（AI-IMG/USER-IMG）→ markdown 图片语法
    md = re.sub(
        r'\[AI-IMG:\s*风格学习前后对比[^\]]+\]',
        f'\n![风格学习前后对比]({img_jpg_dir}/step3-style-compare.jpg)\n',
        md,
    )
    md = re.sub(
        r'\[USER-IMG:\s*飞书机器人推送成功日志[^\]]+\]',
        f'\n![推草稿日志]({img_jpg_dir}/push-log.jpg)\n', md,
    )
    md = re.sub(
        r'\[USER-IMG:\s*完整交付清单[^\]]+\]',
        f'\n![交付清单]({img_jpg_dir}/delivery-list.jpg)\n', md,
    )
    md = re.sub(
        r'\[USER-IMG:\s*飞书资料包主图[^\]]+\]',
        f'\n![资料包主图]({img_jpg_dir}/feishu-package.jpg)\n', md,
    )
    md = re.sub(
        r'\[USER-IMG:\s*飞书资料包封面卡片[^\]]+\]',
        f'\n![资料包封面]({img_jpg_dir}/feishu-cover.jpg)\n', md,
    )
    md = re.sub(r'\n*\[AI-IMG:[^\]]+\]\n*', '\n', md)

    # 3. Step 1-4 标题后插入对应 jpg 图
    md = re.sub(r'(### Step 1：[^\n]+)', rf'\1\n\n![Step 1]({img_jpg_dir}/01.jpg)\n', md)
    md = re.sub(r'(### Step 2：[^\n]+)', rf'\1\n\n![Step 2]({img_jpg_dir}/02.jpg)\n', md)
    md = re.sub(r'(### Step 4：[^\n]+)', rf'\1\n\n![Step 4]({img_jpg_dir}/04.jpg)\n', md)
    md = re.sub(r'!\[小姚 IP\]\([^)]+\)\n*', '', md)

    # 4. 微信号块
    md = md.replace(
        '微信号：**Yao934025938**',
        '<p style="display: block; background-color: #f0f7ff; border: 2px solid #2563EB; '
        'border-radius: 6px; padding: 12px 16px; margin: 16px 0; color: #2563EB; '
        'font-size: 17px; font-weight: 600;">微信号：<strong>Yao934025938</strong></p>'
    )

    # 5. Markdown → 微信原生 HTML（行内 style）
    lines = md.split('\n')
    out = []
    table_rows = []

    def flush_table():
        if not table_rows: return ''
        sep_idx = -1
        for i, r in enumerate(table_rows):
            if all(re.match(r'^[-:]+$', c.strip()) for c in r):
                sep_idx = i
                break
        if sep_idx == -1:
            sep_idx = 1
        headers = table_rows[0]
        body = table_rows[sep_idx + 1:]
        html = (
            '<table style="width: 100%; border-collapse: collapse; margin: 16px 0; '
            'font-size: 14px; background-color: #ffffff; border: 1px solid #e5e7eb; '
            'border-radius: 4px;">'
        )
        html += (
            '<tr>' + ''.join(
                f'<th style="padding: 8px 10px; border-bottom: 1px solid #e5e7eb; '
                f'text-align: left; background-color: #f9fafb; font-weight: 600;">{c.strip()}</th>'
                for c in headers
            ) + '</tr>'
        )
        for row in body:
            html += (
                '<tr>' + ''.join(
                    f'<td style="padding: 8px 10px; border-bottom: 1px solid #e5e7eb; '
                    f'text-align: left;">{c.strip()}</td>'
                    for c in row
                ) + '</tr>'
            )
        html += '</table>'
        return html

    i = 0
    in_list = None
    while i < len(lines):
        line = lines[i]
        # 图片语法 ![alt](path)
        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if img_match:
            if in_list: out.append(f'</{in_list}>'); in_list = None
            alt = img_match.group(1)
            path = img_match.group(2)
            out.append(
                f'<img src="{path}" style="display: block; width: 100%; max-width: 100%; '
                f'height: auto; margin: 12px 0; border-radius: 8px;"/>'
            )
            i += 1
            continue
        # 表格
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if in_list: out.append(f'</{in_list}>'); in_list = None
            cells = [c for c in line.strip().strip('|').split('|')]
            table_rows.append(cells)
            i += 1
            continue
        else:
            if table_rows:
                out.append(flush_table())
                table_rows = []
        if line.strip() == '---':
            if in_list: out.append(f'</{in_list}>'); in_list = None
            out.append('<hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;"/>')
        elif line.startswith('# '):
            if in_list: out.append(f'</{in_list}>'); in_list = None
            out.append(
                f'<h1 style="font-size: 24px; font-weight: 700; color: #2563EB; '
                f'margin: 16px 0 12px; line-height: 1.4; text-align: center;">{line[2:].strip()}</h1>'
            )
        elif line.startswith('## '):
            if in_list: out.append(f'</{in_list}>'); in_list = None
            out.append(
                f'<h2 style="font-size: 19px; font-weight: 700; color: #1f2329; '
                f'margin: 24px 0 10px; padding-left: 10px; border-left: 4px solid #F97316;">{line[3:].strip()}</h2>'
            )
        elif line.startswith('### '):
            if in_list: out.append(f'</{in_list}>'); in_list = None
            out.append(
                f'<h3 style="font-size: 17px; font-weight: 600; color: #2563EB; '
                f'margin: 18px 0 8px;">{line[4:].strip()}</h3>'
            )
        elif line.startswith('> '):
            if in_list: out.append(f'</{in_list}>'); in_list = None
            out.append(
                f'<blockquote style="background-color: #f0f7ff; border-left: 3px solid #2563EB; '
                f'padding: 10px 14px; margin: 12px 0; color: #4b5563; font-size: 15px; '
                f'border-radius: 0 4px 4px 0;">{line[2:].strip()}</blockquote>'
            )
        elif line.startswith('- '):
            if in_list != 'ul':
                if in_list: out.append(f'</{in_list}>')
                out.append('<ul style="margin: 8px 0 8px 20px; padding-left: 8px;">')
                in_list = 'ul'
            out.append(f'<li style="margin: 4px 0; color: #1f2329;">{line[2:].strip()}</li>')
        elif re.match(r'^\d+\.\s', line):
            if in_list != 'ol':
                if in_list: out.append(f'</{in_list}>')
                out.append('<ol style="margin: 8px 0 8px 20px; padding-left: 8px;">')
                in_list = 'ol'
            content = re.sub(r'^\d+\.\s', '', line).strip()
            out.append(f'<li style="margin: 4px 0; color: #1f2329;">{content}</li>')
        elif line.strip() == '':
            if in_list: out.append(f'</{in_list}>'); in_list = None
        else:
            if in_list: out.append(f'</{in_list}>'); in_list = None
            out.append(
                f'<p style="margin: 8px 0; color: #1f2329; line-height: 1.75;">{line.strip()}</p>'
            )
        i += 1
    if in_list: out.append(f'</{in_list}>')
    if table_rows: out.append(flush_table())

    html = '\n'.join(out)
    # 行内格式
    html = re.sub(
        r'\*\*(.+?)\*\*',
        r'<strong style="color: #1f2329; font-weight: 600;">\1</strong>',
        html,
    )
    html = re.sub(
        r'`([^`]+)`',
        r'<code style="background-color: #f3f4f6; padding: 1px 6px; border-radius: 3px; '
        r'font-size: 14px; color: #2563EB;">\1</code>',
        html,
    )
    html = re.sub(r'(</blockquote>)\s*<blockquote', r'\1<br/><blockquote', html)
    return html


def wrap_wechat_html(body_html: str) -> str:
    """包成完整 HTML（无 <style> 块，body 自身带 style）"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>公众号文章</title>
</head>
<body style="font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; max-width: 720px; margin: 0 auto; padding: 20px 16px 40px; background-color: #fafafa; color: #1f2329; line-height: 1.75; font-size: 16px;">

{body_html}

</body>
</html>'''


# ============ 使用方法 ============
if __name__ == "__main__":
    from pathlib import Path
    art = Path("output/<date>-<slug>/article.md")
    body = art.read_text().split("## 📌 配图占位说明")[0].rstrip()
    body_html = md_to_wechat_native(body, img_jpg_dir="imgs/jpg")
    out_html = wrap_wechat_html(body_html)

    out = Path("output/<date>-<slug>/html/<slug>-推草稿版-v1.html")
    out.write_text(out_html, encoding="utf-8")
    print(f"✅ 推草稿版: {out} ({out.stat().st_size / 1024:.1f} KB)")

    # 验证
    checks = {
        "无 <style>": "<style" not in out_html,
        "无 class=": 'class="' not in out_html,
        "无 data-src": "data-src" not in out_html,
        "有 src=imgs/": 'src="imgs/' in out_html,
    }
    for k, v in checks.items():
        print(f"  {'✅' if v else '❌'} {k}")
```

## 关键差异点速查

| 元素 | 浏览器版（粘贴版 OK）| 推草稿版（必须）|
|---|---|---|
| 样式位置 | `<style>` 块 + class | 每个元素 `style="..."` |
| 虚线占位 | `<div class="sshot">` | `<p style="border: 2px dashed #f59e0b; ...">` |
| 微信号块 | `<span class="wechat-id">` | `<p style="background: #f0f7ff; border: 2px solid #2563EB; ...">` |
| 图片 | `<img data-src="...">` | `<img src="...">` |
| 表格 | `<table><thead><tbody>` | `<table>` 扁平，th/td 各自 style |
| H1 居中 | `text-align: center` 写在 CSS | 直接 `style="text-align: center;"` 内联 |

## 推完必跑验证

```bash
python3 -c "
content = open('output/<date>-<slug>/html/<slug>-推草稿版-v1.html').read()
checks = {
    '无 <style>': '<style' not in content,
    '无 class=': chr(34) + 'class=' + chr(34) not in content,
    '无 data-src': 'data-src' not in content,
    '有 src=imgs/': 'src=' + chr(34) + 'imgs/' in content,
}
for k, v in checks.items():
    print(f\"  {'✅' if v else '❌'} {k}\")
"
```

## 故障排查

| 现象 | 原因 | 修法 |
|---|---|---|
| 虚线框变普通段落 | 用了 `<div class="sshot">` | 改成 `<p style="border: 2px dashed #f59e0b; ...">` |
| 微信号块变普通文字 | 用了 `<span class="wechat-id">` | 改成 `<p style="background: #f0f7ff; border: 2px solid #2563EB; ...">` |
| 图片不显示 | 用了 `<img data-src="...">` | 改成 `<img src="...">` |
| 表格丢边线 | 用了 `<thead><tbody>` 嵌套 | 改扁平 `<table>`，th/td 各自 style |
| 整体散架 | 用了 `<style>` 块 + class | 把所有 CSS 移到每个元素的 `style="..."` |
| **列表项之间多空 `●`** | 用了 `<ul><li>...</li></ul>` | 改用 `<p>● 内容</p>` + position absolute |
| **数字列表项之间多空 `1.`** | 用了 `<ol><li>...</li></ol>` | 改用 `<p>1. 内容</p>` + position absolute |
| **表格错乱/挤压** | 微信对 `<thead>/<tbody>` 嵌套处理不一致 | 改"卡片化"：表头 `<p>━━━ A | B | C ━━━</p>` + 行 `<p style="background:...">A | B | C</p>` |
| 字号偏小 | CSS 14-15px | 调 16-17px；line-height 调 2 |
| **行高紧** | line-height 1.75 | 调 2 |
| 推草稿脚本删不掉坏草稿 | `urllib` 未 import，NameError | 在 `scripts/push_draft.py` L4 加 `import urllib.request` |
| 推草稿误报"中文 < 1000" | 阈值硬卡 1000，图片替换后正常就是 800-1100 | 改阈值到 800（在 `verify_draft` L90） |

## ⚠️ 关键反例（2026-07-06 实测踩坑）

### ❌ 绝对不能用的 HTML 写法（推草稿版）

```html
<!-- ❌ 微信会在每个 li 之间插入空 li -->
<ul>
  <li>选题</li>
  <li>写稿</li>
</ul>

<!-- ❌ 微信对 thead/tbody 嵌套处理不一致 -->
<table>
  <thead><tr><th>环节</th></tr></thead>
  <tbody><tr><td>选题</td></tr></tbody>
</table>

<!-- ❌ 微信对 h1 居中支持差 -->
<h1 style="text-align: center;">标题</h1>
```

### ✅ 正确的替代写法

```html
<!-- ✅ 用 p + ● 字符模拟列表 -->
<p style="margin: 6px 0; padding: 2px 0 2px 20px; position: relative; line-height: 2;">
  <span style="position: absolute; left: 0; color: #F97316; font-weight: 700;">●</span>
  选题：让 AI 拉爆款库、按行业出候选
</p>

<!-- ✅ 数字列表用 p + 数字 -->
<p style="margin: 6px 0; padding: 2px 0 2px 28px; position: relative; line-height: 2;">
  <span style="position: absolute; left: 0; color: #2563EB; font-weight: 700;">1.</span>
  把最近 30 篇 10W+ 文章打包 PDF
</p>

<!-- ✅ 表格改"卡片化" -->
<p style="font-size: 15px; font-weight: 600; margin: 16px 0 6px;">━━━ 环节 | 人工 | AI 化 ━━━</p>
<p style="margin: 4px 0; padding: 8px 12px; background-color: #fafafa; border-left: 3px solid #2563EB;">选题 | 刷竞品 | AI 拉爆款库</p>
```

## 字号规范

| 元素 | 推荐尺寸 | 行高 |
|---|---|---|
| H1（标题） | 22-24px | 1.5 |
| H2（章节） | 19-20px | 1.5 |
| H3（小节） | 17-18px | 1.5 |
| 正文 | 16-17px | 2.0（不要 1.75，太紧）|
| 列表项 | 16px | 2.0 |
| 引用块 | 15-16px | 1.8 |
| 虚线占位说明 | 14-15px | 1.8 |

## 关联

- **规则源头**：`references/two-html-pattern.md`（双 HTML 模式总览）
- **踩坑记录**：`references/push-draft-pitfalls.md` 坑 10/11/12（2026-07-06 实测）
- **对接脚本**：`scripts/push_draft.py`（已修：import urllib + 阈值 800）
