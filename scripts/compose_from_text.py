#!/usr/bin/env python3
"""
compose_from_text.py — 当用户给的截图被截/模糊/有 UI 噪音时，从源文字内容
用 Pillow 重排合成一张干净的设计稿级别对比图/教程图/数据图。

Use when:
- 用户提供"风格对比图"/"教程图"/"数据图"的截图但部分内容截断
- 用户提供的截图分辨率太低、包含 UI 噪音
- AI 重新生成比让用户重截更可靠

Pitfall #30 in SKILL.md (2026-07-06 实测).
"""
import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

CJK_FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def find_font():
    for p in CJK_FONT_PATHS:
        if Path(p).exists():
            return p
    return None


def load_font(size: int):
    fp = find_font()
    if fp:
        return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def render_two_column(
    left_title: str,
    left_subtitle: str,
    left_blocks: list,
    right_title: str,
    right_subtitle: str,
    right_blocks: list,
    footer: str = "",
    output_path: str = "compare.png",
    canvas_size=(1400, 1500),
    title_bar_text: str = "风格学习前后对比",
    subtitle_bar_text: str = "",
):
    """
    Render a clean two-column comparison image.

    block format: tuple of (kind, text) where kind is one of:
      - "TITLE": large bold heading
      - "H": section header
      - "P": paragraph (auto-wrap)
      - "SIG": signature line (gray, smaller)
      - "BREAK": vertical breathing room
    """
    W, H = canvas_size
    canvas = Image.new("RGB", (W, H), "#fafafa")
    draw = ImageDraw.Draw(canvas)

    # 顶部黑底标题栏
    title_h = 100
    draw.rectangle([0, 0, W, title_h], fill="#1f2329")
    title_font = load_font(36)
    sub_bar_font = load_font(20)
    draw.text((40, 28), title_bar_text, fill="#ffffff", font=title_font)
    if subtitle_bar_text:
        draw.text((40, 75), subtitle_bar_text, fill="#9ca3af", font=sub_bar_font)

    top = title_h
    pad = 30
    col_w = (W - pad * 3) // 2
    left_x0, left_x1 = pad, pad + col_w
    right_x0, right_x1 = pad * 2 + col_w, pad * 2 + col_w * 2
    label_h = 50
    sub_label_h = 30

    # 左栏 header
    draw.rectangle([left_x0, top, left_x1, top + label_h], fill="#e5e7eb")
    draw.text((left_x0 + 20, top + 10), left_title, fill="#374151", font=load_font(24))
    if left_subtitle:
        draw.text((left_x0 + 20, top + label_h + 5), left_subtitle, fill="#6b7280", font=load_font(16))

    # 右栏 header
    draw.rectangle([right_x0, top, right_x1, top + label_h], fill="#F97316")
    draw.text((right_x0 + 20, top + 10), right_title, fill="#ffffff", font=load_font(24))
    if right_subtitle:
        draw.text((right_x0 + 20, top + label_h + 5), right_subtitle, fill="#9a3412", font=load_font(16))

    # 卡片底
    card_top = top + label_h + sub_label_h
    draw.rectangle([left_x0, card_top, left_x1, H - 80], fill="#ffffff", outline="#e5e7eb", width=1)
    draw.rectangle([right_x0, card_top, right_x1, H - 80], fill="#ffffff", outline="#F97316", width=2)

    def write_column(blocks, x0, x1, y0):
        y = y0 + 20
        body_font = load_font(20)
        title_font2 = load_font(26)
        bold_font = load_font(22)
        sig_font = load_font(18)
        max_chars = (x1 - x0 - 40) // 22
        for kind, text in blocks:
            if kind == "TITLE":
                tag = "【标题】"
                draw.text((x0 + 20, y + 5), tag, fill="#F97316", font=load_font(28))
                w1 = int(draw.textlength(tag, font=load_font(28)))
                main = text[len(tag):] if text.startswith(tag) else text
                if len(main) > max_chars - 4:
                    draw.text((x0 + 20 + w1, y + 5), main[: max_chars - 4], fill="#1f2329", font=title_font2)
                    draw.text((x0 + 20, y + 45), main[max_chars - 4:], fill="#1f2329", font=title_font2)
                    y += 95
                else:
                    draw.text((x0 + 20 + w1, y + 5), main, fill="#1f2329", font=title_font2)
                    y += 50
            elif kind == "H":
                draw.text((x0 + 20, y + 5), text, fill="#1f2329", font=bold_font)
                y += 38
            elif kind == "P":
                lines = []
                while len(text) > max_chars:
                    lines.append(text[:max_chars])
                    text = text[max_chars:]
                if text:
                    lines.append(text)
                for ln in lines:
                    draw.text((x0 + 20, y + 5), ln, fill="#374151", font=body_font)
                    y += 30
                y += 8
            elif kind == "SIG":
                draw.text((x0 + 20, y + 5), text, fill="#6b7280", font=sig_font)
                y += 28
            elif kind == "BREAK" or kind == "":
                y += 12
        return y

    write_column(left_blocks, left_x0, left_x1, card_top)
    write_column(right_blocks, right_x0, right_x1, card_top)

    # 底部参数对比条
    if footer:
        draw.rectangle([40, H - 70, W - 40, H - 30], fill="#f0f7ff")
        draw.text((60, H - 60), footer, fill="#2563EB", font=load_font(18))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, optimize=True)
    print(f"OK generated: {output_path} ({Path(output_path).stat().st_size / 1024:.0f} KB, {W}x{H})")


if __name__ == "__main__":
    import json
    ap = argparse.ArgumentParser(description="Compose a clean two-column comparison image from source text")
    ap.add_argument("--left-title", required=True)
    ap.add_argument("--left-subtitle", default="")
    ap.add_argument("--left-blocks-file", required=True, help="JSON list of [kind, text] tuples")
    ap.add_argument("--right-title", required=True)
    ap.add_argument("--right-subtitle", default="")
    ap.add_argument("--right-blocks-file", required=True)
    ap.add_argument("--footer", default="")
    ap.add_argument("--title-bar", default="风格学习前后对比")
    ap.add_argument("--subtitle-bar", default="")
    ap.add_argument("--output", required=True)
    ap.add_argument("--width", type=int, default=1400)
    ap.add_argument("--height", type=int, default=1500)
    args = ap.parse_args()

    left_blocks = json.loads(Path(args.left_blocks_file).read_text())
    right_blocks = json.loads(Path(args.right_blocks_file).read_text())

    render_two_column(
        left_title=args.left_title,
        left_subtitle=args.left_subtitle,
        left_blocks=left_blocks,
        right_title=args.right_title,
        right_subtitle=args.right_subtitle,
        right_blocks=right_blocks,
        footer=args.footer,
        output_path=args.output,
        canvas_size=(args.width, args.height),
        title_bar_text=args.title_bar,
        subtitle_bar_text=args.subtitle_bar,
    )
