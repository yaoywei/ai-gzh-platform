#!/usr/bin/env python3
"""
HTML 生成脚本：读取 article.md 和图片文件，生成 base64 内嵌的完整公众号 HTML。

特性：
  - 从 config.json 读取排版风格（10+1 种可选）
  - 所有图片 base64 内嵌，一个 HTML 文件搞定
  - 支持两种配图标记：【配图X：desc】（原子化）/ [SCREENSHOT: desc]（传统）
  - Markdown 完整渲染：标题/表格/引用/代码/列表/加粗/行内代码
  - 配图标记自动匹配 imgs/ 目录中的图片

用法：
  python3 build_html.py --article article.md --imgs-dir imgs/
  python3 build_html.py --article article.md --imgs-dir imgs/ --output html/xxx.html
  python3 build_html.py  # 自动扫描 output/ 最新目录
"""

import argparse
import base64
import io
import json
import os
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("错误：需要安装 Pillow。运行 pip install Pillow")
    sys.exit(1)

# ────────── 配置加载 ──────────
CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_style_colors(cfg: dict) -> dict:
    """从 config.json 读取当前排版风格的颜色配置"""
    style_name = cfg.get("html_template", {}).get("style_name", "kunpeng-blue")
    styles = cfg.get("html_styles", {})
    if style_name in styles:
        s = styles[style_name]
        return {
            "primary": s.get("primary", "#0057FF"),
            "accent": s.get("accent", "#0057FF"),
            "bg": s.get("bg", "#FFFFFF"),
            "name": s.get("name", style_name),
        }
    # fallback: 从 html_template 直接读
    ht = cfg.get("html_template", {})
    return {
        "primary": ht.get("primary_color", "#0057FF"),
        "accent": ht.get("accent_color", "#0057FF"),
        "bg": ht.get("background_color", "#FFFFFF"),
        "name": style_name,
    }


CFG = load_config()
COLOR = get_style_colors(CFG)
BRAND_NAME = CFG.get("brand", {}).get("brand_name", "")

# 通用颜色
TEXT = "#1F2937"
SUB = "#6B7280"
BORDER = "#E5E7EB"
SOFT_BG = "#F8FAFC"
CODE_BG = "#F1F5F9"

# ────────── 图片工具 ──────────


def img_to_base64(img_path, quality=80):
    """将图片转为 base64 JPEG"""
    img = Image.open(img_path)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, "#FFFFFF")
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode()


def find_image(imgs_dir, keyword):
    """在图片目录中查找匹配关键词的图片"""
    if not imgs_dir or not os.path.isdir(imgs_dir):
        return None
    for f in sorted(os.listdir(imgs_dir)):
        if keyword in f and f.lower().endswith((".png", ".jpg", ".jpeg")):
            return os.path.join(imgs_dir, f)
    return None


# 图片关键词映射：marker → 文件名关键词
IMG_KEYWORDS = {
    "封面": ["封面", "cover", "素材-封面"],
    "配图1": ["配图-1", "配图1", "pipeline", "流程"],
    "配图2": ["配图-2", "配图2", "cases", "数据", "案例", "薪资", "架构"],
    "配图3": ["配图-3", "配图3", "compare", "对比"],
    "配图4": ["配图-4", "配图4", "barriers", "门槛", "选题", "配方"],
    "配图5": ["配图-5", "配图5", "html", "效果", "preview"],
    "配图6": ["配图-6", "配图6", "before-after", "before", "after"],
    "正文素材": ["素材-正文", "正文"],
}


