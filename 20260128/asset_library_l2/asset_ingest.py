# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
L2 Asset Ingest: normalize external data to internal format, append to asset files,
and write working log (time, content, ids_added). For continuous global collection.
"""
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Default: parent dir (20260128) holds merged_data.json, expert_map_data.json
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DATA_DIR = os.path.dirname(SCRIPT_DIR)
WORKING_LOG_JSONL = os.path.join(SCRIPT_DIR, "working_log.jsonl")
WORKING_LOG_MD = os.path.join(SCRIPT_DIR, "working_log.md")
HOSPITAL_ASSETS_FILE = os.path.join(PARENT_DATA_DIR, "hospital_center_assets.json")
MERGED_DATA_FILE = os.path.join(PARENT_DATA_DIR, "merged_data.json")
EXPERT_MAP_FILE = os.path.join(PARENT_DATA_DIR, "expert_map_data.json")
PATIENT_COVERAGE_FILE = os.path.join(PARENT_DATA_DIR, "patient_coverage_by_region.json")

# ------------------------------------------------------------------------------
# Normalize: map external payload to internal L2 format
# ------------------------------------------------------------------------------
def _normalize_trial(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map external trial to merged_data internal format."""
    return {
        "id": raw.get("id") or raw.get("nct_id") or "",
        "source": raw.get("source", ""),
        "category": raw.get("category", ""),
        "title": raw.get("title") or raw.get("brief_title", ""),
        "status": (raw.get("status") or raw.get("overall_status", "")).upper(),
        "criteria": raw.get("criteria", ""),
    }


