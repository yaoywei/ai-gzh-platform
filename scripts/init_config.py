#!/usr/bin/env python3
"""
交互式配置向导：引导用户填写 config.json 的关键字段。

用法：
  python3 init_config.py
  python3 init_config.py --non-interactive  # 仅检查，不修改
"""

import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"
EXAMPLE_PATH = Path(__file__).parent.parent / "config.example.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    elif EXAMPLE_PATH.exists():
        with open(EXAMPLE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print("❌ config.example.json 不存在！", file=sys.stderr)
        sys.exit(1)


def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已保存到 {CONFIG_PATH}")


def ask(prompt, default="", choices=None):
    """交互式输入，支持默认值和选项"""
    if choices:
        print(f"\n{prompt}")
        for i, c in enumerate(choices, 1):
            print(f"  {i}. {c}")
        while True:
            raw = input(f"选择 (1-{len(choices)}) [{default}]: ").strip()
            if not raw:
                return default
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
            except ValueError:
                if raw in choices:
                    return raw
            print(f"  无效选择，请输入 1-{len(choices)}")
    else:
        raw = input(f"{prompt} [{default}]: ").strip()
        return raw if raw else default


def main():
    print("╔══════════════════════════════════════════╗")
    print("║  AI公众号内容生产平台 · 配置向导         ║")
    print("╚══════════════════════════════════════════╝")

    cfg = load_config()

    if "--non-interactive" in sys.argv:
        print("\n当前配置：")
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
        return

    # 品牌名
    brand = cfg.get("brand", {})
    brand_name = ask(
        "公众号/品牌名称",
        default=brand.get("brand_name", ""),
    )
    brand["brand_name"] = brand_name

    # 排版由摸鱼小李 gzh-design-skill 接管（v4.1 启动版）
    # 师傅 npx skills add https://github.com/isjiamu/gzh-design-skill 后
    # 跑 npx gzh-design-skill render --input article.md --theme 摸鱼绿
    # 不在本 skill 内置排版（避免 AGPL 传染）

    # 飞书配置
    feishu = cfg.get("feishu", {})
    print(f"\n飞书模块: {'已启用' if feishu.get('enabled') else '未启用'}")
    enable_feishu = ask("是否启用飞书模块?", default="y" if feishu.get("enabled") else "n", choices=["y", "n"])
    feishu["enabled"] = enable_feishu == "y"
    if feishu["enabled"]:
        feishu["base_token"] = ask("飞书 Base Token", default=feishu.get("base_token", ""))
        feishu["table_topic"] = ask("选题配方表 Table ID", default=feishu.get("table_topic", ""))
        feishu["table_source"] = ask("素材原子库 Table ID", default=feishu.get("table_source", ""))
    cfg["feishu"] = feishu

    # Image API
    image_api = cfg.get("image_api", {})
    print(f"\n图片 API: {'已启用' if image_api.get('enabled') else '未启用'}")
    enable_img = ask("是否启用图片 API?", default="y" if image_api.get("enabled") else "n", choices=["y", "n"])
    image_api["enabled"] = enable_img == "y"
    if image_api["enabled"]:
        image_api["endpoint"] = ask("API Endpoint", default=image_api.get("endpoint", "https://api.zhongzhuan.chat/v1/images/generations"))
        image_api["key_env"] = ask("Key 环境变量名", default=image_api.get("key_env", "GPT_IMAGE2_API_KEY"))
    cfg["image_api"] = image_api

    # 微信代理
    wechat = cfg.get("wechat_proxy", {})
    print(f"\n微信代理: {'已启用' if wechat.get('enabled') else '未启用'}")
    enable_wx = ask("是否启用微信代理（推草稿）?", default="y" if wechat.get("enabled") else "n", choices=["y", "n"])
    wechat["enabled"] = enable_wx == "y"
    if wechat["enabled"]:
        wechat["server_ip"] = ask("代理服务器 IP", default=wechat.get("server_ip", ""))
        wechat["proxy_port"] = int(ask("代理端口", default=str(wechat.get("proxy_port", 8787))))
    cfg["wechat_proxy"] = wechat

    # 标记配置完成
    cfg["setup_status"] = "configured"
    cfg["brand"] = brand

    save_config(cfg)

    print("\n下一步：")
    print("  1. 运行门禁:  python3 scripts/preflight.py")
    print("  2. 开始写文章")


if __name__ == "__main__":
    main()