def embed_image(imgs_dir, keyword):
    """查找并嵌入图片"""
    # 先按编号精确匹配
    num_match = re.search(r"配图(\d+)", keyword)
    if num_match:
        num = num_match.group(1)
        kw_key = f"配图{num}"
        kw_list = IMG_KEYWORDS.get(kw_key, [])
        for f in sorted(os.listdir(imgs_dir)):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                if any(kw in f for kw in kw_list):
                    img_path = os.path.join(imgs_dir, f)
                    b64 = img_to_base64(img_path)
                    return f'<img src="data:image/jpeg;base64,{b64}" alt="{keyword}" style="max-width:100%;border-radius:8px;margin:24px 0;display:block;">\n'

    # 按关键词模糊匹配
    for kw_key, kw_list in IMG_KEYWORDS.items():
        if kw_key in keyword or any(kw in keyword for kw in kw_list):
            for kw in kw_list:
                img_path = find_image(imgs_dir, kw)
                if img_path:
                    b64 = img_to_base64(img_path)
                    return f'<img src="data:image/jpeg;base64,{b64}" alt="{keyword}" style="max-width:100%;border-radius:8px;margin:24px 0;display:block;">\n'
    return ""


# ────────── 占位符渲染 ──────────
SCREENSHOT_RE = re.compile(r"^\[SCREENSHOT:\s*(.+?)\]\s*$", re.MULTILINE)
AI_IMG_RE = re.compile(r"^\[AI-IMG:\s*(.+?)\]\s*$", re.MULTILINE)


def render_placeholder_box(text, kind="screenshot"):
    """占位提示框：截图位（橙虚线）vs AI 配图位（蓝虚线）"""
    if kind == "screenshot":
        return (
            f'<div style="margin:24px 0;padding:18px 20px;background:#FFFBEB;'
            f"border:1px dashed #F59E0B;border-radius:8px;color:#92400E;"
            f'font-size:14px;line-height:1.7;">'
            f'<div style="font-weight:600;margin-bottom:6px;">📷 待替换：截图位</div>'
            f'<div style="color:#78350F;">{text}</div></div>\n'
        )
    return (
        f'<div style="margin:24px 0;padding:18px 20px;background:#EFF6FF;'
        f"border:1px dashed #2563EB;border-radius:8px;color:#1E40AF;"
        f'font-size:14px;line-height:1.7;">'
        f'<div style="font-weight:600;margin-bottom:6px;">🎨 待生成：AI 配图位</div>'
        f'<div style="color:#1E3A8A;">{text}</div></div>\n'
    )


# ────────── Markdown 元素渲染 ──────────


def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_inline(text):
    text = escape_html(text)
    # **xxx** -> <strong>
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        rf'<strong style="color:{TEXT};font-weight:600;">\1</strong>',
        text,
    )
    # `xxx` -> <code>
    text = re.sub(
        r"`([^`]+)`",
        rf'<code style="background:{CODE_BG};padding:1px 6px;'
        rf"border-radius:4px;font-family:Menlo,Consolas,monospace;"
        rf'font-size:14px;color:{COLOR["primary"]};">\1</code>',
        text,
    )
    return text


def is_table_separator(row):
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    return all(re.match(r"^:?-+:?$", c) for c in cells if c)


def render_table(rows):
    rows = [r for r in rows if not is_table_separator(r)]
    if not rows:
        return ""
    html = [
        f'<table style="width:100%;border-collapse:collapse;margin:20px 0;'
        f"font-size:15px;line-height:1.6;background:#FFFFFF;"
        f'border:1px solid {BORDER};border-radius:6px;overflow:hidden;">'
    ]
    for i, row in enumerate(rows):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        tag = "th" if i == 0 else "td"
        if i == 0:
            style = (
                f'background:{COLOR["primary"]}10;color:{COLOR["primary"]};font-weight:600;'
                f"text-align:left;padding:10px 12px;"
                f"border-bottom:1px solid {BORDER};"
            )
        else:
            style = (
                f"padding:10px 12px;border-bottom:1px solid #F3F4F6;"
                f"color:{TEXT};"
            )
            if i % 2 == 0:
                style += "background:#F9FAFB;"
        row_html = "".join(
            f'<{tag} style="{style}">{render_inline(c)}</{tag}>' for c in cells
        )
        html.append(f"<tr>{row_html}</tr>")
    html.append("</table>")
    return "\n".join(html)


