#!/usr/bin/env python3
"""
压缩 output 目录下的 PNG 配图为 JPG（quality 80），避免 push_draft.py 触发
errcode 45002 (content size out of limit)。

用法:
  python scripts/compress_images.py <output_dir>

例:
  python scripts/compress_images.py output/2026-07-02-ai-gzh-true-way/

行为:
  - 找目录下所有 *.png（除 cover.png / *_calibration* / assets/examples/*）
  - 转 RGB（如 RGBA 则贴白底），保存为同名 .jpg
  - quality=80, optimize=True
  - 输出每个文件的 src_size / dst_size / ratio
  - 总压缩比
"""
import sys
import os
from pathlib import Path
from PIL import Image

# These filenames are NOT body images — keep as PNG
KEEP_AS_PNG = {"cover.png", "thumb.png"}

def should_compress(path: Path) -> bool:
    if path.suffix.lower() != ".png":
        return False
    if path.name in KEEP_AS_PNG:
        return False
    # Skip assets/examples/ calibration samples
    if "assets/examples" in str(path) or "calibration" in path.name.lower():
        return False
    return True

def compress_one(src: Path) -> tuple[str, int, int]:
    dst = src.with_suffix(".jpg")
    img = Image.open(src)
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
        img = bg
    img.save(dst, "JPEG", quality=80, optimize=True)
    return (dst.name, os.path.getsize(src), os.path.getsize(dst))

def main():
    if len(sys.argv) != 2:
        print("usage: python compress_images.py <output_dir>")
        sys.exit(1)
    out_dir = Path(sys.argv[1]).resolve()
    if not out_dir.is_dir():
        print(f"FAIL: {out_dir} is not a directory")
        sys.exit(1)

    pngs = [p for p in out_dir.rglob("*.png") if should_compress(p)]
    if not pngs:
        print(f"no compressible PNGs in {out_dir}")
        return

    total_src = 0
    total_dst = 0
    for src in sorted(pngs):
        name, src_size, dst_size = compress_one(src)
        ratio = 100 * dst_size / src_size
        print(f"  {name}: {src_size//1024}KB -> {dst_size//1024}KB ({ratio:.0f}%)")
        total_src += src_size
        total_dst += dst_size

    print()
    print(f"compressed {len(pngs)} images")
    print(f"  total: {total_src//1024}KB -> {total_dst//1024}KB "
          f"({100*total_dst/total_src:.0f}%)")
    if total_src > 2 * 1024 * 1024:
        print(f"  WARNING: total src > 2MB, may still trigger 45002. "
              f"Lower quality or remove cover from HTML.")

if __name__ == "__main__":
    main()
