#!/usr/bin/env python3
"""
原子组装脚本 v2：按 00 取料规则从 13 可独立取料原子库拉取原子。
按 14 题材组合模板组装，从 08 精选生产池选题。

用法：
  python3 assemble_atoms.py --pool-id recXXXX      # 从08精选生产池选一条
  python3 assemble_atoms.py --topic "选题关键词"     # 按关键词匹配08表
  python3 assemble_atoms.py --template "实战复盘"    # 按14模板取料

输出：JSON文件，包含选题信息+规则+原子+模板
"""

import argparse
import json
import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"❌ 配置文件不存在: {CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_CFG = load_config()
_FEISHU = _CFG.get("feishu", {})
BASE_TOKEN = _FEISHU.get("base_token", "")
AS_IDENTITY = _FEISHU.get("as_identity", "bot")

# 表 ID
TABLE_RULES = _FEISHU.get("table_rules", "")       # 00
TABLE_ATOM = _FEISHU.get("table_atom", "")          # 13
TABLE_TEMPLATE = _FEISHU.get("table_template", "")  # 14
TABLE_POOL = _FEISHU.get("table_pool", "")          # 08
TABLE_TOPIC = _FEISHU.get("table_topic", "")        # 07
TABLE_VISUAL = _FEISHU.get("table_visual", "")      # 15


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
    """清理 select 字段的 [\"value\"] 格式"""
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
    return val.strip('"\'')


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


# === Phase 1: 读取取料规则 ===
def load_rules():
    """从 00 表加载取料规则"""
    records = fetch_all(TABLE_RULES)
    rules = []
    for r in records:
        rules.append({
            "name": r.get("规则名称", ""),
            "适用表": r.get("适用表", ""),
            "取料条件": r.get("取料条件", ""),
            "Hermes动作": r.get("Hermes动作", ""),
            "禁用条件": r.get("禁用条件", ""),
            "用途": r.get("用途", ""),
        })
    return rules


# === Phase 2: 从 08 精选生产池选题 ===
def get_pool_item(pool_id=None, keyword=None):
    records = fetch_all(TABLE_POOL)
    for r in records:
        rid = r.get("_record_id", "")
        title = r.get("选题标题", "")
        status = clean_select(r.get("素材状态", ""))
        prod_status = clean_select(r.get("生产状态", ""))

        if pool_id and rid == pool_id:
            return r
        if keyword and keyword in title:
            return r

    return None


# === Phase 3: 从 14 表读题材模板 ===
def get_template(template_name=None, topic_type=None):
    records = fetch_all(TABLE_TEMPLATE)
    for r in records:
        status = clean_select(r.get("模板状态", ""))
        if status != "启用":
            continue
        name = r.get("题材模板", "")
        t_type = clean_select(r.get("题材类型", ""))

        if template_name and template_name in name:
            return r
        if topic_type and topic_type == t_type:
            return r

    # 返回第一个启用的模板
    for r in records:
        if clean_select(r.get("模板状态", "")) == "启用":
            return r
    return None


# === Phase 4: 从 13 表按规则取料 ===
def fetch_atoms(template, rules):
    """按模板配方和规则从 13 表取料"""
    all_atoms = fetch_all(TABLE_ATOM)

    # 解析模板的原子配方
    recipe = template.get("原子配方", "") if template else ""
    recipe_types = []
    if recipe:
        try:
            recipe_types = json.loads(recipe)
        except:
            recipe_types = [t.strip() for t in recipe.strip("[]").split(",")]

    # 解析推荐标签
    rec_tags = template.get("推荐标签", "") if template else ""
    try:
        rec_tags_list = json.loads(rec_tags) if rec_tags else []
    except:
        rec_tags_list = [t.strip() for t in rec_tags.strip("[]").split(",") if t.strip()]

    # 解析禁用标签
    ban_tags = template.get("禁用标签", "") if template else ""
    try:
        ban_tags_list = json.loads(ban_tags) if ban_tags else []
    except:
        ban_tags_list = [t.strip() for t in ban_tags.strip("[]").split(",") if t.strip()]

    # 每篇建议原子数
    try:
        max_atoms = int(template.get("每篇建议原子数", "8")) if template else 8
    except:
        max_atoms = 8

    # 筛选合格原子
    selected = []
    for atom in all_atoms:
        # 必须是可直接取料
        usage_status = clean_select(atom.get("Hermes使用状态", ""))
        if usage_status != "可直接取料":
            continue

        # 证据等级必须是 A 或 B
        evidence = clean_select(atom.get("证据等级", ""))
        if evidence not in ["A-可引用事实", "B-可用观点/方法"]:
            continue

        # 检查禁用标签
        atom_tags = atom.get("适用标签", "")
        try:
            atom_tags_list = json.loads(atom_tags) if atom_tags else []
        except:
            atom_tags_list = []

        if any(bt in atom_tags_list for bt in ban_tags_list):
            continue

        # 检查模板的原子类型匹配
        atom_type = clean_select(atom.get("原子类型", ""))
        if recipe_types and atom_type not in recipe_types:
            # 也检查是否在模板的适用栏目中
            pass

        selected.append(atom)

    # 按证据等级排序：A > B
    def evidence_key(a):
        ev = clean_select(a.get("证据等级", ""))
        if "A" in ev:
            return 0
        elif "B" in ev:
            return 1
        return 2

    selected.sort(key=evidence_key)

    # 按类型分组，每种类型取1-2条，确保多样性
    by_type = {}
    for atom in selected:
        t = clean_select(atom.get("原子类型", "其他"))
        by_type.setdefault(t, []).append(atom)

    # 每种类型按证据等级排序
    for t in by_type:
        by_type[t].sort(key=evidence_key)

    result = []
    has_boundary = False

    # 第一轮：每种类型取1条
    for t, atoms_of_type in by_type.items():
        if len(result) >= max_atoms:
            break
        if t == "边界":
            has_boundary = True
        result.append(atoms_of_type[0])

    # 第二轮：如果还有余量，从高证据等级的补
    if len(result) < max_atoms:
        used_ids = {a.get("_record_id") for a in result}
        for atom in selected:
            if len(result) >= max_atoms:
                break
            if atom.get("_record_id") not in used_ids:
                result.append(atom)
                used_ids.add(atom.get("_record_id"))

    # 确保有边界原子
    if not has_boundary:
        for atom in selected:
            if clean_select(atom.get("原子类型", "")) == "边界":
                result.append(atom)
                break

    return result[:max_atoms]


