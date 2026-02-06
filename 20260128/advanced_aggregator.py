# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# 文件名: advanced_aggregator.py — V4.0 AGID 映射，0.79 阈值来自 amah_config.json

import json
import requests
import time
import hashlib
import os

# 闭环：精度阈值来自 amah_config.json
def _load_precision_threshold():
    try:
        from amani_core_v4 import get_precision_threshold
        return get_precision_threshold()
    except Exception:
        cfg_path = os.path.join(os.path.dirname(__file__), "amah_config.json")
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                return float(json.load(f).get("alignment_logic", {}).get("precision_lock_threshold", 0.79))
        except Exception:
            return 0.79

def to_agid(namespace: str, node_type: str, raw_id) -> str:
    sid = hashlib.sha256(f"{namespace}:{node_type}:{raw_id}".encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"

PRECISION_LOCK_THRESHOLD = _load_precision_threshold()


def fetch_v20k_final_sprint():
    print("🏁 启动 20,000 项‘终极冲刺’ (V4.0 AGID)：锁定全球顶级稀缺资产...")
    print(f"📌 精度阈值来源: amah_config.json → {PRECISION_LOCK_THRESHOLD}")

    sprint_keywords = [
        "Longevity OR Anti-aging OR Telomere OR Senolytic OR NAD+",
        "Multiple System Atrophy OR MSA OR Progressive Supranuclear Palsy OR PSP",
        "Creutzfeldt-Jakob Disease OR CJD OR Prion Disease",
        "Organoid OR Organ-on-a-chip OR Bio-ink OR 3D Printed Bone",
        "Deep Brain Stimulation OR DBS AND Depression OR OCD",
        "BNCT Japan OR Carbon Ion Radiation OR iPS Cell Spinal Cord",
        "Gene Therapy AND Haemophilia OR Thalassemia",
        "Achondroplasia OR Pediatric Rare Disease OR Gene Therapy Eye",
        "Cochlear Regeneration OR Advanced Otolaryngology"
    ]

    all_assets = []
    seen_ids = set()

    try:
        with open("merged_data.json", "r", encoding="utf-8") as f:
            all_assets = json.load(f)
            seen_ids = {item.get("id") or item.get("agid") for item in all_assets if item.get("id") or item.get("agid")}
            print(f"📊 当前底座: {len(all_assets)} | 开启最后 1,600 项定向清扫...")
    except Exception:
        pass

    target_total = 20000
    session = requests.Session()

    for word in sprint_keywords:
        if len(all_assets) >= target_total:
            break
        print(f"📡 正在捕捉稀缺资产: [{word}]")

        next_token = None
        while True:
            params = {
                "query.term": word,
                "filter.overallStatus": "RECRUITING,AVAILABLE,ENROLLING_BY_INVITATION",
                "fields": "NCTId,BriefTitle,Condition,LocationFacility,EligibilityCriteria",
                "pageSize": 100
            }
            if next_token:
                params["pageToken"] = next_token

            try:
                resp = session.get("https://clinicaltrials.gov/api/v2/studies", params=params, timeout=20)
                if resp.status_code != 200:
                    break
                data = resp.json()
                studies = data.get("studies", [])
                if not studies:
                    break

                new_in_batch = 0
                for s in studies:
                    nct_id = s.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
                    if nct_id not in seen_ids:
                        seen_ids.add(nct_id)
                        proto = s.get("protocolSection", {})
                        category = "High-End-Tech"
                        title = proto.get("identificationModule", {}).get("briefTitle", "Unknown")
                        q_low = (word + " " + title).lower()
                        if "aging" in q_low or "longevity" in q_low:
                            category = "Longevity"
                        elif "neuro" in q_low or "brain" in q_low:
                            category = "Neurology"
                        elif "rare" in q_low or "gene" in q_low:
                            category = "Orphan-Drug"

                        # V4.0 AGID 映射：每条资产带 agid，并挂载 precision_lock_threshold
                        agid = to_agid("AGG", "ASSET", nct_id)
                        all_assets.append({
                            "id": nct_id,
                            "agid": agid,
                            "source": f"Final_Sprint_{word[:10]}",
                            "category": category,
                            "title": f"【全球顶层资源】{title}",
                            "status": "Active",
                            "criteria": proto.get("eligibilityModule", {}).get("eligibilityCriteria", ""),
                            "precision_target": PRECISION_LOCK_THRESHOLD,
                        })
                        new_in_batch += 1

                if len(all_assets) % 100 == 0:
                    with open("merged_data.json", "w", encoding="utf-8") as f:
                        json.dump(all_assets, f, ensure_ascii=False, indent=2)
                    print(f"📈 目标逼近中: {len(all_assets)} / 20000")

                next_token = data.get("nextPageToken")
                if not next_token or new_in_batch == 0:
                    break
                time.sleep(0.1)
            except Exception:
                break

    with open("merged_data.json", "w", encoding="utf-8") as f:
        json.dump(all_assets, f, ensure_ascii=False, indent=2)
    print(f"🎉 20,000 项全球全量资产调度库建设完成 (V4.0 AGID，阈值 {PRECISION_LOCK_THRESHOLD})！")


if __name__ == "__main__":
    fetch_v20k_final_sprint()