def _normalize_pi(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map external PI/expert to expert_map_data internal format."""
    loc = raw.get("location") or {}
    if isinstance(loc, dict):
        pass
    else:
        loc = {}
    return {
        "id": raw.get("id") or (raw.get("name", "")[:20].replace(" ", "_") + "_" + str(hash(str(raw)) % 10**6)),
        "name": raw.get("name", ""),
        "affiliation": raw.get("affiliation", ""),
        "specialty": raw.get("specialty", ""),
        "expertise_tags": raw.get("expertise_tags", []),
        "insurance_partners": raw.get("insurance_partners", []),
        "value_add_services": raw.get("value_add_services", []),
        "location": {"city": loc.get("city", ""), "state": loc.get("state", ""), "zip": loc.get("zip", "")},
        "linked_projects": raw.get("linked_projects", []),
    }


def _normalize_hospital(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map external hospital/center to internal format (hospital_center_assets)."""
    return {
        "id": raw.get("id", ""),
        "name": raw.get("name", ""),
        "affiliation": raw.get("affiliation", ""),
        "region": raw.get("region", ""),
        "country": raw.get("country", ""),
        "city": raw.get("city", ""),
        "state": raw.get("state", ""),
        "specialty_focus": raw.get("specialty_focus", []),
        "value_add_services": raw.get("value_add_services", []),
    }


def _normalize_patient_coverage(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map external patient coverage (aggregate, de-identified only) to internal format."""
    return {
        "id": raw.get("id", ""),
        "region": raw.get("region", ""),
        "country": raw.get("country", ""),
        "coverage_count": int(raw.get("coverage_count", 0)),
        "source_description": raw.get("source_description", ""),
    }


# ------------------------------------------------------------------------------
# Validation (minimal: required fields, no duplicate id in target list)
# ------------------------------------------------------------------------------
def _validate_trial(rec: Dict[str, Any]) -> Tuple[bool, str]:
    if not rec.get("id"):
        return False, "missing id"
    if not (rec.get("title") or rec.get("brief_title")):
        return False, "missing title/brief_title"
    if not (rec.get("status") or rec.get("overall_status")):
        return False, "missing status/overall_status"
    return True, ""


def _validate_pi(rec: Dict[str, Any]) -> Tuple[bool, str]:
    if not (rec.get("id") or rec.get("name")):
        return False, "missing id or name"
    if not rec.get("affiliation"):
        return False, "missing affiliation"
    return True, ""


def _validate_hospital(rec: Dict[str, Any]) -> Tuple[bool, str]:
    if not rec.get("id"):
        return False, "missing id"
    if not rec.get("name"):
        return False, "missing name"
    return True, ""


def _validate_patient_coverage(rec: Dict[str, Any]) -> Tuple[bool, str]:
    if not rec.get("id"):
        return False, "missing id"
    if not rec.get("region"):
        return False, "missing region"
    if rec.get("coverage_count", -1) < 0:
        return False, "coverage_count must be >= 0"
    return True, ""


# ------------------------------------------------------------------------------
# Load / save JSON list
# ------------------------------------------------------------------------------
def _load_json_list(path: str) -> List[Dict[str, Any]]:
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []


def _save_json_list(path: str, items: List[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------------------------
# Working log: append one entry (time, action, content_summary, ids_added)
# ------------------------------------------------------------------------------
def _append_working_log(
    action: str,
    content_summary: str,
    ids_added: List[str],
    source_file: Optional[str] = None,
    count: int = 0,
) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    entry = {
        "time": ts,
        "action": action,
        "content_summary": content_summary,
        "ids_added": ids_added,
        "count": count or len(ids_added),
    }
    if source_file:
        entry["source_file"] = source_file
    # JSONL
    with open(WORKING_LOG_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    # MD: init header on first write
    if not os.path.isfile(WORKING_LOG_MD):
        with open(WORKING_LOG_MD, "w", encoding="utf-8") as f:
            f.write("# L2 Asset Library — Working Log\n\n| Time | Action | Content | IDs Added |\n|------|--------|--------|----------|\n")
    with open(WORKING_LOG_MD, "a", encoding="utf-8") as f:
        ids_str = ", ".join(ids_added[:10]) + (" ..." if len(ids_added) > 10 else "")
        f.write(f"| {ts} | {action} | {content_summary[:80]} | {ids_str} |\n")


# ------------------------------------------------------------------------------
# Ingest entry points
# ------------------------------------------------------------------------------
def ingest_trials(records: List[Dict[str, Any]], data_dir: Optional[str] = None) -> Tuple[int, List[str]]:
    """Normalize and append trials to merged_data.json. Returns (appended_count, ids_added)."""
    path = os.path.join(data_dir or PARENT_DATA_DIR, "merged_data.json")
    existing = _load_json_list(path)
    existing_ids = {r.get("id") for r in existing if r.get("id")}
    added = []
    for raw in records:
        norm = _normalize_trial(raw)
        ok, err = _validate_trial(norm)
        if not ok:
            continue
        if norm["id"] in existing_ids:
            continue
        existing.append(norm)
        existing_ids.add(norm["id"])
        added.append(norm["id"])
    if added:
        _save_json_list(path, existing)
        _append_working_log("ingest_trial", f"trials added: {len(added)}", added, count=len(added))
    return len(added), added


def ingest_pis(records: List[Dict[str, Any]], data_dir: Optional[str] = None) -> Tuple[int, List[str]]:
    """Normalize and append PIs/experts to expert_map_data.json. Returns (appended_count, ids_added)."""
    path = os.path.join(data_dir or PARENT_DATA_DIR, "expert_map_data.json")
    existing = _load_json_list(path)
    existing_ids = {str(r.get("id") or r.get("name", "")) for r in existing}
    added = []
    for raw in records:
        norm = _normalize_pi(raw)
        ok, err = _validate_pi(norm)
        if not ok:
            continue
        key = str(norm.get("id") or norm.get("name", ""))
        if key in existing_ids:
            continue
        existing.append(norm)
        existing_ids.add(key)
        added.append(key)
    if added:
        _save_json_list(path, existing)
        _append_working_log("ingest_pi", f"PIs added: {len(added)}", added, count=len(added))
    return len(added), added


def ingest_hospitals(records: List[Dict[str, Any]], data_dir: Optional[str] = None) -> Tuple[int, List[str]]:
    """Normalize and append hospitals/centers to hospital_center_assets.json. Returns (appended_count, ids_added)."""
    path = os.path.join(data_dir or PARENT_DATA_DIR, "hospital_center_assets.json")
    existing = _load_json_list(path)
    existing_ids = {r.get("id") for r in existing if r.get("id")}
    added = []
    for raw in records:
        norm = _normalize_hospital(raw)
        ok, err = _validate_hospital(norm)
        if not ok:
            continue
        if norm["id"] in existing_ids:
            continue
        existing.append(norm)
        existing_ids.add(norm["id"])
        added.append(norm["id"])
    if added:
        _save_json_list(path, existing)
        _append_working_log("ingest_hospital", f"hospitals/centers added: {len(added)}", added, count=len(added))
    return len(added), added


def ingest_patient_coverage(
    records: List[Dict[str, Any]], data_dir: Optional[str] = None
) -> Tuple[int, List[str]]:
    """Merge aggregate patient coverage by region (de-identified only; no PII). Returns (appended_count, ids_added)."""
    path = os.path.join(data_dir or PARENT_DATA_DIR, "patient_coverage_by_region.json")
    existing = _load_json_list(path)
    existing_ids = {r.get("id") for r in existing if r.get("id")}
    added = []
    for raw in records:
        norm = _normalize_patient_coverage(raw)
        ok, _ = _validate_patient_coverage(norm)
        if not ok:
            continue
        if norm["id"] in existing_ids:
            continue
        existing.append(norm)
        existing_ids.add(norm["id"])
        added.append(norm["id"])
    if added:
        _save_json_list(path, existing)
        total = sum(r.get("coverage_count", 0) for r in existing)
        _append_working_log(
            "ingest_patient_coverage",
            f"patient coverage regions added: {len(added)}, total coverage count: {total}",
            added,
            count=len(added),
        )
    return len(added), added


def ingest(
    asset_type: str,
    records: List[Dict[str, Any]],
    data_dir: Optional[str] = None,
) -> Tuple[int, List[str]]:
    """
    Single entry: asset_type in ('trial','pi','hospital').
    Normalizes to internal format, appends to the correct file, writes working log.
    Returns (count_added, ids_added).
    """
    asset_type = (asset_type or "").strip().lower()
    if asset_type in ("trial", "trials", "clinical"):
        return ingest_trials(records, data_dir)
    if asset_type in ("pi", "pis", "expert", "experts"):
        return ingest_pis(records, data_dir)
    if asset_type in ("hospital", "hospitals", "center", "centers"):
        return ingest_hospitals(records, data_dir)
    if asset_type in ("patient_coverage", "coverage", "patient_coverage_by_region"):
        return ingest_patient_coverage(records, data_dir)
    return 0, []


# ------------------------------------------------------------------------------
# CLI: e.g. python asset_ingest.py trial ./new_trials.json
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python asset_ingest.py <trial|pi|hospital|patient_coverage> <path_to_json_or_single_json>")
        sys.exit(1)
    kind = sys.argv[1]
    path_or_json = sys.argv[2]
    data_dir = sys.argv[3] if len(sys.argv) > 3 else None
    records = []
    if os.path.isfile(path_or_json):
        records = _load_json_list(path_or_json)
    else:
        try:
            records = [json.loads(path_or_json)]
        except Exception:
            print("Second arg must be a file path or a single JSON object string.")
            sys.exit(2)
    count, ids = ingest(kind, records, data_dir)
    print(f"Added {count} record(s); ids: {ids}")
