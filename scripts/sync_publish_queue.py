#!/usr/bin/env python3
"""
08→09 发布队列自动流转脚本

从 08 精选生产池中筛选「可发布」的记录，自动写入 09 发布队列。
同时更新 08 表的生产状态为「已入发布队列」。

用法：
  python3 sync_publish_queue.py              # 同步所有可发布的
  python3 sync_publish_queue.py --dry-run    # 只预览不写入
"""

import argparse
import json
import subprocess
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_CFG = load_config()
_FEISHU = _CFG.get("feishu", {})
BASE_TOKEN = _FEISHU.get("base_token", "")
AS_IDENTITY = _FEISHU.get("as_identity", "bot")
TABLE_POOL = _FEISHU.get("table_pool", "")        # 08
TABLE_PUBLISH = _FEISHU.get("table_publish", "")   # 09


def lark_cmd(args):
    cmd = ["lark-cli", "base"] + args + ["--as", AS_IDENTITY]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return result.stdout


def parse_table(output):
    lines = output.strip().split("\n")
    records = []
    header = None
    for line in lines:
        if line.startswith("| _record_id"):
            header = [c.strip() for c in line.split("|")[1:-1]]
        elif line.startswith("| rec") and header:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) == len(header):
                records.append(dict(zip(header, cols)))
    return records


def clean_select(val):
    if not val:
        return ""
    val = val.strip()
    if val.startswith("[") and val.endswith("]"):
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list) and len(parsed) == 1:
                return parsed[0]
            return parsed
        except:
            pass
    return val.strip('"')


def fetch_all(table_id):
    records = []
    page_token = None
    while True:
        cmd = ["+record-list", "--base-token", BASE_TOKEN, "--table-id", table_id, "--page-size", "200"]
        if page_token:
            cmd += ["--page-token", page_token]
        output = lark_cmd(cmd)
        batch = parse_table(output)
        records.extend(batch)
        if "has_more=true" not in output:
            break
        m = re.search(r'page_token=(\S+)', output)
        if m:
            page_token = m.group(1)
        else:
            break
    return records


def create_record(table_id, fields):
    fields_json = json.dumps(fields, ensure_ascii=False)
    output = lark_cmd([
        "+record-upsert",
        "--base-token", BASE_TOKEN,
        "--table-id", table_id,
        "--json", fields_json,
    ])
    return '"ok": true' in output


def update_record(table_id, record_id, fields):
    fields_json = json.dumps(fields, ensure_ascii=False)
    output = lark_cmd([
        "+record-upsert",
        "--base-token", BASE_TOKEN,
        "--table-id", table_id,
        "--record-id", record_id,
        "--json", fields_json,
    ])
    return '"ok": true' in output


def main():
    parser = argparse.ArgumentParser(description="08→09 发布队列同步")
    parser.add_argument("--dry-run", action="store_true", help="只预览不写入")
    args = parser.parse_args()

    # 1. 获取 08 表所有记录
    print("📋 读取 08 精选生产池...")
    pool_records = fetch_all(TABLE_POOL)
    print(f"   总记录: {len(pool_records)}")

    # 2. 获取 09 表已有记录（防重复）
    print("\n📋 读取 09 发布队列...")
    publish_records = fetch_all(TABLE_PUBLISH)
    existing_titles = set()
    for r in publish_records:
        title = r.get("发布标题", "").strip()
        if title:
            existing_titles.add(title)
    print(f"   已有: {len(existing_titles)} 条")

    # 3. 筛选可发布的：素材状态=可写 且 优先级=P0-先写
    to_publish = []
    for r in pool_records:
        material_status = clean_select(r.get("素材状态", ""))
        priority = clean_select(r.get("优先级", ""))
        prod_status = clean_select(r.get("生产状态", ""))
        title = r.get("选题标题", "").strip()

        # 同步条件：可写 + P0优先级 + 还没入过发布队列
        if (material_status == "可写"
                and "P0" in priority
                and title
                and title not in existing_titles
                and prod_status not in ["已入发布队列", "已发布"]):
            to_publish.append(r)

    print(f"\n📤 待同步: {len(to_publish)} 条")

    if not to_publish:
        print("   没有需要同步的记录")
        return

    # 4. 同步到 09
    success = 0
    for item in to_publish:
        title = item.get("选题标题", "")
        article_type = clean_select(item.get("文章类型", ""))
        column = clean_select(item.get("所属栏目", ""))
        reader = clean_select(item.get("目标读者", ""))
        pool_id = item.get("_record_id", "")

        # 计算计划发布日（下周一/三/五）
        today = datetime.now()
        days_until_next = (7 - today.weekday()) % 7
        if days_until_next == 0:
            days_until_next = 3
        publish_date = (today + timedelta(days=days_until_next)).strftime("%Y-%m-%d")

        fields = {
            "发布标题": title,
            "对应精选选题": pool_id,
            "计划发布日": publish_date,
            "发布渠道": "公众号",
            "稿件状态": "待生成",
            "审核重点": "1.禁用词 2.数据真实性 3.CTA合规",
        }

        if args.dry_run:
            print(f"   [预览] {title[:40]} → {publish_date}")
            success += 1
        else:
            if create_record(TABLE_PUBLISH, fields):
                # 更新 08 表状态
                update_record(TABLE_POOL, pool_id, {"生产状态": "已入发布队列"})
                print(f"   ✅ {title[:40]}")
                success += 1
            else:
                print(f"   ❌ {title[:40]}")

    print(f"\n{'预览' if args.dry_run else '同步'}完成: {success}/{len(to_publish)}")


if __name__ == "__main__":
    main()
