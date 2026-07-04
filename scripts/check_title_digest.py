#!/usr/bin/env python3
"""
标题/摘要字节校验脚本（微信公众号草稿硬限）

用法：
  python check_title_digest.py --title "标题" --digest "摘要"
  python check_title_digest.py --article output/2026-07-03-xxx/article.md

规则：
  - title  ≤ 30 字节（UTF-8 编码后字节数，中文 3B/字）
  - digest ≤ 54 字节

退出码：
  0 = 通过
  1 = 超限（打印当前字节数 + 建议压缩方案）
"""
import argparse
import sys
import re
from pathlib import Path

TITLE_LIMIT = 30
DIGEST_LIMIT = 54


def utf8_bytes(s: str) -> int:
    return len(s.encode("utf-8"))


def extract_from_md(md_path: str) -> tuple[str, str]:
    """从 article.md 第一行提取标题，第二非空行或 frontmatter digest 提取摘要"""
    content = Path(md_path).read_text(encoding="utf-8")
    lines = content.strip().split("\n")

    title = ""
    digest = ""

    # 跳过 frontmatter
    in_fm = False
    body_start = 0
    if lines and lines[0].strip() == "---":
        in_fm = True
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                body_start = i + 1
                break

    body_lines = lines[body_start:]

    # 标题：第一个 # 开头的行或第一个非空行
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            break
        elif stripped and not title:
            title = stripped

    # 摘要：尝试找 <!-- digest: xxx --> 注释，否则取标题后第一段的前 18 个汉字
    digest_match = re.search(r'<!--\s*digest:\s*(.+?)\s*-->', content)
    if digest_match:
        digest = digest_match.group(1).strip()
    elif title:
        # 取标题后第一段非空文本
        found_title = False
        for line in body_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not found_title and stripped.startswith("#"):
                found_title = True
                continue
            if found_title or not title:
                digest = stripped[:18]
                break

    return title, digest


def suggest_compress(s: str, limit: int) -> str:
    """给出压缩建议"""
    current = utf8_bytes(s)
    over = current - limit
    # 估算需要砍几个汉字
    chinese_chars = sum(1 for c in s if ord(c) > 127)
    ascii_chars = len(s) - chinese_chars
    need_cut_chars = over // 3 + (1 if over % 3 else 0)

    return (
        f"  超限 {over}B，需砍约 {need_cut_chars} 个汉字。"
        f"当前 {chinese_chars} 汉字 + {ascii_chars} ASCII = {current}B"
    )


def main():
    parser = argparse.ArgumentParser(description="标题/摘要字节校验")
    parser.add_argument("--title", help="标题文本")
    parser.add_argument("--digest", help="摘要文本")
    parser.add_argument("--article", help="article.md 路径（自动提取标题和摘要）")
    args = parser.parse_args()

    if args.article:
        title, digest = extract_from_md(args.article)
        print(f"从 {args.article} 提取：")
        print(f"  标题: {title}")
        print(f"  摘要: {digest}")
    else:
        title = args.title or ""
        digest = args.digest or ""

    errors = []

    if title:
        tb = utf8_bytes(title)
        status = "✅" if tb <= TITLE_LIMIT else "❌"
        print(f"标题: {status} {tb}B / {TITLE_LIMIT}  \"{title}\"")
        if tb > TITLE_LIMIT:
            errors.append(("title", tb, title, TITLE_LIMIT))
    else:
        print("⚠️ 未提供标题")

    if digest:
        db = utf8_bytes(digest)
        status = "✅" if db <= DIGEST_LIMIT else "❌"
        print(f"摘要: {status} {db}B / {DIGEST_LIMIT}  \"{digest}\"")
        if db > DIGEST_LIMIT:
            errors.append(("digest", db, digest, DIGEST_LIMIT))
    else:
        print("⚠️ 未提供摘要（跳过校验）")

    if errors:
        print("\n❌ 字节超限，压缩建议：")
        for field, current, text, limit in errors:
            print(f"  [{field}] {suggest_compress(text, limit)}")
        sys.exit(1)
    else:
        print("\n✅ 校验通过")
        sys.exit(0)


if __name__ == "__main__":
    main()