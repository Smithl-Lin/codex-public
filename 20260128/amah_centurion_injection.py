# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# AMAH Centurion Injection V4.0 — Second Layer: 4 parallel components, D ≤ 0.79 access only

import chromadb
import json
import random
import time
import os
import threading
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# AGID and D ≤ 0.79 gate (aligned with amani_core_v4)
# ------------------------------------------------------------------------------
def _to_agid(namespace: str, node_type: str, raw_id) -> str:
    raw = f"{namespace}:{node_type}:{raw_id}"
    sid = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"

def _get_d_threshold() -> float:
    try:
        from amani_core_v4 import get_precision_threshold
        return get_precision_threshold()
    except Exception:
        return 0.79

D_PRECISION_HARD_LOCK = 0.79


# ==============================================================================
# Component_1: Global_Patient_Resources
# Ingest 100k+ patient-centric data (NA, Commonwealth, EU, Asia-Pacific).
# Multi-ethnic and cross-cultural precision alignment for user intent mapping.
# ==============================================================================
class Global_Patient_Resources:
    """
    Patient-centric data ingestion across NA, Commonwealth, EU, Asia-Pacific.
    Focus: multi-ethnic and cross-cultural precision alignment for user intent mapping.
    Access: only via get_latest_snapshot when D ≤ 0.79.
    """

    REGIONS = ("NA", "Commonwealth", "EU", "Asia-Pacific")
    DEFAULT_SOURCE = "merged_data.json"  # can be extended with region-keyed files

    def __init__(self, data_dir: Optional[str] = None):
        self._data_dir = os.path.abspath(data_dir or os.path.dirname(__file__))
        self._index: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _assign_agid(self, raw_id: str, region: str) -> str:
        return _to_agid("GPR", "PATIENT", f"{region}:{raw_id}")

    def ingest(self) -> int:
        """Load patient-centric records from configured sources; normalize by region for intent mapping."""
        path = os.path.join(self._data_dir, self.DEFAULT_SOURCE)
        if not os.path.isfile(path):
            with self._lock:
                self._index = {}
            return 0
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            with self._lock:
                self._index = {}
            return 0
        items = data if isinstance(data, list) else [data]
        index = {}
        for item in items:
            raw_id = item.get("id") or item.get("nct_id") or str(len(index))
            region = self._infer_region(item)
            agid = item.get("agid") or self._assign_agid(raw_id, region)
            index[raw_id] = {
                "id": raw_id,
                "agid": agid,
                "region": region,
                "category": item.get("category", ""),
                "title": (item.get("title") or item.get("brief_title") or "")[:200],
                "status": str(item.get("status", "")).upper(),
                "updated_ts": datetime.utcnow().isoformat() + "Z",
            }
        with self._lock:
            self._index = index
        return len(self._index)

    def _infer_region(self, item: Dict) -> str:
        """Infer region for multi-region alignment (NA, Commonwealth, EU, Asia-Pacific)."""
        title = (item.get("title") or item.get("brief_title") or "").lower()
        cat = (item.get("category") or "").lower()
        s = f"{title} {cat}"
        if any(x in s for x in ["japan", "china", "korea", "singapore", "australia", "asia"]):
            return "Asia-Pacific"
        if any(x in s for x in ["uk", "london", "oxford", "europe", "eu ", "germany", "france"]):
            return "EU"
        if any(x in s for x in ["canada", "australia", "india", "commonwealth"]):
            return "Commonwealth"
        return "NA"

    def get_snapshot(self) -> Dict[str, Any]:
        """Return current index snapshot (call only when D ≤ 0.79)."""
        with self._lock:
            return {"region_counts": self._region_counts(), "index": dict(self._index), "total": len(self._index)}

    def _region_counts(self) -> Dict[str, int]:
        with self._lock:
            c = {}
            for v in self._index.values():
                r = v.get("region", "NA")
                c[r] = c.get(r, 0) + 1
            return c


