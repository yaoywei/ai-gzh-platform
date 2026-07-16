#!/usr/bin/env python3
"""
执行后验证：检查所有产出物是否完整且质量达标。

用法：
  python3 postflight.py --output-dir output/xxx
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_skill_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"❌ 配置文件不存在: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_CFG = load_skill_config()
BRAND = _CFG.get("brand", {})
BRAND_NAME = BRAND.get("brand_name", "")
COMPANY_NAME = BRAND.get("company_name", "")


def check(name, ok, detail=""):
    status = "✅" if ok else "❌"
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    return ok


def main():
    parser = argparse.ArgumentParser(description="执行后验证")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    args = parser.parse_args()

    output_dir = args.output_dir
    print("=" * 50)
    print("Postflight Check — 执行后验证")
    print("=" * 50)

    all_ok = True

    # 1. 文章文件
    print("\n[1/6] 文章文件")
    article_path = os.path.join(output_dir, "article.md")
    if os.path.exists(article_path):
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chinese = len(re.findall(r'[\u4e00-\u9fff]', content))
        all_ok &= check("article.md 存在", True, f"{chinese}字")

        # 字数检查
        all_ok &= check("字数 ≥2500", chinese >= 2500, f"{chinese}字")

        # 禁用词检查
        forbidden = ["赋能", "闭环", "颠覆式", "颗粒度", "抓手", "底层逻辑",
                      "颠覆", "引领", "唯一", "综上所述", "值得注意的是"]
        found = [w for w in forbidden if w in content]
        all_ok &= check("禁用词零命中", len(found) == 0,
                         f"发现: {found}" if found else "")

        # 双引号检查（排除书名号《》）
        quotes = re.findall(r'[""\u201c\u201d]', content)
        all_ok &= check("双引号零命中", len(quotes) == 0,
                         f"{len(quotes)}处" if quotes else "")

        # 表格检查
        tables = re.findall(r'^\|.+\|$', content, re.MULTILINE)
        data_rows = [t for t in tables if not all(set(c) <= set('-: ') for c in t.split('|'))]
        all_ok &= check("数据表格 ≥2", len(data_rows) >= 4,
                         f"{len(data_rows)}行数据（需≥4行=2个表）")

        # 配图标记检查（支持两种格式）
        img_markers_kunpeng = re.findall(r'【配图\d+：.+?】', content)
        img_markers_aigzh = re.findall(r'\[(?:SCREENSHOT|AI-IMG):.+?\]', content)
        total_markers = len(img_markers_kunpeng) + len(img_markers_aigzh)
        all_ok &= check("配图标记 ≥3", total_markers >= 3,
                         f"{total_markers}个: {len(img_markers_kunpeng)} 配图标记 + {len(img_markers_aigzh)} 占位符")

        # 品牌名检查（如果配置了）
        if BRAND_NAME and BRAND_NAME != "你的公众号品牌":
            brand_mentions = len(re.findall(re.escape(BRAND_NAME), content))
            check(f"品牌名「{BRAND_NAME}」嵌入", brand_mentions >= 1,
                  f"{brand_mentions}处")
    else:
        all_ok &= check("article.md 存在", False)

    # 2. 公司名检查（可选）
    if COMPANY_NAME:
        print(f"\n[2/6] 公司名检查")
        if os.path.exists(article_path):
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            company_mentions = len(re.findall(re.escape(COMPANY_NAME), content))
            all_ok &= check(f"公司名「{COMPANY_NAME}」嵌入 ≥2", company_mentions >= 2,
                             f"{company_mentions}处")
    else:
        print("\n[2/6] 公司名检查")
        print("  ⏭ brand.company_name 未配置，跳过")

    # 3. 图片文件
    print("\n[3/6] 图片文件")
    imgs_dir = os.path.join(output_dir, "imgs")
    if os.path.isdir(imgs_dir):
        img_files = [f for f in os.listdir(imgs_dir)
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        large_imgs = [f for f in img_files
                      if os.path.getsize(os.path.join(imgs_dir, f)) > 100 * 1024]
        all_ok &= check("图片文件 ≥4张", len(large_imgs) >= 4,
                         f"{len(large_imgs)}张 >100KB")
    else:
        all_ok &= check("imgs/ 目录存在", False)

    # 4. HTML文件
    print("\n[4/6] HTML文件")
    html_dir = os.path.join(output_dir, "html")
    if os.path.isdir(html_dir):
        html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
        all_ok &= check("HTML文件存在", len(html_files) > 0,
                         f"{len(html_files)}个")

        for hf in html_files:
            hp = os.path.join(html_dir, hf)
            with open(hp, 'r', encoding='utf-8') as f:
                html_content = f.read()
            b64_count = html_content.count('data:image/jpeg;base64,')
            size_kb = os.path.getsize(hp) // 1024
            all_ok &= check(f"{hf}", b64_count >= 3,
                             f"{size_kb}KB, {b64_count}张内嵌图")
    else:
        all_ok &= check("html/ 目录存在", False)

    # 5. 标题字节检查
    print("\n[5/6] 标题字节")
    title_path = os.path.join(output_dir, "title.txt")
    if os.path.exists(title_path):
        with open(title_path, 'r', encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
        if lines:
            title = lines[0]
            title_bytes = len(title.encode('utf-8'))
            all_ok &= check("标题 ≤30字节", title_bytes <= 30,
                             f"{title_bytes}B: {title}")
        if len(lines) > 1:
            digest = lines[1]
            digest_bytes = len(digest.encode('utf-8'))
            all_ok &= check("摘要 ≤54字节", digest_bytes <= 54,
                             f"{digest_bytes}B")
    else:
        print("  ⏭ title.txt 不存在，跳过标题检查")

    # 6. 段落行距检查
    print("\n[6/8] 段落行距")
    if os.path.exists(article_path):
        with open(article_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 提取正文段落（排除标题、表格、代码块、列表、引用块、配图标记、分隔线）
        in_code_block = False
        paragraphs = []
        current_para = []
        for line in lines:
            stripped = line.strip()
            # 代码块开关
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                if current_para:
                    paragraphs.append(current_para)
                    current_para = []
                continue
            if in_code_block:
                continue
            # 跳过非正文行
            if (stripped.startswith('#') or
                stripped.startswith('|') or
                stripped.startswith('>') or
                stripped.startswith('- ') or
                stripped.startswith('* ') or
                stripped.startswith('---') or
                stripped.startswith('【配图') or
                stripped.startswith('[SCREENSHOT') or
                stripped.startswith('[AI-IMG') or
                re.match(r'^\d+\.\s', stripped) or
                stripped == ''):
                if current_para:
                    paragraphs.append(current_para)
                    current_para = []
                continue
            current_para.append(stripped)
        if current_para:
            paragraphs.append(current_para)

        long_paras = []
        for i, para in enumerate(paragraphs):
            if len(para) > 4:
                long_paras.append((i + 1, len(para)))

        all_ok &= check("段落 ≤4 行", len(long_paras) == 0,
                         f"{len(long_paras)} 段超限" if long_paras else "")
        if long_paras:
            for pnum, plen in long_paras[:5]:
                print(f"    ⚠️ 第 {pnum} 段有 {plen} 行，建议拆分")
    else:
        print("  ⏭ article.md 不存在，跳过")

    # 7. 信息峰值密度检查（警告，不阻断）
    print("\n[7/8] 信息峰值密度")
    if os.path.exists(article_path):
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 排除标题/元数据行后计算中文字数
        body_lines = []
        in_code = False
        for line in content.split('\n'):
            if line.strip().startswith('```'):
                in_code = not in_code
                continue
            if in_code:
                continue
            body_lines.append(line)
        body_text = '\n'.join(body_lines)
        chinese_count = len(re.findall(r'[\u4e00-\u9fff]', body_text))

        # 统计信息峰值标记
        peak_patterns = [
            r'\*\*[^*]{4,}\*\*',          # 粗体（≥4字符，排除短标记）
            r'「[^」]{4,}」',              # 金句引用
            r'^>\s+.+',                     # 引用块
            r'\d+(?:\.\d+)?%',             # 百分比数据
            r'\d+(?:\.\d+)?(?:分钟|小时|天|周|个月|年)',  # 时间数据
            r'❌|✅|📝',                    # 案例/踩坑标记
        ]
        peak_count = 0
        for pattern in peak_patterns:
            peak_count += len(re.findall(pattern, body_text, re.MULTILINE))

        # 去重（同一行可能匹配多个模式，按行去重）
        peak_lines = set()
        for pattern in peak_patterns:
            for m in re.finditer(pattern, body_text, re.MULTILINE):
                line_start = body_text.rfind('\n', 0, m.start()) + 1
                line_end = body_text.find('\n', m.end())
                if line_end == -1:
                    line_end = len(body_text)
                peak_lines.add((line_start, line_end))
        unique_peaks = len(peak_lines)

        # 每 300 字至少 1 个峰值
        expected_peaks = max(1, chinese_count // 300)
        density_ok = unique_peaks >= expected_peaks
        ratio = unique_peaks / expected_peaks if expected_peaks > 0 else 0
        print(f"  {'✅' if density_ok else '⚠️'} 信息峰值密度 — "
              f"{unique_peaks} 个峰值 / 预期 ≥{expected_peaks} 个 "
              f"(每300字1个, 密度比 {ratio:.1f})")
        if not density_ok:
            print("  💡 建议：在平铺直叙的段落中补充金句/数据/小案例/对比/反常识")
            print("     参考 references/information-density.md")
        # 密度不足是警告，不阻断 all_ok
    else:
        print("  ⏭ article.md 不存在，跳过")

    # 8. QA 报告（可选）
    print("\n[8/8] QA 报告")
    qa_path = os.path.join(output_dir, "qa-report.md")
    if os.path.exists(qa_path):
        check("qa-report.md 存在", True)
    else:
        print("  ⏭ qa-report.md 不存在（可选，非阻塞）")

    # 总结
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ 验证通过，所有产出物完整且质量达标")
    else:
        print("❌ 验证未通过，请检查上述问题")
    print("=" * 50)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
