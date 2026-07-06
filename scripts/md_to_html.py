#!/usr/bin/env python3
"""
Markdown → tech-blue 风格 HTML 转换器

按 ai-gzh-platform 的 Step 10 双 HTML 模式产出：
  - 微信粘贴版（base64 内嵌，方便飞书/浏览器预览）
  - 推草稿版（相对路径 imgs/*.jpg，配合 push_draft.py）

支持元素：
  - # / ## / ### 标题（H1 加蓝色装饰线，H2 加蓝色左竖条，H3 普通加粗）
  - 表格（自动过滤 |---|---| 分隔行，首行作为表头）
  - 引用块 > xxx（浅蓝底 + 蓝色左竖线）
  - 有序/无序列表（圆点用 #F97316 橙色，避免和链接蓝色撞色）
  - 代码块 / 行内 code
  - **加粗** / `inline code`
  - [SCREENSHOT: ...] 占位框（橙色虚线）→ 提示用户替换
  - [AI-IMG: ...] 占位框（蓝色虚线）→ 提示用户生成
  - —— 签名行（带顶部虚线分隔）

用法:
  python scripts/md_to_html.py
  # 或带参数
  python scripts/md_to_html.py <article.md> <output_dir>

约定: 颜色取自 config.json html_template（tech-blue: #2563EB, #F97316）
"""
import re
import base64
import os
import sys
from pathlib import Path


def find_latest_output_dir() -> Path:
    """找最新的 output/{date}-{slug} 目录"""
    base = Path.home() / '.hermes/skills/ai-gzh-platform/output'
    if not base.exists():
        sys.exit(f"FAIL: {base} 不存在")
    subdirs = [p for p in base.iterdir() if p.is_dir()]
    if not subdirs:
        sys.exit(f"FAIL: {base} 下没有子目录")
    return max(subdirs, key=lambda p: p.stat().st_mtime)


# ────────── 颜色配置 (tech-blue) ──────────
COLOR = {
    'primary': '#2563EB',
    'accent':  '#F97316',
    'bg':      '#FFFFFF',
    'text':    '#1F2937',
    'sub':     '#6B7280',
    'border':  '#E5E7EB',
    'soft_bg': '#F8FAFC',
    'code_bg': '#F1F5F9',
    'ok':      '#10B981',
    'err':     '#EF4444',
}


# ────────── 占位符解析 ──────────
SCREENSHOT_RE = re.compile(r'^\[SCREENSHOT:\s*(.+?)\]\s*$', re.MULTILINE)
AI_IMG_RE     = re.compile(r'^\[AI-IMG:\s*(.+?)\]\s*$', re.MULTILINE)


def render_placeholder_box(text, kind='screenshot'):
    """占位提示框：截图位（橙虚线）vs AI 配图位（蓝虚线）— 视觉区分"""
    if kind == 'screenshot':
        return (
            f'<div style="margin:24px 0;padding:18px 20px;background:#FFFBEB;'
            f'border:1px dashed #F59E0B;border-radius:8px;color:#92400E;'
            f'font-size:14px;line-height:1.7;">'
            f'<div style="font-weight:600;margin-bottom:6px;">📷 待替换：截图位</div>'
            f'<div style="color:#78350F;">{text}</div></div>'
        )
    return (
        f'<div style="margin:24px 0;padding:18px 20px;background:#EFF6FF;'
        f'border:1px dashed #2563EB;border-radius:8px;color:#1E40AF;'
        f'font-size:14px;line-height:1.7;">'
        f'<div style="font-weight:600;margin-bottom:6px;">🎨 待生成：AI 配图位</div>'
        f'<div style="color:#1E3A8A;">{text}</div></div>'
    )


# ────────── Markdown 元素渲染 ──────────
def escape_html(text):
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))


def render_inline(text):
    text = escape_html(text)
    # **xxx** -> <strong>
    text = re.sub(r'\*\*([^*]+)\*\*',
                  r'<strong style="color:#1F2937;font-weight:600;">\1</strong>',
                  text)
    # `xxx` -> <code>
    text = re.sub(r'`([^`]+)`',
                  r'<code style="background:#F1F5F9;padding:1px 6px;'
                  r'border-radius:4px;font-family:Menlo,Consolas,monospace;'
                  r'font-size:14px;color:#2563EB;">\1</code>',
                  text)
    return text


def is_table_separator(row):
    cells = [c.strip() for c in row.strip().strip('|').split('|')]
    return all(re.match(r'^:?-+:?$', c) for c in cells if c)


