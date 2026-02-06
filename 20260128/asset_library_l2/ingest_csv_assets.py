# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Ingest CSV assets (ID,Category,Name,Location,Lead_PI,Specialty,Key_Tech,Source_URL,Ingestion_Time).
Maps: Trial / BCI Clinical Trial -> merged_data.json; Center / Company / BCI Company -> hospital_center_assets.json.
Duplicate IDs are skipped (no update). Working log updated on add.
"""
import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from asset_ingest import ingest_trials, ingest_hospitals

TRIAL_CATEGORIES = ("Trial", "BCI Clinical Trial")
HOSPITAL_CATEGORIES = ("Center", "Company", "BCI Company")


def _parse_location(loc: str):
    if not loc or not loc.strip():
        return "", ""
    parts = [p.strip() for p in str(loc).split(",", 1)]
    city = parts[0] if parts else ""
    country = parts[1] if len(parts) > 1 else ""
    return city, country


def _region_from_country(country: str) -> str:
    c = (country or "").upper()
    if not c:
        return ""
    if "USA" in c or "UNITED STATES" in c or "CANADA" in c:
        return "North America"
    if any(x in c for x in ["UK", "GERMANY", "FRANCE", "ITALY", "SPAIN", "NETHERLANDS", "SWITZERLAND", "AUSTRIA", "POLAND", "BELGIUM", "SWEDEN", "NORWAY", "FINLAND", "IRELAND"]):
        return "Europe"
    if any(x in c for x in ["CHINA", "JAPAN", "SINGAPORE", "AUSTRALIA", "KOREA", "INDIA", "ETHIOPIA"]):
        return "Asia-Pacific"
    return ""


def load_and_ingest(csv_path: str, data_dir: str = None) -> None:
    data_dir = data_dir or os.path.dirname(SCRIPT_DIR)
    if not os.path.isfile(csv_path):
        print(f"File not found: {csv_path}")
        return
    trials = []
    hospitals = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = (row.get("Category") or "").strip()
            uid = (row.get("ID") or "").strip()
            name = (row.get("Name") or "").strip()
            if not uid:
                continue
            if cat in TRIAL_CATEGORIES:
                trials.append({
                    "id": uid,
                    "title": name,
                    "status": "RECRUITING",
                    "criteria": "",
                    "source": (row.get("Source_URL") or "ClinicalTrials.gov").strip(),
                    "category": (row.get("Specialty") or row.get("Key_Tech") or "").strip(),
                })
            elif cat in HOSPITAL_CATEGORIES:
                city, country = _parse_location(row.get("Location") or "")
                specialty = (row.get("Specialty") or "").strip()
                specialty_focus = [s.strip() for s in specialty.replace(",", ";").split(";") if s.strip()][:10] if specialty else []
                hospitals.append({
                    "id": uid,
                    "name": name,
                    "affiliation": "",
                    "region": _region_from_country(country),
                    "country": country,
                    "city": city,
                    "state": "",
                    "specialty_focus": specialty_focus,
                    "value_add_services": [],
                })
    t_count, t_ids = ingest_trials(trials, data_dir=data_dir)
    h_count, h_ids = ingest_hospitals(hospitals, data_dir=data_dir)
    print(f"Trials added: {t_count} (duplicates skipped). ids: {t_ids[:8]}{'...' if len(t_ids) > 8 else ''}")
    print(f"Hospitals/Companies added: {h_count} (duplicates skipped). ids: {h_ids}")
    print("Asset library and working log updated.")


if __name__ == "__main__":
    default_csv = os.path.join(SCRIPT_DIR, "new_assets_20260202.csv")
    csv_path = sys.argv[1] if len(sys.argv) > 1 else default_csv
    load_and_ingest(csv_path)
