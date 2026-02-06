# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Load 0131global_medical_assets (CSV) and ingest into L2 asset library.
Maps: Trial -> merged_data.json; Center/Company -> hospital_center_assets.json.
"""
import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_FILE = os.path.join(SCRIPT_DIR, "0131global_medical_assets")
sys.path.insert(0, SCRIPT_DIR)
from asset_ingest import ingest_trials, ingest_hospitals


def _parse_location(loc: str):
    """Parse 'City, Country' or 'City, State' into city, country/state."""
    if not loc or not loc.strip():
        return "", ""
    parts = [p.strip() for p in loc.split(",", 1)]
    city = parts[0] if parts else ""
    country = parts[1] if len(parts) > 1 else ""
    return city, country


def run():
    if not os.path.isfile(ASSET_FILE):
        print(f"File not found: {ASSET_FILE}")
        return
    trials = []
    hospitals = []
    with open(ASSET_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = (row.get("Category") or "").strip()
            uid = (row.get("ID") or "").strip()
            name = (row.get("Name") or "").strip()
            if not uid:
                continue
            if cat == "Trial":
                trials.append({
                    "id": uid,
                    "title": name,
                    "status": "RECRUITING",
                    "criteria": "",
                    "source": row.get("Source_URL", "ClinicalTrials.gov") or "ClinicalTrials.gov",
                    "category": (row.get("Specialty") or row.get("Key_Tech") or "").strip(),
                })
            elif cat in ("Center", "Company"):
                city, country = _parse_location(row.get("Location") or "")
                specialty = (row.get("Specialty") or "").strip()
                specialty_focus = [s.strip() for s in specialty.split(";") if s.strip()] if specialty else []
                hospitals.append({
                    "id": uid,
                    "name": name,
                    "affiliation": "",
                    "region": "North America" if "USA" in country or "United States" in country or "Canada" in country else ("Europe" if any(x in country for x in ["UK", "Germany", "France", "Italy", "Spain", "Netherlands", "Switzerland", "Austria", "Poland", "Belgium", "Sweden", "Norway", "Finland"]) else "Asia-Pacific" if any(x in country for x in ["China", "Japan", "Singapore", "Australia"]) else ""),
                    "country": country,
                    "city": city,
                    "state": "",
                    "specialty_focus": specialty_focus[:10],
                    "value_add_services": [],
                })
    # Ingest: parent data dir = 20260128
    data_dir = os.path.dirname(SCRIPT_DIR)
    t_count, t_ids = ingest_trials(trials, data_dir=data_dir)
    h_count, h_ids = ingest_hospitals(hospitals, data_dir=data_dir)
    print(f"Trials added: {t_count} (ids: {t_ids[:5]}...)" if len(t_ids) > 5 else f"Trials added: {t_count} (ids: {t_ids})")
    print(f"Hospitals/Centers added: {h_count} (ids: {h_ids[:5]}...)" if len(h_ids) > 5 else f"Hospitals/Centers added: {h_count} (ids: {h_ids})")
    print("Done. Working log updated in asset_library_l2/working_log.jsonl and working_log.md")


if __name__ == "__main__":
    run()