def render_table(rows):
    rows = [r for r in rows if not is_table_separator(r)]
    if not rows:
        return ''
    html = ['<table style="width:100%;border-collapse:collapse;margin:20px 0;'
            'font-size:15px;line-height:1.6;background:#FFFFFF;'
            'border:1px solid #E5E7EB;border-radius:6px;overflow:hidden;">']
    for i, row in enumerate(rows):
        cells = [c.strip() for c in row.strip().strip('|').split('|')]
        tag = 'th' if i == 0 else 'td'
        if i == 0:
            style = ('background:#EFF6FF;color:#1E40AF;font-weight:600;'
                     'text-align:left;padding:10px 12px;'
                     'border-bottom:1px solid #E5E7EB;')
        else:
            style = ('padding:10px 12px;border-bottom:1px solid #F3F4F6;'
                     'color:#1F2937;')
            if i % 2 == 0:
                style += 'background:#F9FAFB;'
        row_html = ''.join(f'<{tag} style="{style}">{render_inline(c)}</{tag}>'
                           for c in cells)
        html.append(f'<tr>{row_html}</tr>')
    html.append('</table>')
    return '\n'.join(html)


def render_quote(text):
    return (
        f'<blockquote style="margin:20px 0;padding:12px 16px;background:#F0F9FF;'
        f'border-left:3px solid #2563EB;color:#1E40AF;font-size:15px;'
        f'line-height:1.7;border-radius:0 6px 6px 0;">'
        f'{render_inline(text)}</blockquote>'
    )


def render_list_items(items, ordered=False):
    tag = 'ol' if ordered else 'ul'
    style = 'list-style:none;padding-left:0;margin:16px 0;'
    item_style = ('padding:6px 0 6px 24px;position:relative;color:#1F2937;'
                  'font-size:15px;line-height:1.75;')
    # 圆点用橙色 #F97316，避免和正文链接蓝色撞色
    bullet_style = ('position:absolute;left:6px;top:14px;width:6px;height:6px;'
                    'background:#F97316;border-radius:50%;')
    if ordered:
        item_style = ('padding:6px 0 6px 28px;position:relative;color:#1F2937;'
                      'font-size:15px;line-height:1.75;')
        bullet_style = ('position:absolute;left:6px;top:8px;color:#F97316;'
                        'font-weight:600;')
    items_html = []
    for i, item in enumerate(items, 1):
        if ordered:
            items_html.append(
                f'<li style="{item_style}">'
                f'<span style="{bullet_style}">{i}.</span>'
                f'{render_inline(item)}</li>'
            )
        else:
            items_html.append(
                f'<li style="{item_style}">'
                f'<span style="{bullet_style}"></span>'
                f'{render_inline(item)}</li>'
            )
    return f'<{tag} style="{style}">{"".join(items_html)}</{tag}>'


def render_h1(text):
    return (
        f'<h1 style="font-size:24px;font-weight:700;color:#1F2937;'
        f'margin:32px 0 16px;line-height:1.4;'
        f'border-bottom:2px solid #2563EB;padding-bottom:8px;">'
        f'{render_inline(text)}</h1>'
    )


def render_h2(text):
    return (
        f'<h2 style="font-size:20px;font-weight:700;color:#1E40AF;'
        f'margin:32px 0 14px;line-height:1.4;'
        f'padding-left:12px;border-left:4px solid #2563EB;">'
        f'{render_inline(text)}</h2>'
    )


def render_h3(text):
    return (
        f'<h3 style="font-size:17px;font-weight:600;color:#1F2937;'
        f'margin:24px 0 12px;line-height:1.4;">'
        f'{render_inline(text)}</h3>'
    )


def render_code_block(text):
    return (
        f'<pre style="background:#1E293B;color:#E2E8F0;padding:16px 18px;'
        f'border-radius:8px;font-size:14px;line-height:1.6;overflow-x:auto;'
        f'margin:18px 0;font-family:Menlo,Consolas,monospace;">'
        f'{escape_html(text)}</pre>'
    )


def render_paragraph(text):
    return (
        f'<p style="margin:14px 0;font-size:15.5px;line-height:1.8;'
        f'color:#1F2937;letter-spacing:0.3px;">'
        f'{render_inline(text)}</p>'
    )


