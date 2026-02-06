# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Ingest global top 100 hospitals + lead experts/teams + representative clinical research.
Data: asset_library_l2/top100_hospitals_data.json (Newsweek/Statista World's Best Hospitals 2025 + extended).
Run from 20260128: python ingest_top100_hospitals.py
"""
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_LIB = os.path.join(SCRIPT_DIR, "asset_library_l2")
DATA_FILE = os.path.join(ASSET_LIB, "top100_hospitals_data.json")


def load_hospitals():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("hospitals", [])


def to_hospital_record(h):
    return {
        "id": h["id"],
        "name": h["name"],
        "affiliation": h.get("affiliation", ""),
        "region": h.get("region", "North America"),
        "country": h.get("country", ""),
        "city": h.get("city", ""),
        "state": h.get("state", ""),
        "specialty_focus": h.get("specialty_focus", []),
        "value_add_services": h.get("value_add_services", []),
    }


def to_expert_record(h, index):
    pid = f"pi_top_{index:03d}"
    specialties = h.get("specialty_focus", [])
    primary = specialties[0] if specialties else "Multi-Specialty"
    return {
        "id": pid,
        "name": f"{h['name'][:40]} - Lead Clinical Team",
        "affiliation": h["name"],
        "specialty": primary,
        "expertise_tags": specialties[:5] + ["Clinical-Trial", "International-Patient"],
        "insurance_partners": ["Medicare", "International-Private"],
        "value_add_services": h.get("value_add_services", []) or ["Hospital-Docking", "International-Patient-Desk"],
        "location": {
            "city": h.get("city", ""),
            "state": h.get("state", ""),
            "zip": "",
        },
        "linked_projects": [],
    }


def to_trial_records(hospitals, max_per_hospital=1):
    """Representative high-end / clinical research trials linked to top hospitals."""
    trials = []
    for i, h in enumerate(hospitals[:80]):
        tid = f"NCT_TOP_{i+1:04d}"
        specialties = h.get("specialty_focus", [])
        cat = specialties[0] if specialties else "Oncology"
        trials.append({
            "id": tid,
            "title": f"Clinical research and high-end program at {h['name'][:50]}",
            "status": "RECRUITING",
            "source": "AMANI_Top100",
            "category": cat,
            "criteria": f"Refer to {h['name']} international patient desk.",
        })
    return trials


def main():
    sys.path.insert(0, ASSET_LIB)
    import asset_ingest

    if not os.path.isfile(DATA_FILE):
        print(f"Missing {DATA_FILE}")
        return 1

    hospitals = load_hospitals()
    if not hospitals:
        print("No hospitals in data file.")
        return 1

    # 1) Hospitals
    hospital_records = [to_hospital_record(h) for h in hospitals]
    n_h, ids_h = asset_ingest.ingest_hospitals(hospital_records, data_dir=SCRIPT_DIR)
    print(f"Hospitals: added {n_h}; ids (first 5): {ids_h[:5]}")

    # 2) Experts / lead teams (one per hospital)
    expert_records = [to_expert_record(h, i + 1) for i, h in enumerate(hospitals)]
    n_p, ids_p = asset_ingest.ingest_pis(expert_records, data_dir=SCRIPT_DIR)
    print(f"Experts/teams: added {n_p}; ids (first 5): {ids_p[:5]}")

    # 3) Representative clinical research (placeholder trials linked to top hospitals)
    trial_records = to_trial_records(hospitals, max_per_hospital=1)
    n_t, ids_t = asset_ingest.ingest_trials(trial_records, data_dir=SCRIPT_DIR)
    print(f"Trials (representative): added {n_t}; ids (first 5): {ids_t[:5]}")

    print("\nDone. Regenerate physical node registry: python sync_l2_to_chromadb.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
