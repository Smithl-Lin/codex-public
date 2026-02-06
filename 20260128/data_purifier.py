# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# Data Purifier V4.0 — 输出节点重构为 AGID 体系

import json
import os
import hashlib

# ------------------------------------------------------------------------------
# AGID 体系
# ------------------------------------------------------------------------------
def to_agid(namespace: str, node_type: str, raw_id) -> str:
    sid = hashlib.sha256(f"{namespace}:{node_type}:{raw_id}".encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


def strategic_purification():
    print("🧹 启动 20,000 项资产库‘战略清洗’程序 (V4.0 AGID)...")

    input_file = "merged_data.json"
    output_file = "merged_data_cleaned.json"

    if not os.path.exists(input_file):
        print(f"❌ 错误: 未找到 {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    initial_count = len(raw_data)
    noise_keywords = [
        "Nursing Care", "General Support", "Mechanical Ventilation",
        "ICU Care", "Intensive Care Unit", "Primary Care",
        "Standard of Care", "Educational Program", "Exercise Program",
        "Home Care", "Social Support", "Caregiver Support",
        "Hospital Management", "Quality of Life Survey"
    ]

    cleaned_data = []
    removed_count = 0

    for item in raw_data:
        title = item.get("title", "").lower()
        criteria = item.get("criteria", "").lower()
        category = item.get("category", "")
        is_noise = any(noise.lower() in title for noise in noise_keywords)
        if category in ["Regenerative", "Neurology"]:
            if "icu" in title or "ventilation" in title:
                is_noise = True
        core_tech_anchors = ["ips", "bci", "dbs", "stem cell", "neural", "robotic"]
        has_core_tech = any(tech in title or tech in criteria for tech in core_tech_anchors)

        if is_noise and not has_core_tech:
            removed_count += 1
        else:
            # V4.0: 每条保留记录附加 AGID
            raw_id = item.get("id", id(item))
            item["agid"] = to_agid("PURIFY", "ASSET", str(raw_id))
            cleaned_data.append(item)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    run_agid = to_agid("PURIFY", "RUN", f"{initial_count}_{len(cleaned_data)}_{removed_count}")
    print(f"✅ 清洗完成 (V4.0 AGID)!")
    print(f"📊 本批次 AGID: {run_agid}")
    print(f"📊 原始数据: {initial_count} 项")
    print(f"🗑️ 剔除负样本: {removed_count} 项")
    print(f"💎 纯净资产库: {len(cleaned_data)} 项")


if __name__ == "__main__":
    strategic_purification()