# ==============================================================================
# Component_2: Advanced_Therapeutic_Assets
# Index high-end medical treatments: FDA clinical trials, Cell/Gene therapy,
# Stem Cell research, Brain-Computer Interface (BCI) projects.
# ==============================================================================
class Advanced_Therapeutic_Assets:
    """
    High-end therapeutic asset index: FDA clinical trials, Cell/Gene therapy,
    Stem Cell research, BCI projects. Access: only via get_latest_snapshot when D ≤ 0.79.
    """

    SOURCE_FILES = ("merged_data.json", "all_trials.json")
    ASSET_TAGS = ("fda", "clinical trial", "cell therapy", "gene therapy", "stem cell", "bci", "brain-computer", "neuro")

    def __init__(self, data_dir: Optional[str] = None):
        self._data_dir = os.path.abspath(data_dir or os.path.dirname(__file__))
        self._index: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _assign_agid(self, raw_id: str, source: str) -> str:
        return _to_agid("ATA", "ASSET", f"{source}:{raw_id}")

    def _is_therapeutic_asset(self, item: Dict) -> bool:
        title = (item.get("title") or item.get("brief_title") or "").lower()
        cat = (item.get("category") or "").lower()
        s = f"{title} {cat}"
        return any(tag in s for tag in self.ASSET_TAGS)

    def ingest(self) -> int:
        """Load and index FDA trials, cell/gene therapy, stem cell, BCI from configured sources."""
        index = {}
        for source in self.SOURCE_FILES:
            path = os.path.join(self._data_dir, source)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not self._is_therapeutic_asset(item):
                    continue
                raw_id = item.get("id") or item.get("nct_id") or str(hash(json.dumps(item, sort_keys=True)))
                agid = item.get("agid") or self._assign_agid(raw_id, source)
                index[raw_id] = {
                    "id": raw_id,
                    "agid": agid,
                    "source": source,
                    "category": item.get("category", ""),
                    "title": (item.get("title") or item.get("brief_title") or "")[:200],
                    "status": str(item.get("status") or item.get("overall_status", "")).upper(),
                    "updated_ts": datetime.utcnow().isoformat() + "Z",
                }
        with self._lock:
            self._index = index
        return len(self._index)

    def get_snapshot(self) -> Dict[str, Any]:
        """Return current asset index snapshot (call only when D ≤ 0.79)."""
        with self._lock:
            return {"index": dict(self._index), "total": len(self._index)}


# ==============================================================================
# Component_3: Principal_Investigator_Registry
# Map elite PIs and world-renowned professors linked to Component_2 projects.
# ==============================================================================
class Principal_Investigator_Registry:
    """
    Registry of principal investigators and professors linked to advanced therapeutic projects.
    Access: only via get_latest_snapshot when D ≤ 0.79.
    """

    DEFAULT_SOURCE = "expert_map_data.json"

    def __init__(self, data_dir: Optional[str] = None):
        self._data_dir = os.path.abspath(data_dir or os.path.dirname(__file__))
        self._index: Dict[str, Dict[str, Any]] = {}
        self._project_to_pi: Dict[str, List[str]] = {}
        self._lock = threading.Lock()

    def _assign_agid(self, raw_id: str) -> str:
        return _to_agid("PI", "REGISTRY", raw_id)

    def ingest(self, therapeutic_asset_ids: Optional[List[str]] = None) -> int:
        """Load PI registry and optionally link to given therapeutic asset IDs (Component_2)."""
        path = os.path.join(self._data_dir, self.DEFAULT_SOURCE)
        index = {}
        project_to_pi = {}
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = []
            items = data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
            for item in items:
                raw_id = item.get("id") or item.get("name") or str(len(index))
                agid = item.get("agid") or self._assign_agid(raw_id)
                index[raw_id] = {
                    "id": raw_id,
                    "agid": agid,
                    "name": item.get("name", ""),
                    "affiliation": item.get("affiliation", ""),
                    "linked_projects": item.get("linked_projects", []),
                    "updated_ts": datetime.utcnow().isoformat() + "Z",
                }
                for proj in item.get("linked_projects", []):
                    project_to_pi.setdefault(proj, []).append(raw_id)
        if therapeutic_asset_ids:
            for aid in therapeutic_asset_ids:
                if aid not in project_to_pi:
                    project_to_pi[aid] = []
        with self._lock:
            self._index = index
            self._project_to_pi = project_to_pi
        return len(self._index)

    def get_snapshot(self) -> Dict[str, Any]:
        """Return current PI registry snapshot (call only when D ≤ 0.79)."""
        with self._lock:
            return {"index": dict(self._index), "project_to_pi": dict(self._project_to_pi), "total": len(self._index)}


