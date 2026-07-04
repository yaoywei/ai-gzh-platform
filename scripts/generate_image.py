#!/usr/bin/env python3
"""
GPT Image 2 图片生成脚本
双环境兼容：Coze沙箱 / Hermes / OpenClaw / 任意Python环境

用法：
  python generate_image.py --prompt "你的prompt" --size "1792x768" --output "cover.png"

配置：
  - API endpoint和model从同目录上级的config.json读取
  - API Key从环境变量读取（变量名在config.json的image_api.key_env中指定）

依赖：
  pip install requests
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 双环境兼容：Coze沙箱用coze_workload_identity，其他环境用标准requests
try:
    from coze_workload_identity import requests as http_client
except ImportError:
    import requests as http_client


def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        print(f"⚠️ 配置文件不存在: {config_path}", file=sys.stderr)
        print("请从 config.example.json 复制并填写", file=sys.stderr)
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_image(prompt: str, size: str, output: str, n: int = 1) -> str:
    """调用 GPT Image 2 API 生成图片"""
    config = load_config()
    api_config = config["image_api"]

    # 从环境变量读取 API Key（变量名在config.json中配置）
    api_key = os.getenv(api_config["key_env"])
    if not api_key:
        print(f"⚠️ 环境变量 {api_config['key_env']} 未设置", file=sys.stderr)
        sys.exit(1)

    endpoint = api_config["endpoint"]
    model = api_config["model"]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": size,
    }

    # 发起请求（指数退避重试：2s → 4s → 8s，共 3 次）
    import time

    max_retries = 3
    result = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🎨 生成图片中... (model={model}, size={size}, attempt={attempt}/{max_retries})")
            resp = http_client.post(endpoint, json=payload, headers=headers, timeout=300)
            resp.raise_for_status()
            result = resp.json()
            break
        except http_client.exceptions.HTTPError as e:
            body = e.response.text if e.response else ""
            status = e.response.status_code if e.response else 0
            # 4xx 不重试（401/403/422 是配置错误），429 除外
            if 400 <= status < 500 and status != 429:
                print(f"❌ API请求失败: HTTP {status} - {body}", file=sys.stderr)
                sys.exit(1)
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"⚠️ HTTP {status}, {wait}s 后重试...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"❌ API请求失败(已重试{max_retries}次): HTTP {status} - {body}", file=sys.stderr)
                sys.exit(1)
        except http_client.exceptions.ConnectionError as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"⚠️ 网络连接失败, {wait}s 后重试... ({e})", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"❌ 网络连接失败(已重试{max_retries}次): {e}", file=sys.stderr)
                sys.exit(1)
        except http_client.exceptions.Timeout:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"⚠️ 请求超时(300s), {wait}s 后重试...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"❌ 请求超时(已重试{max_retries}次, 300s/次)", file=sys.stderr)
                sys.exit(1)

    # 解析结果：兼容 url 与 b64_json 两种 OpenAI-compatible 图片返回形态
    if result is None or "data" not in result or not result["data"]:
        print(f"❌ API返回异常: {json.dumps(result, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)

    item = result["data"][0]
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if item.get("b64_json"):
        try:
            import base64
            output_path.write_bytes(base64.b64decode(item["b64_json"]))
            file_size = output_path.stat().st_size
            print(f"✅ 图片已保存: {output_path} ({file_size:,} bytes, from b64_json)")
            return str(output_path)
        except Exception as e:
            print(f"❌ b64_json 解码失败: {e}", file=sys.stderr)
            sys.exit(1)

    image_url = item.get("url")
    if not image_url:
        print("❌ 返回数据中无图片URL或b64_json", file=sys.stderr)
        sys.exit(1)

    # 下载图片
    try:
        print(f"⬇️ 下载图片到: {output_path}")
        img_resp = http_client.get(image_url, timeout=60)
        img_resp.raise_for_status()
        output_path.write_bytes(img_resp.content)
        file_size = output_path.stat().st_size
        print(f"✅ 图片已保存: {output_path} ({file_size:,} bytes)")
        return str(output_path)
    except Exception as e:
        print(f"❌ 下载失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="GPT Image 2 图片生成")
    parser.add_argument("--prompt", required=True, help="图片生成prompt")
    parser.add_argument("--size", default="1792x768", help="图片尺寸 (默认: 1792x768)")
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument("--n", type=int, default=1, help="生成数量 (默认: 1)")

    args = parser.parse_args()
    generate_image(args.prompt, args.size, args.output, args.n)


if __name__ == "__main__":
    main()