# ────────── 主转换 ──────────
def md_to_html(content, in_meta_section=False):
    """Markdown → HTML
    in_meta_section: True 后跳过渲染（用于元信息部分）
    """
    lines = content.split('\n')
    html_parts = []
    i = 0
    in_meta = in_meta_section

    while i < len(lines):
        line = lines[i]

        # 「配图占位说明」section 之后停止渲染正文
        if line.startswith('## 📌'):
            in_meta = True
        if in_meta:
            i += 1
            continue

        # SCREENSHOT / AI-IMG 占位
        m_ss = SCREENSHOT_RE.match(line)
        m_ai = AI_IMG_RE.match(line)
        if m_ss:
            html_parts.append(render_placeholder_box(m_ss.group(1), 'screenshot'))
            i += 1
            continue
        if m_ai:
            html_parts.append(render_placeholder_box(m_ai.group(1), 'ai_img'))
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        # Markdown 分隔线 ---（≥3 个连字符）
        if re.match(r'^-{3,}\s*$', line.strip()):
            i += 1
            continue

        # 标题
        if line.startswith('# '):
            html_parts.append(render_h1(line[2:].strip()))
            i += 1
            continue
        if line.startswith('## '):
            html_parts.append(render_h2(line[3:].strip()))
            i += 1
            continue
        if line.startswith('### '):
            html_parts.append(render_h3(line[4:].strip()))
            i += 1
            continue

        # 引用
        if line.startswith('> '):
            quote_lines = []
            while i < len(lines) and (lines[i].startswith('> ') or
                                       lines[i].startswith('>')):
                quote_lines.append(lines[i].lstrip('> ').rstrip())
                i += 1
            html_parts.append(render_quote(' '.join(quote_lines)))
            continue

        # 代码块
        if line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            html_parts.append(render_code_block('\n'.join(code_lines)))
            continue

        # 表格
        if '|' in line and i + 1 < len(lines) and is_table_separator(lines[i+1]):
            table_rows = [line]
            i += 1
            while i < len(lines) and '|' in lines[i]:
                table_rows.append(lines[i])
                i += 1
            html_parts.append(render_table(table_rows))
            continue

        # 无序列表
        if re.match(r'^\s*[-*]\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\s*[-*]\s+', lines[i]):
                items.append(re.sub(r'^\s*[-*]\s+', '', lines[i]))
                i += 1
            html_parts.append(render_list_items(items, ordered=False))
            continue

        # 有序列表
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                items.append(re.sub(r'^\s*\d+\.\s+', '', lines[i]))
                i += 1
            html_parts.append(render_list_items(items, ordered=True))
            continue

        # 签名行 —— xxx
        if line.startswith('—— '):
            html_parts.append(
                f'<p style="margin:32px 0 8px;padding-top:20px;'
                f'border-top:1px dashed #E5E7EB;color:#6B7280;'
                f'font-size:14px;text-align:right;">'
                f'{render_inline(line)}</p>'
            )
            i += 1
            continue

        # 普通段落
        html_parts.append(render_paragraph(line))
        i += 1

    return '\n'.join(html_parts)


# ────────── 输出 ──────────
def make_full_html(body):
    """完整 HTML 文档（微信粘贴版用）"""
    return (
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>公众号文章</title>\n'
        '</head>\n'
        '<body style="margin:0;padding:24px 18px;background:#F8FAFC;'
        'font-family:-apple-system,BlinkMacSystemFont,'
        '\'PingFang SC\',\'Microsoft YaHei\','
        '\'Helvetica Neue\',sans-serif;">\n'
        '<div style="max-width:680px;margin:0 auto;background:#FFFFFF;'
        'padding:32px 24px;border-radius:12px;'
        'box-shadow:0 2px 8px rgba(0,0,0,0.04);">\n'
        f'{body}\n'
        '<div style="margin-top:40px;padding:20px 0;'
        'border-top:1px dashed #E5E7EB;text-align:center;'
        'color:#9CA3AF;font-size:13px;">\n'
        '  本文由「大姚AI提效」原创 · 用 AI 改造你的公众号\n'
        '</div>\n'
        '</div>\n'
        '</body>\n'
        '</html>\n'
    )


def main():
    if len(sys.argv) >= 3:
        article_path = Path(sys.argv[1]).resolve()
        html_dir = Path(sys.argv[2]).resolve()
    else:
        out_dir = find_latest_output_dir()
        article_path = out_dir / 'article.md'
        html_dir = out_dir / 'html'

    if not article_path.exists():
        sys.exit(f"FAIL: {article_path} 不存在")
    html_dir.mkdir(parents=True, exist_ok=True)

    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 取正文（不含元信息）
    meta_idx = content.find('## 📌')
    if meta_idx > 0:
        body_content = content[:meta_idx].rstrip()
        body_content = re.sub(r'\n---\s*$', '', body_content)
    else:
        body_content = content

    body_html = md_to_html(body_content)
    full_html = make_full_html(body_html)

    # 微信粘贴版（base64 内嵌，单独可打开）
    paste_path = html_dir / 'gzh-微信粘贴版-v1.html'
    with open(paste_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    paste_size = os.path.getsize(paste_path) / 1024
    print(f'✅ 微信粘贴版: {paste_path}  ({paste_size:.1f} KB)')

    # 推草稿版（等真图生成后再做相对路径；当前用相同 body）
    draft_path = html_dir / 'gzh-推草稿版-v1.html'
    with open(draft_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    draft_size = os.path.getsize(draft_path) / 1024
    print(f'✅ 推草稿版:   {draft_path}  ({draft_size:.1f} KB)')

    print(f'\n预览: 浏览器打开 {paste_path}')


if __name__ == '__main__':
    main()