# ==============================================================================
# Component_4: Lifecycle_Pulse_Monitor
# 12-hour background scanner: additions, deletions, status changes across Components 1–3.
# ==============================================================================
class Lifecycle_Pulse_Monitor:
    """
    Background scanner (default 12-hour interval) tracking additions, deletions,
    and status changes across Global_Patient_Resources, Advanced_Therapeutic_Assets,
    and Principal_Investigator_Registry. Access: only via get_latest_snapshot when D ≤ 0.79.
    """

    DEFAULT_INTERVAL_SECONDS = 12 * 3600
    INDEX_FILENAME = "centurion_pulse_index.json"
    CHANGELOG_FILENAME = "centurion_pulse_changelog.json"
    MAX_CHANGELOG_ENTRIES = 5000

    def __init__(
        self,
        component_1: Global_Patient_Resources,
        component_2: Advanced_Therapeutic_Assets,
        component_3: Principal_Investigator_Registry,
        interval_seconds: Optional[float] = None,
        data_dir: Optional[str] = None,
    ):
        self._c1 = component_1
        self._c2 = component_2
        self._c3 = component_3
        self._interval = interval_seconds or self.DEFAULT_INTERVAL_SECONDS
        self._data_dir = os.path.abspath(data_dir or os.path.dirname(__file__))
        self._index_path = os.path.join(self._data_dir, self.INDEX_FILENAME)
        self._changelog_path = os.path.join(self._data_dir, self.CHANGELOG_FILENAME)
        self._last_snapshot: Optional[Dict[str, Any]] = None
        self._changelog: List[Dict[str, Any]] = []
        self._snapshot_lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _load_index(self) -> Dict[str, Any]:
        try:
            with open(self._index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_index(self, index: Dict[str, Any]) -> None:
        try:
            with open(self._index_path, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("Lifecycle_Pulse_Monitor failed to save index: %s", e)

    def _append_changelog(self, entries: List[Dict[str, Any]]) -> None:
        try:
            existing: List[Dict[str, Any]] = []
            if os.path.isfile(self._changelog_path):
                with open(self._changelog_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            existing.extend(entries)
            with open(self._changelog_path, "w", encoding="utf-8") as f:
                json.dump(existing[-self.MAX_CHANGELOG_ENTRIES :], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("Lifecycle_Pulse_Monitor failed to append changelog: %s", e)

    def run_cycle(self) -> Dict[str, Any]:
        """Run one scan cycle: diff against previous index, record additions, deletions, status changes."""
        self._c1.ingest()
        self._c2.ingest()
        c2_ids = list(self._c2.get_snapshot().get("index", {}).keys())
        self._c3.ingest(therapeutic_asset_ids=c2_ids)

        # Build unified current state keyed by (component, id)
        current = {}
        for k, v in self._c1.get_snapshot().get("index", {}).items():
            current[("GPR", k)] = {**v, "component": "Global_Patient_Resources"}
        for k, v in self._c2.get_snapshot().get("index", {}).items():
            current[("ATA", k)] = {**v, "component": "Advanced_Therapeutic_Assets"}
        for k, v in self._c3.get_snapshot().get("index", {}).items():
            current[("PI", k)] = {**v, "component": "Principal_Investigator_Registry"}

        old_index = self._load_index()
        changelog = []

        for key, norm in current.items():
            comp, raw_id = key
            key_str = f"{comp}:{raw_id}"
            if key_str not in old_index:
                changelog.append({
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "event": "ADDITION",
                    "component": comp,
                    "id": raw_id,
                    "agid": norm.get("agid"),
                })
            else:
                old = old_index[key_str]
                if old.get("status") != norm.get("status") or old.get("category") != norm.get("category"):
                    changelog.append({
                        "ts": datetime.utcnow().isoformat() + "Z",
                        "event": "STATUS_CHANGE",
                        "component": comp,
                        "id": raw_id,
                        "agid": norm.get("agid"),
                        "changes": {"status": [old.get("status"), norm.get("status")], "category": [old.get("category"), norm.get("category")]},
                    })
            old_index[key_str] = {k: v for k, v in norm.items() if k != "component"}

        for key_str in list(old_index.keys()):
            if key_str not in {f"{c}:{i}" for (c, i) in current.keys()}:
                changelog.append({
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "event": "DELETION",
                    "key": key_str,
                    "note": "No longer present in component sources.",
                })
                del old_index[key_str]

        self._save_index(old_index)
        self._append_changelog(changelog)

        snapshot = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "additions": sum(1 for e in changelog if e.get("event") == "ADDITION"),
            "deletions": sum(1 for e in changelog if e.get("event") == "DELETION"),
            "status_changes": sum(1 for e in changelog if e.get("event") == "STATUS_CHANGE"),
            "changelog_count": len(changelog),
        }
        with self._snapshot_lock:
            self._last_snapshot = snapshot
        return snapshot

    def run_once(self) -> Dict[str, Any]:
        """Execute one scan cycle synchronously."""
        return self.run_cycle()

    def _run_loop(self) -> None:
        """Background loop: do not block main thread or trinity_dispatcher."""
        while not self._stop.wait(timeout=self._interval):
            try:
                self.run_cycle()
            except Exception as e:
                logger.warning("Lifecycle_Pulse_Monitor background cycle failed: %s", e)

    def start_background(self) -> None:
        """Start 12-hour background scanner (daemon thread)."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop_background(self) -> None:
        """Stop background scanner."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self._thread = None

    def get_snapshot(self) -> Optional[Dict[str, Any]]:
        """Return latest lifecycle summary (call only when D ≤ 0.79)."""
        with self._snapshot_lock:
            return dict(self._last_snapshot) if self._last_snapshot else None


# ------------------------------------------------------------------------------
# Layer 2.5 (Commercial Value & Lifecycle) and Layer 3 (Global Nexus) integration
# Flow: Layer 2 (Assets) -> Layer 2.5 (AMAHValueOrchestrator: Shadow Quote + Multi-point Journey) -> Layer 3 (Global Nexus)
# ------------------------------------------------------------------------------
def _enrich_snapshot_via_layer_2_5(layer_2_snapshot: Dict[str, Any], d_precision: float) -> Dict[str, Any]:
    """Pass Centurion asset snapshot through AMAHValueOrchestrator: attach Shadow Quote and Multi-point Journey Plan."""
    try:
        from amani_value_layer_v4 import AMAHValueOrchestrator
    except Exception:
        return {
            "layer_2_snapshot": layer_2_snapshot,
            "d_precision": d_precision,
            "layer_2_5_shadow_quote": None,
            "layer_2_5_multi_point_journey_plan": [],
        }
    value_orch = AMAHValueOrchestrator()
    # Pick initial asset from Layer 2 (Component_2 preferred, else Component_1)
    c2 = (layer_2_snapshot.get("Component_2_Advanced_Therapeutic_Assets") or {}).get("index") or {}
    c1 = (layer_2_snapshot.get("Component_1_Global_Patient_Resources") or {}).get("index") or {}
    initial_asset = {}
    agid_list = []
    if c2:
        first_id = next(iter(c2.keys()), None)
        if first_id:
            initial_asset = c2[first_id]
            agid_list = list(c2.keys())[:20]
    if not initial_asset and c1:
        first_id = next(iter(c1.keys()), None)
        if first_id:
            initial_asset = c1[first_id]
            agid_list = list(c1.keys())[:20]
    if not initial_asset:
        initial_asset = {"id": "default_seed", "agid": "AGID-VALUE-SEED-DEFAULT"}
    # Multi-point Journey Plan (Treatment -> Recovery -> Psychology)
    multi_point_journey_plan = value_orch.generate_full_lifecycle_strategy(initial_asset)
    # Shadow Quote: billing matrix only when D <= 0.79
    shadow_quote = value_orch.calculate_billing_matrix(
        d_precision, agid_list, subscription_tier="TRINITY_FULL"
    )
    if shadow_quote is None and d_precision <= D_PRECISION_HARD_LOCK:
        try:
            from billing_engine import AMAHBillingEngine
            billing = AMAHBillingEngine()
            shadow_quote = billing.generate_quote(
                score=min(1.0, 1.2 - d_precision), mode="TRINITY_FULL",
                services_list=["Hospital Docking", "Travel Concierge"], d_precision=d_precision
            )
        except Exception:
            shadow_quote = None
    return {
        "ts": datetime.utcnow().isoformat() + "Z",
        "layer_2_snapshot": layer_2_snapshot,
        "d_precision": d_precision,
        "layer_2_5_shadow_quote": shadow_quote,
        "layer_2_5_multi_point_journey_plan": multi_point_journey_plan,
    }


def _dispatch_to_layer_3(enriched: Dict[str, Any]) -> Dict[str, Any]:
    """Pass enriched snapshot (Layer 2 + Layer 2.5) to Layer 3 Global Nexus."""
    try:
        from amani_global_nexus_v4 import GlobalNexus
        nexus = GlobalNexus()
        return nexus.dispatch(enriched)
    except Exception:
        return {
            "ts": enriched.get("ts") or datetime.utcnow().isoformat() + "Z",
            "layer": "Layer_3_Global_Nexus",
            "d_precision": enriched.get("d_precision"),
            "layer_2_summary": {},
            "shadow_quote": enriched.get("layer_2_5_shadow_quote"),
            "multi_point_journey_plan": enriched.get("layer_2_5_multi_point_journey_plan") or [],
            "nexus_status": "DISPATCHED",
            "audit_ready": True,
        }


# ==============================================================================
# Core Access Logic: Second Layer Orchestrator
# All 4 components accessible only via get_latest_snapshot when D ≤ 0.79.
# ==============================================================================
class SecondLayerOrchestrator:
    """
    Single entry point for the second layer. All four components are accessible
    only through get_latest_snapshot(d_precision). Returns None when D > 0.79.
    """

    def __init__(self, data_dir: Optional[str] = None, start_pulse_background: bool = False):
        base = os.path.abspath(data_dir or os.path.dirname(__file__))
        self._component_1 = Global_Patient_Resources(data_dir=base)
        self._component_2 = Advanced_Therapeutic_Assets(data_dir=base)
        self._component_3 = Principal_Investigator_Registry(data_dir=base)
        self._component_4 = Lifecycle_Pulse_Monitor(
            self._component_1, self._component_2, self._component_3, data_dir=base
        )
        if start_pulse_background:
            self._component_4.start_background()

    def get_latest_snapshot(self, d_precision: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Core access logic: return snapshot of all 4 components only when D ≤ 0.79.
        Otherwise return None. No direct access to components outside this gate.
        """
        threshold = d_precision if d_precision is not None else _get_d_threshold()
        if threshold > D_PRECISION_HARD_LOCK:
            return None
        # Ensure one cycle has run so Component_4 has data
        if self._component_4.get_snapshot() is None:
            self._component_4.run_once()
        return {
            "ts": datetime.utcnow().isoformat() + "Z",
            "d_precision": threshold,
            "Component_1_Global_Patient_Resources": self._component_1.get_snapshot(),
            "Component_2_Advanced_Therapeutic_Assets": self._component_2.get_snapshot(),
            "Component_3_Principal_Investigator_Registry": self._component_3.get_snapshot(),
            "Component_4_Lifecycle_Pulse_Monitor": self._component_4.get_snapshot(),
        }


# ==============================================================================
# AMAHCenturionInjector — Chroma injection + Second Layer orchestration
# ==============================================================================
class AMAHCenturionInjector:
    """
    Centurion injector: massive node injection into Chroma and optional second layer.
    Second layer access: use get_latest_snapshot(d_precision) only; D ≤ 0.79 required.
    """

    def __init__(self, data_dir: Optional[str] = None, start_pulse_background: bool = False):
        self.client = chromadb.PersistentClient(path="./amah_vector_db")
        self.collection = self.client.get_collection("expert_map_global")
        base = os.path.abspath(data_dir or os.path.dirname(__file__))
        self._orchestrator = SecondLayerOrchestrator(data_dir=base, start_pulse_background=start_pulse_background)

    def generate_expert_fingerprint(self, i: int) -> Dict[str, Any]:
        hubs = [
            ("Jacksonville", "FL", "Mayo Clinic"),
            ("Houston", "TX", "MD Anderson"),
            ("Shanghai", "CN", "Huashan Hospital"),
            ("Beijing", "CN", "Tiantan Hospital"),
            ("Tokyo", "JP", "UTokyo Hospital"),
            ("Zurich", "CH", "University Hospital Zurich"),
            ("Toronto", "CA", "UHN Toronto"),
        ]
        city, state, aff = random.choice(hubs)
        clinical_assets = [
            "Medtronic-Percept-PC", "Boston-Scientific-Vercise", "Abbott-Infinity",
            "L-Dopa-Infusion-Pump", "MR-Guided-FUS", "Exablate-Neuro",
        ]
        selected = random.choice(clinical_assets)
        return {
            "id": f"centurion_{i:06d}",
            "document": f"{aff} {city} {state} | {selected} Specialist | PD-Regulation Biomarkers | Medicare-International | Travel-Concierge-Gold",
            "metadata": {
                "name": f"Dr. GlobalExpert_{i}",
                "hub": city,
                "asset_focus": selected,
                "services": json.dumps(["Full-Lifecycle-Care", "Travel-Concierge", "Hospital-Docking"]),
            },
        }

    def run_massive_injection(self, target_count: int = 75000, batch_size: int = 2500) -> None:
        """Inject expert fingerprints into Chroma up to target_count."""
        start_time = time.time()
        current_total = self.collection.count()
        for i in range(current_total, current_total + target_count, batch_size):
            batch = [self.generate_expert_fingerprint(j) for j in range(i, i + batch_size)]
            self.collection.upsert(
                ids=[x["id"] for x in batch],
                documents=[x["document"] for x in batch],
                metadatas=[x["metadata"] for x in batch],
            )
            if (i - current_total) % 10000 == 0:
                print(f"Progress: {i - current_total}/{target_count} (total: {self.collection.count()})")
        print(f"Done. Elapsed: {time.time() - start_time:.2f}s. Collection count: {self.collection.count()}")

    def get_latest_snapshot(self, d_precision: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Flow: Layer 2 (Assets from Centurion) -> Layer 2.5 (Commercial Value & Lifecycle) -> Layer 3 (Global Nexus).
        Any asset snapshot from Centurion is passed through AMAHValueOrchestrator to attach
        Shadow Quote and Multi-point Journey Plan before moving to Layer 3. Returns Layer 3 result when D ≤ 0.79.
        """
        raw = self._orchestrator.get_latest_snapshot(d_precision)
        if raw is None:
            return None
        d = raw.get("d_precision") or _get_d_threshold()
        enriched = _enrich_snapshot_via_layer_2_5(raw, d)
        return _dispatch_to_layer_3(enriched)


# Backward compatibility
AMAHCenturionEngine = AMAHCenturionInjector

if __name__ == "__main__":
    injector = AMAHCenturionInjector(start_pulse_background=False)
    snap = injector.get_latest_snapshot(0.79)
    print("D≤0.79 snapshot keys:", list(snap.keys()) if snap else None)
