#!/usr/bin/env python3
"""Interactive first-run configurator for ai-gzh-platform.

Creates config.json from config.example.json and forces the user to choose
brand, audience, HTML style, image style, and optional capabilities before the
skill generates any article.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "config.example.json"
CONFIG = ROOT / "config.json"


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def ask_list(prompt: str, default: list[str]) -> list[str]:
    raw = ask(prompt, "、".join(default))
    items = [x.strip() for x in raw.replace(",", "、").split("、") if x.strip()]
    return items or default


def choose(title: str, options: list[dict], default_id: str) -> dict:
    print(f"\n{title}")
    by_id = {o["id"]: o for o in options}
    for i, opt in enumerate(options, 1):
        mark = "（推荐）" if opt.get("recommended") else ""
        print(f"  {i}. {opt['id']} / {opt['name']} {mark} - {opt.get('best_for', '')}")
    while True:
        raw = ask("请输入编号或id", default_id)
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        if raw in by_id:
            return by_id[raw]
        print("输入无效，请重新选择。")


def yes_no(prompt: str, default: bool = False) -> bool:
    default_text = "y" if default else "n"
    raw = ask(prompt + " (y/n)", default_text).lower()
    return raw in {"y", "yes", "是", "启用", "true", "1"}


def main() -> None:
    if not EXAMPLE.exists():
        raise SystemExit(f"Missing template: {EXAMPLE}")
    cfg = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    fq = cfg.get("first_run_questions", {})

    print("AI公众号内容平台 · 首次配置向导")
    print("不会收集真实 API Key；这里只写环境变量名和启用开关。")

    cfg["brand_name"] = ask("公众号/品牌名", cfg.get("brand_name", "你的公众号品牌"))
    cfg["content_directions"] = ask_list(
        "内容方向（用顿号或逗号分隔，建议2-4个）",
        cfg.get("content_directions", ["AI提效", "行业观察", "工具教程"]),
    )
    target = cfg.setdefault("target_audience", {})
    target["P1"] = ask("P1核心读者画像", target.get("P1", ""))
    target["P2"] = ask("P2核心读者画像", target.get("P2", ""))
    target["P3"] = ask("P3核心读者画像", target.get("P3", ""))

    html_opt = choose(
        "选择HTML排版风格（10选1）",
        fq.get("html_template_options", []),
        cfg.get("html_template", {}).get("style_name", "tech-blue"),
    )
    cfg["html_template"] = {
        "style_name": html_opt["id"],
        "primary_color": html_opt.get("colors", {}).get("primary", "#2563EB"),
        "accent_color": html_opt.get("colors", {}).get("accent", "#F97316"),
        "background_color": html_opt.get("colors", {}).get("background", "#FFFFFF"),
    }

    image_opt = choose(
        "选择配图风格（6选1）",
        fq.get("image_style_options", []),
        cfg.get("image_style", {}).get("name", "baoyu-notion"),
    )
    cfg["image_style"] = {
        "name": image_opt["id"],
        "style_prompt_prefix": "",
    }
    if image_opt["id"] == "custom":
        cfg["image_style"]["style_prompt_prefix"] = ask("自定义配图prompt前缀", "")

    cfg.setdefault("image_api", {})["enabled"] = yes_no("是否启用图片生成？启用前请先确认 endpoint/key 可用", False)
    cfg.setdefault("feishu", {})["enabled"] = yes_no("是否启用飞书资料包？启用前请先确认飞书凭证可用", False)
    cfg.setdefault("wechat_proxy", {})["enabled"] = yes_no("是否启用微信公众号推草稿？启用前请先确认代理/凭证可用", False)

    cfg["setup_status"] = "configured"
    cfg.pop("first_run_questions", None)

    if CONFIG.exists():
        overwrite = yes_no(f"{CONFIG.name} 已存在，是否覆盖？", False)
        if not overwrite:
            raise SystemExit("已取消，未覆盖现有 config.json。")
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n已写入 {CONFIG}")
    print("下一步：把真实 API Key 写入环境变量/平台凭证；不要提交 config.json。")


if __name__ == "__main__":
    main()
