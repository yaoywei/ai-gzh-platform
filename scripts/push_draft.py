#!/usr/bin/env python3
"""推草稿到公众号 - 通过wx-proxy代理，双环境兼容"""
import json, sys, os, re, subprocess

# 双环境兼容
try:
    from coze_workload_identity import requests as http_client
except ImportError:
    import requests as http_client

# 从环境变量读取配置
PROXY = f"http://{os.getenv('WX_PROXY_SERVER', '')}:{os.getenv('WX_PROXY_PORT', '8787')}"
AUTH_TOKEN = os.getenv('WX_PROXY_TOKEN', '')
APPID = os.getenv('WX_APPID', '')
APPSECRET = os.getenv('WX_APPSECRET', '')


def api_call(path, data=None, method="GET"):
    import json as _json
    url = f"{PROXY}{path}"
    headers = {"x-publish-token": AUTH_TOKEN}
    if data:
        headers["Content-Type"] = "application/json; charset=utf-8"
    try:
        if method == "GET":
            resp = http_client.get(url, headers=headers, timeout=30)
        else:
            # CRITICAL: ensure_ascii=False so Chinese content is sent as raw UTF-8
            # bytes, not \\uXXXX escape sequences. Using `json=data` triggers
            # ensure_ascii=True which causes WeChat to display raw \\uXXXX literals
            # in the draft editor (verified bug 2026-07-02).
            body = _json.dumps(data, ensure_ascii=False).encode("utf-8")
            resp = http_client.post(url, headers=headers, data=body, timeout=30)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def upload_img(access_token, file_path):
    """上传文章内图片（用curl因为需要multipart）"""
    url = f"{PROXY}/cgi-bin/media/uploadimg?access_token={access_token}"
    r = subprocess.run(["curl", "-s", "-X", "POST", url,
                       "-H", f"x-publish-token: {AUTH_TOKEN}",
                       "-F", f"media=@{file_path}"],
                      capture_output=True, text=True)
    return json.loads(r.stdout)


def upload_material(access_token, file_path):
    """上传永久素材（封面图）"""
    url = f"{PROXY}/cgi-bin/material/add_material?access_token={access_token}&type=image"
    r = subprocess.run(["curl", "-s", "-X", "POST", url,
                       "-H", f"x-publish-token: {AUTH_TOKEN}",
                       "-F", f"media=@{file_path}"],
                      capture_output=True, text=True)
    return json.loads(r.stdout)


def push_draft(title, author, digest, html_path, cover_path, img_paths):
    """推送草稿到公众号"""
    # 1. 获取token
    print("1. 获取access_token...")
    token_resp = api_call(f"/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}")
    if "access_token" not in token_resp:
        print(f"token失败: {token_resp}"); sys.exit(1)
    at = token_resp["access_token"]
    print("token获取成功")

    # 2. 上传封面图
    print("2. 上传封面图(永久素材)...")
    cover_resp = upload_material(at, cover_path)
    if "media_id" not in cover_resp:
        print(f"封面图失败: {cover_resp}"); sys.exit(1)
    thumb_media_id = cover_resp["media_id"]
    print(f"thumb_media_id: {thumb_media_id}")

    # 3. 上传所有图片
    print("3. 上传图片(文章内)...")
    wx_urls = {}
    for f in img_paths:
        resp = upload_img(at, f)
        if "url" in resp:
            wx_urls[f] = resp["url"]
            print(f"  {f} OK")
        else:
            print(f"  {f} FAIL: {resp}")

    # 4. 替换HTML中的base64
    print("4. 处理HTML...")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Pattern 1: base64 inline images (微信粘贴版)
    base64_pattern = r'<img[^>]*src="(data:image/[^"]+)"[^>]*>'
    matches = list(re.finditer(base64_pattern, html))

    for i, match in enumerate(matches):
        if i < len(img_paths) and img_paths[i] in wx_urls:
            html = html.replace(match.group(1), wx_urls[img_paths[i]], 1)
            print(f"  替换第{i+1}张(base64): {img_paths[i]}")

    # Pattern 2: relative-path images like imgs/01.jpg (推草稿版)
    rel_pattern = r'<img[^>]*src="(imgs/[^"]+)"[^>]*>'
    rel_matches = list(re.finditer(rel_pattern, html))

    for match in rel_matches:
        rel_path = match.group(1)
        # Try to match against img_paths by basename
        rel_basename = os.path.basename(rel_path)
        for full_path in img_paths:
            if os.path.basename(full_path) == rel_basename and full_path in wx_urls:
                html = html.replace(rel_path, wx_urls[full_path], 1)
                print(f"  替换(rel): {rel_path} → {wx_urls[full_path][:60]}...")
                break

    remaining_b64 = len(re.findall(base64_pattern, html))
    remaining_rel = len(re.findall(rel_pattern, html))
    print(f"  残留base64: {remaining_b64}, 残留相对路径: {remaining_rel}, 处理后: {len(html)} bytes")

    # 5. 创建草稿
    print("5. 创建草稿...")
    article_data = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": html,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]
    }

    draft_resp = api_call(f"/cgi-bin/draft/add?access_token={at}", data=article_data, method="POST")
    if "media_id" in draft_resp:
        print(f"草稿创建成功！media_id: {draft_resp['media_id']}")
    else:
        print(f"草稿创建失败: {draft_resp}"); sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--author", default="")
    parser.add_argument("--digest", default="")
    parser.add_argument("--html", required=True)
    parser.add_argument("--cover", required=True)
    parser.add_argument("--images", nargs="+", required=True)
    args = parser.parse_args()
    push_draft(args.title, args.author, args.digest, args.html, args.cover, args.images)