# === Phase 5: 从 15 表取视觉素材 ===
def fetch_visuals(pool_item):
    """从 15 表取关联视觉素材"""
    if not pool_item:
        return []

    visual_ref = pool_item.get("关联视觉素材", "")
    if not visual_ref or visual_ref in ["", "null", "[]"]:
        return []

    # 解析关联的 record_id
    try:
        refs = json.loads(visual_ref)
        if isinstance(refs, list):
            ref_ids = [r.get("id", "") if isinstance(r, dict) else str(r) for r in refs]
        else:
            ref_ids = [str(refs)]
    except:
        ref_ids = []

    if not ref_ids:
        return []

    all_visuals = fetch_all(TABLE_VISUAL)
    return [v for v in all_visuals if v.get("_record_id", "") in ref_ids]


# === 主流程 ===
def main():
    parser = argparse.ArgumentParser(description="按取料规则组装原子")
    parser.add_argument("--pool-id", help="08精选生产池的 record_id")
    parser.add_argument("--topic", help="选题关键词，匹配08表")
    parser.add_argument("--template", help="14题材模板名称或类型")
    parser.add_argument("--output", help="输出JSON路径")
    args = parser.parse_args()

    # 1. 加载规则
    print("📋 加载取料规则...")
    rules = load_rules()
    print(f"   {len(rules)} 条规则")

    # 2. 选题
    print("\n📌 选题...")
    pool_item = get_pool_item(args.pool_id, args.topic)
    if pool_item:
        topic_title = pool_item.get("选题标题", "?")
        topic_type = clean_select(pool_item.get("文章类型", ""))
        print(f"   选中: {topic_title}")
        print(f"   类型: {topic_type}")
    else:
        print("   ⚠️ 未找到匹配的精选选题，使用通用模板")
        topic_title = args.topic or "通用选题"
        topic_type = ""

    # 3. 读模板
    print("\n📐 读取题材模板...")
    template = get_template(args.template, topic_type)
    if template:
        print(f"   模板: {template.get('题材模板', '?')}")
        print(f"   原子配方: {template.get('原子配方', '?')}")
        print(f"   每篇建议: {template.get('每篇建议原子数', '?')} 条")
    else:
        print("   ⚠️ 未找到启用的模板，使用默认取料")

    # 4. 取料
    print("\n🔬 从13表按规则取料...")
    atoms = fetch_atoms(template, rules)
    print(f"   获取 {len(atoms)} 条原子")

    # 按类型统计
    type_counts = {}
    for a in atoms:
        t = clean_select(a.get("原子类型", "其他"))
        type_counts[t] = type_counts.get(t, 0) + 1
    for t, c in sorted(type_counts.items()):
        print(f"     {t}: {c}")

    # 5. 视觉素材
    print("\n🎨 获取视觉素材...")
    visuals = fetch_visuals(pool_item)
    print(f"   {len(visuals)} 条视觉素材")

    # 6. 组装输出
    result = {
        "选题": {
            "标题": topic_title,
            "类型": topic_type,
            "来源": "08精选生产池" if pool_item else "手动指定",
            "record_id": pool_item.get("_record_id", "") if pool_item else "",
        },
        "取料规则": rules,
        "题材模板": {
            "名称": template.get("题材模板", "") if template else "",
            "原子配方": template.get("原子配方", "") if template else "",
            "文章结构": template.get("文章结构", "") if template else "",
            "CTA方式": template.get("CTA方式", "") if template else "",
            "事实边界": template.get("事实边界", "") if template else "",
        } if template else {},
        "原子": atoms,
        "视觉素材": visuals,
        "统计": {
            "原子数": len(atoms),
            "视觉素材数": len(visuals),
            "有边界原子": any(clean_select(a.get("原子类型", "")) == "边界" for a in atoms),
            "证据等级分布": {
                "A": sum(1 for a in atoms if "A" in clean_select(a.get("证据等级", ""))),
                "B": sum(1 for a in atoms if "B" in clean_select(a.get("证据等级", ""))),
            },
            "组装时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    }

    # 7. 输出
    if args.output:
        output_path = args.output
    else:
        slug = topic_title[:20].replace(" ", "-").replace("：", "-").replace("?", "")
        date = datetime.now().strftime("%Y-%m-%d")
        output_dir = os.path.expanduser(f"~/.hermes/skills/kunpeng-gzh-platform/output/{date}-{slug}")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "atoms.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 原子组装完成: {output_path}")
    print(f"   原子: {len(atoms)} 条")
    print(f"   视觉: {len(visuals)} 条")
    print(f"   规则: {len(rules)} 条")

    return result


if __name__ == "__main__":
    main()