def render_quote(text):
    return (
        f'<blockquote style="margin:20px 0;padding:12px 16px;'
        f'background:{COLOR["primary"]}08;'
        f'border-left:3px solid {COLOR["primary"]};color:{COLOR["primary"]};'
        f'font-size:15px;line-height:1.7;border-radius:0 6px 6px 0;">'
        f"{render_inline(text)}</blockquote>\n"
    )


def render_list_items(items, ordered=False):
    tag = "ol" if ordered else "ul"
    style = "list-style:none;padding-left:0;margin:16px 0;"
    item_style = (
        f"padding:6px 0 6px 24px;position:relative;color:{TEXT};"
        f"font-size:15px;line-height:1.75;"
    )
    bullet_style = (
        f'position:absolute;left:6px;top:14px;width:6px;height:6px;'
        f'background:{COLOR["accent"]};border-radius:50%;'
    )
    if ordered:
        item_style = (
            f"padding:6px 0 6px 28px;position:relative;color:{TEXT};"
            f"font-size:15px;line-height:1.75;"
        )
        bullet_style = (
            f'position:absolute;left:6px;top:8px;color:{COLOR["accent"]};'
            f"font-weight:600;"
        )
    items_html = []
    for i, item in enumerate(items, 1):
        if ordered:
            items_html.append(
                f'<li style="{item_style}">'
                f'<span style="{bullet_style}">{i}.</span>'
                f"{render_inline(item)}</li>"
            )
        else:
            items_html.append(
                f'<li style="{item_style}">'
                f'<span style="{bullet_style}"></span>'
                f"{render_inline(item)}</li>"
            )
    return f'<{tag} style="{style}">{"".join(items_html)}</{tag}>\n'


def render_h1(text):
    return (
        f'<h1 style="font-size:24px;font-weight:700;color:{TEXT};'
        f'margin:32px 0 16px;line-height:1.4;'
        f'border-bottom:2px solid {COLOR["primary"]};padding-bottom:8px;">'
        f"{render_inline(text)}</h1>\n"
    )


def render_h2(text):
    return (
        f'<h2 style="font-size:20px;font-weight:700;color:{COLOR["primary"]};'
        f'margin:32px 0 14px;line-height:1.4;'
        f'padding-left:12px;border-left:4px solid {COLOR["primary"]};'
        f'">{render_inline(text)}</h2>\n'
    )


def render_h3(text):
    return (
        f'<h3 style="font-size:17px;font-weight:600;color:{TEXT};'
        f'margin:24px 0 12px;line-height:1.4;">'
        f"{render_inline(text)}</h3>\n"
    )


def render_code_block(text):
    return (
        f'<pre style="background:#1E293B;color:#E2E8F0;padding:16px 18px;'
        f"border-radius:8px;font-size:14px;line-height:1.6;overflow-x:auto;"
        f'margin:18px 0;font-family:Menlo,Consolas,monospace;">'
        f"{escape_html(text)}</pre>\n"
    )


def render_paragraph(text):
    return (
        f'<p style="margin:14px 0;font-size:15.5px;line-height:1.8;'
        f'color:{TEXT};letter-spacing:0.3px;">'
        f"{render_inline(text)}</p>\n"
    )


# ────────── 主转换 ──────────


