#!/usr/bin/env python3
"""
执行前门禁检查 v2：验证 16 表 + 所有前置条件。

用法：
  python3 preflight.py
  python3 preflight.py --check-wechat    # 额外检查微信代理
  python3 preflight.py --check-atoms     # 额外检查原子库数据量
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"❌ 配置文件不存在: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


CFG = load_config()
BRAND = CFG.get("brand", {})
FEISHU = CFG.get("feishu", {})
FEISHU_ENABLED = FEISHU.get("enabled", False)
BASE_TOKEN = FEISHU.get("base_token", "")
TABLES = FEISHU.get("tables", {})
IMAGE_API = CFG.get("image_api", {})
WECHAT = CFG.get("wechat_proxy", {})
HTML_STYLE = CFG.get("html_template", {}).get("style_name", "")


def check(name, ok, detail=""):
    status = "✅" if ok else "❌"
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))
    return ok


def run_cmd(cmd, timeout=15):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def count_records(table_id):
    """获取表记录数"""
    ok, out = run_cmd([
        "lark-cli", "base", "+record-list",
        "--base-token", BASE_TOKEN,
        "--table-id", table_id,
        "--as", FEISHU.get("as_identity", "bot"),
        "--page-size", "1"
    ])
    if not ok:
        return -1
    # 从 Meta 行提取 count
    for line in out.split("\n"):
        if line.startswith("Meta:"):
            import re
            m = re.search(r'count=(\d+)', line)
            if m:
                return int(m.group(1))
    return 0


def main():
    parser = argparse.ArgumentParser(description="执行前门禁检查")
    parser.add_argument("--check-wechat", action="store_true", help="检查微信代理连通性")
    parser.add_argument("--check-atoms", action="store_true", help="检查原子库数据量")
    args = parser.parse_args()

    print("=" * 50)
    print("Preflight Check v2 — 16 表门禁")
    print("=" * 50)

    all_ok = True

    # [0] config 核心字段
    print("\n[0/7] config.json 核心字段")
    all_ok &= check("brand.brand_name", bool(BRAND.get("brand_name")))
    all_ok &= check("setup_status = configured", CFG.get("setup_status") == "configured")
    all_ok &= check("html_template.style_name", bool(HTML_STYLE))
    if not all_ok:
        print("\n❌ config.json 必填字段缺失", file=sys.stderr)
        return 1

    # [1] 16 表 ID 配置
    print("\n[1/7] 飞书 16 表配置")
    required_tables = ["rules", "atom", "template", "pool", "publish", "topic",
                       "source", "process", "problem", "opinion", "reform", "case",
                       "visual", "collect", "clean_index", "delete_verify"]
    for tname in required_tables:
        tid = TABLES.get(tname, "")
        all_ok &= check(f"tables.{tname}", bool(tid), tid[:20] if tid else "未配置")

    if not FEISHU_ENABLED:
        check("飞书模块", True, "未启用，跳过后续飞书检查")
        print("\n" + "=" * 50)
        print("✅ 门禁通过（飞书未启用）" if all_ok else "❌ 门禁未通过")
        return 0 if all_ok else 1

    # [2] 飞书连接
    print("\n[2/7] 飞书连接")
    if BASE_TOKEN:
        test_tid = TABLES.get("pool", list(TABLES.values())[0] if TABLES else "")
        ok, out = run_cmd([
            "lark-cli", "base", "+record-list",
            "--base-token", BASE_TOKEN,
            "--table-id", test_tid,
            "--as", FEISHU.get("as_identity", "bot"),
            "--page-size", "1"
        ])
        all_ok &= check("飞书 Base 可访问", ok, "" if ok else out[:80])
    else:
        all_ok &= check("base_token", False, "为空")

    # [3] GPT Image 2 API
    print("\n[3/7] GPT Image 2 API")
    key_env = IMAGE_API.get("key_env", "GPT_IMAGE2_API_KEY")
    api_key = os.environ.get(key_env, "")
    if not api_key:
        env_path = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith(f"{key_env}="):
                        api_key = line.strip().split("=", 1)[1]
    has_key = bool(api_key and len(api_key) > 10)
    all_ok &= check(f"{key_env}", has_key,
                     f"{api_key[:8]}...{api_key[-4:]}" if has_key else "未找到")
    all_ok &= check("endpoint", bool(IMAGE_API.get("endpoint")))

    # [4] 微信代理
    print("\n[4/7] 微信代理")
    if WECHAT.get("enabled"):
        server_ip = WECHAT.get("server_ip", "")
        port = WECHAT.get("proxy_port", 8787)
        all_ok &= check("server_ip 已配置", bool(server_ip), f"{server_ip}:{port}")

        if args.check_wechat and server_ip:
            import urllib.request
            try:
                resp = urllib.request.urlopen(
                    f"http://{server_ip}:{port}/health", timeout=5
                )
                health = json.loads(resp.read())
                all_ok &= check("wx-proxy /health", health.get("status") == "ok")
            except Exception as e:
                all_ok &= check("wx-proxy /health", False, str(e)[:50])
    else:
        check("微信代理", True, "未启用，跳过")

    # [5] 工具依赖
    print("\n[5/7] 工具依赖")
    try:
        import PIL
        check("Pillow", True, f"v{PIL.__version__}")
    except ImportError:
        all_ok &= check("Pillow", False, "pip install Pillow")

    try:
        import requests
        check("requests", True)
    except ImportError:
        all_ok &= check("requests", False, "pip install requests")

    if FEISHU_ENABLED:
        ok, out = run_cmd(["lark-cli", "--version"])
        check("lark-cli", ok, out.strip()[:30] if ok else "")

    # 配图依赖
    guizang_mat = os.path.expanduser("~/.hermes/skills/guizang-material-illustration")
    check("guizang-material-illustration", os.path.isdir(guizang_mat))

    # 脚本文件
    scripts_dir = Path(__file__).parent
    for script in ["assemble_atoms.py", "sync_publish_queue.py", "build_html.py",
                    "postflight.py", "generate_image.py", "push_draft.py"]:
        check(f"scripts/{script}", (scripts_dir / script).exists())

    # [6] 排版风格
    print("\n[6/7] 排版风格")
    styles = CFG.get("html_styles", {})
    all_ok &= check(f"style '{HTML_STYLE}'", HTML_STYLE in styles)

    # [7] 关键表数据量（可选）
    if args.check_atoms:
        print("\n[7/7] 关键表数据量")
        critical_tables = {
            "rules": "00取料规则",
            "atom": "13原子库",
            "template": "14题材模板",
            "pool": "08精选池",
            "publish": "09发布队列",
        }
        for tkey, tdesc in critical_tables.items():
            tid = TABLES.get(tkey, "")
            if tid:
                count = count_records(tid)
                has_data = count > 0
                all_ok &= check(f"{tdesc}({tkey})", has_data, f"{count}条")
            else:
                all_ok &= check(f"{tdesc}({tkey})", False, "table_id 未配置")
    else:
        print("\n[7/7] 关键表数据量 — 跳过（加 --check-atoms 检查）")

    # 总结
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ 门禁通过，可以开始执行")
    else:
        print("❌ 门禁未通过，请修复上述问题后重试")
    print("=" * 50)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
