# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Phase 3: Sync L2 assets (merged_data, expert_map_data, hospital_center_assets) to ChromaDB.
Ensures semantic search has structured data. Run from 20260128 directory.
"""
import json
import os
import hashlib

def to_agid(namespace: str, node_type: str, raw_id) -> str:
    raw = f"{namespace}:{node_type}:{raw_id}"
    sid = hashlib.sha256(str(raw).encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"

def build_physical_node_registry(data_dir: str) -> list:
    """Build physical_node_registry from expert_map_data + hospital_center_assets."""
    registry = []
    base = data_dir or os.path.dirname(os.path.abspath(__file__))
    for name, namespace, key_id, key_name in [
        ("expert_map_data.json", "PI", "id", "name"),
        ("hospital_center_assets.json", "HOSP", "id", "name"),
    ]:
        path = os.path.join(base, name)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            nid = item.get(key_id) or item.get("agid") or str(len(registry))
            agid = item.get("agid") or to_agid(namespace, "NODE", nid)
            region = (item.get("region") or item.get("location", {}).get("state") or "NA").strip()
            if isinstance(region, dict):
                region = "NA"
            registry.append({
                "agid_or_id": agid,
                "agid": agid,
                "physical_node_id": nid,
                "region": region[:50],
                "endpoint": "",
            })
    return registry

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    registry = build_physical_node_registry(base)
    out_path = os.path.join(base, "physical_node_registry.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    print(f"Built physical_node_registry.json with {len(registry)} entries.")
    try:
        from amani_nexus_layer_v3 import NexusRouter
        router = NexusRouter(default_region="NA")
        n = router.auto_register(out_path)
        print(f"NexusRouter.auto_register loaded {n} mappings.")
    except Exception as e:
        print(f"NexusRouter.auto_register skip: {e}")

if __name__ == "__main__":
    main()