def md_to_html(content, imgs_dir=None):
    """Markdown → HTML，支持完整 Markdown 语法 + 配图标记"""
    lines = content.split("\n")
    html_parts = []
    i = 0
    in_meta = False

    while i < len(lines):
        line = lines[i]

        # 「配图占位说明」section 之后停止渲染正文
        if line.startswith("## 📌"):
            in_meta = True
        if in_meta:
            i += 1
            continue

        # SCREENSHOT / AI-IMG 占位
        m_ss = SCREENSHOT_RE.match(line)
        m_ai = AI_IMG_RE.match(line)
        if m_ss:
            html_parts.append(render_placeholder_box(m_ss.group(1), "screenshot"))
            i += 1
            continue
        if m_ai:
            html_parts.append(render_placeholder_box(m_ai.group(1), "ai_img"))
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        # 分隔线
        if re.match(r"^-{3,}\s*$", line.strip()):
            html_parts.append(f'<hr style="border:none;border-top:1px solid {BORDER};margin:32px 0;">\n')
            i += 1
            continue

        # 配图标记 【配图X：desc】
        match = re.match(r"【配图(\d+)：(.+?)】", line.strip())
        if match:
            num = match.group(1)
            desc = match.group(2)
            if imgs_dir:
                img_html = embed_image(imgs_dir, f"配图{num}")
                if img_html:
                    html_parts.append(img_html)
                    html_parts.append(
                        f'<p style="font-size:14px;color:#999;text-align:center;'
                        f'margin-top:-16px;margin-bottom:24px;">▲ {escape_html(desc)}</p>\n'
                    )
                    i += 1
                    continue
            # 没找到图片，渲染为高亮提示
            html_parts.append(render_placeholder_box(f"配图{num}：{desc}", "ai_img"))
            i += 1
            continue

        # 标题
        if line.startswith("# ") and not line.startswith("## "):
            html_parts.append(render_h1(line[2:].strip()))
            i += 1
            continue
        if line.startswith("## "):
            html_parts.append(render_h2(line[3:].strip()))
            i += 1
            continue
        if line.startswith("### "):
            html_parts.append(render_h3(line[4:].strip()))
            i += 1
            continue

        # 引用
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and (lines[i].startswith("> ") or lines[i] == ">"):
                quote_lines.append(lines[i].lstrip("> ").rstrip())
                i += 1
            html_parts.append(render_quote(" ".join(quote_lines)))
            continue

        # 代码块
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            html_parts.append(render_code_block("\n".join(code_lines)))
            continue

        # 表格
        if "|" in line and i + 1 < len(lines) and is_table_separator(lines[i + 1]):
            table_rows = [line]
            i += 1
            while i < len(lines) and "|" in lines[i]:
                table_rows.append(lines[i])
                i += 1
            html_parts.append(render_table(table_rows))
            continue

        # 无序列表
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            html_parts.append(render_list_items(items, ordered=False))
            continue

        # 有序列表
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            html_parts.append(render_list_items(items, ordered=True))
            continue

        # 签名行
        if line.startswith("—— "):
            html_parts.append(
                f'<p style="margin:32px 0 8px;padding-top:20px;'
                f"border-top:1px dashed {BORDER};color:{SUB};"
                f'font-size:14px;text-align:right;">'
                f"{render_inline(line)}</p>\n"
            )
            i += 1
            continue

        # Markdown 图片引用 ![alt](path)
        img_match = re.match(r"!\[(.+?)\]\((.+?)\)", line.strip())
        if img_match and imgs_dir:
            alt = img_match.group(1)
            src = img_match.group(2)
            img_path = os.path.join(imgs_dir, src) if not os.path.isabs(src) else src
            if os.path.exists(img_path):
                b64 = img_to_base64(img_path)
                html_parts.append(
                    f'<img src="data:image/jpeg;base64,{b64}" alt="{escape_html(alt)}" '
                    f'style="max-width:100%;border-radius:8px;margin:24px 0;display:block;">\n'
                )
                i += 1
                continue

        # 图片说明
        if line.strip().startswith("▲"):
            html_parts.append(
                f'<p style="font-size:14px;color:#999;text-align:center;'
                f'margin-top:-16px;margin-bottom:24px;">{render_inline(line.strip())}</p>\n'
            )
            i += 1
            continue

        # 普通段落
        html_parts.append(render_paragraph(line))
        i += 1

    return "".join(html_parts)


# ────────── HTML 模板 ──────────


def make_full_html(title, body, cfg):
    """生成完整 HTML 文档"""
    brand = cfg.get("brand", {}).get("brand_name", "")
    footer_text = f"本文由「{brand}」原创" if brand else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape_html(title)}</title>
