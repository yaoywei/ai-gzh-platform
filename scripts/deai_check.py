#!/usr/bin/env python3
"""
deai_check.py — 自动扫描 AI 指纹词（30 词清单 + 命中数阈值 + 报告）

来源：参考"纯爱作家"文章 21 词清单 + 师傅知识库 v0.1 §4.3 17 词
清单：合并 30 词（去重）
阈值：3 个命中（超过则警告）

用法：
  python3 scripts/deai_check.py article.md
  python3 scripts/deai_check.py article.md --threshold 5
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# 30 词 AI 指纹词（合并：纯爱作家文章 21 词 + 师傅知识库 v0.1 §4.3 17 词，去重）
AI_FINGERPRINT_WORDS = [
    # 纯爱作家文章里列的
    "值得注意的是", "综上所述", "首先", "其次", "最后", "需要指出的是",
    "让我们", "在这个过程中", "总的来说", "不难发现", "由此可见",
    "换句话说", "具体来说", "事实上", "本文将", "接下来",
    "总而言之", "毫无疑问", "显而易见", "众所周知",
    # 师傅知识库 v0.1 §4.3 补充
    "赋能", "闭环", "颠覆式", "颗粒度", "抓手", "底层逻辑",
    "降维打击", "打通", "永动机",
    # 师傅知识库"真禁用" 词
    "能量场", "显化", "调频", "引领", "唯一",
]

# 不区分大小写
def find_fingerprints(text: str) -> list[tuple[str, int, list[int]]]:
    """返回 [(词, 命中数, [行号]), ...]"""
    scannable_lines = []
    in_code_block = False
    for i, line in enumerate(text.split('\n'), 1):
        if re.match(r'^\s*```', line):
            in_code_block = not in_code_block
            continue
        if in_code_block or re.match(r'^\s*>', line):
            continue

        # 图片说明不属于正文；同时兼容 Markdown 图片和 HTML img 标签。
        line = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', line)
        line = re.sub(r'<img\b[^>]*>', '', line, flags=re.IGNORECASE)
        scannable_lines.append((i, line))

    results = []
    for word in AI_FINGERPRINT_WORDS:
        hits = [i for i, line in scannable_lines if word in line]
        if hits:
            results.append((word, len(hits), hits))
    return results


def main():
    parser = argparse.ArgumentParser(description='AI 指纹词扫描')
    parser.add_argument('file', help='Markdown 文件路径')
    parser.add_argument('--threshold', type=int, default=3, help='命中数阈值（超过警告）')
    args = parser.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f'❌ 文件不存在：{args.file}')
        sys.exit(1)

    text = p.read_text(encoding='utf-8')
    fingerprints = find_fingerprints(text)
    total_hits = sum(c for _, c, _ in fingerprints)

    print(f'\n{"=" * 60}')
    print(f'🔍 AI 指纹词扫描：{p.name}')
    print(f'{"=" * 60}\n')

    if not fingerprints:
        print('✅ 0 命中（30 词清单全清）')
        return 0

    for word, count, lines in fingerprints:
        line_str = ','.join(str(l) for l in lines[:5])
        more = f' (+{len(lines) - 5} 行)' if len(lines) > 5 else ''
        print(f'  [{count:2d}] {word:<10} 行 {line_str}{more}')

    print(f'\n📊 命中统计：{len(fingerprints)} 词 / {total_hits} 次')
    if total_hits > args.threshold:
        print(f'⚠️ 超过阈值 {args.threshold} → 建议修改后重发')
        return 1
    print(f'✅ 未超阈值 {args.threshold}（{total_hits} ≤ {args.threshold}）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