</head>
<body style="margin:0;padding:24px 18px;background:{SOFT_BG};
font-family:-apple-system,BlinkMacSystemFont,
'PingFang SC','Microsoft YaHei',
'Helvetica Neue',sans-serif;">
<div style="max-width:680px;margin:0 auto;background:{COLOR['bg']};
padding:32px 24px;border-radius:12px;
box-shadow:0 2px 8px rgba(0,0,0,0.04);">
{body}
{"<div style='margin-top:40px;padding:20px 0;border-top:1px dashed " + BORDER + ";text-align:center;color:#9CA3AF;font-size:13px;'>" + escape_html(footer_text) + "</div>" if footer_text else ""}
</div>
</body>
</html>
"""


# ────────── 入口 ──────────


def find_latest_output_dir():
    """找最新的 output/{date}-{slug} 目录"""
    base = Path(__file__).parent.parent / "output"
    if not base.exists():
        sys.exit(f"FAIL: {base} 不存在")
    subdirs = [p for p in base.iterdir() if p.is_dir()]
    if not subdirs:
        sys.exit(f"FAIL: {base} 下没有子目录")
    return max(subdirs, key=lambda p: p.stat().st_mtime)


def main():
    parser = argparse.ArgumentParser(description="生成公众号HTML（base64内嵌图片）")
    parser.add_argument("--article", help="article.md 路径")
    parser.add_argument("--imgs-dir", help="图片目录路径")
    parser.add_argument("--output", help="输出 HTML 路径")
    args = parser.parse_args()

    # 自动查找
    if args.article:
        article_path = Path(args.article).resolve()
        imgs_dir = Path(args.imgs_dir).resolve() if args.imgs_dir else article_path.parent / "imgs"
    else:
        out_dir = find_latest_output_dir()
        article_path = out_dir / "article.md"
        imgs_dir = out_dir / "imgs"

    if not article_path.exists():
        sys.exit(f"FAIL: {article_path} 不存在")

    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取标题
    title_match = re.match(r"# (.+)", content)
    title = title_match.group(1) if title_match else "公众号文章"

    # 取正文（不含元信息）
    meta_idx = content.find("## 📌")
    if meta_idx > 0:
        body_content = content[:meta_idx].rstrip()
        body_content = re.sub(r"\n---\s*$", "", body_content)
    else:
        body_content = content

    # 封面图（在第一个 h2 之前插入）
    cover_path = find_image(str(imgs_dir), "封面") if imgs_dir and imgs_dir.exists() else None
    cover_html = ""
    if cover_path:
        b64 = img_to_base64(cover_path)
        cover_html = (
            f'<img src="data:image/jpeg;base64,{b64}" alt="封面" '
            f'style="max-width:100%;border-radius:8px;margin:24px 0;display:block;">\n'
            f'<p style="font-size:14px;color:#999;text-align:center;'
            f'margin-top:-16px;margin-bottom:24px;">▲ 封面</p>\n\n'
        )

    # 转换
    body_html = md_to_html(body_content, str(imgs_dir) if imgs_dir and imgs_dir.exists() else None)

    # 在第一个 h2 之前插入封面
    if cover_html:
        first_h2 = body_html.find("<h2")
        if first_h2 > 0:
            first_p_end = body_html.find("</p>")
            if first_p_end > 0:
                insert_pos = first_p_end + len("</p>")
                body_html = body_html[:insert_pos] + "\n\n" + cover_html + body_html[insert_pos:]

    full_html = make_full_html(title, body_html, CFG)

    # 输出
    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = article_path.parent / "html"
        output_dir.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^\w\u4e00-\u9fff-]", "", title)[:20]
        output_path = output_dir / f"公众号-{slug}-完整版.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    size_kb = os.path.getsize(output_path) // 1024
    img_count = len(re.findall(r"data:image/jpeg;base64,", full_html))
    print(f"✅ {output_path.name} ({size_kb}KB, {img_count}张内嵌图)")
    print(f"   路径: {output_path}")


if __name__ == "__main__":
    main()
