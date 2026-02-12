# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# AMANI Nexus Layer V3 — NexusRouter (AGID physical mapping) & ComplianceGate (regional data privacy)
# ------------------------------------------------------------------------------
# Language: Professional English.
# ------------------------------------------------------------------------------

import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Tuple

# ------------------------------------------------------------------------------
# AGID canonical format (aligned with Sovereign Protocols)
# ------------------------------------------------------------------------------
def _to_agid(namespace: str, node_type: str, raw_id: Any) -> str:
    raw = f"{namespace}:{node_type}:{raw_id}"
    sid = hashlib.sha256(str(raw).encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


# ------------------------------------------------------------------------------
# NexusRouter — AGID physical mapping
# ------------------------------------------------------------------------------
class NexusRouter:
    """
    Handles AGID-to-physical mapping: resolve AGIDs to physical nodes, regions, and endpoints.
    Supports reverse lookup (physical identifier -> AGID) and region assignment per AGID.
    """

    def __init__(self, default_region: str = "NA"):
        self._default_region = default_region
        self._agid_to_physical: Dict[str, Dict[str, Any]] = {}
        self._physical_to_agid: Dict[str, str] = {}

    def register_physical_mapping(
        self,
        agid: str,
        physical_node_id: str,
        region: str,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a physical mapping for an AGID (node, region, optional endpoint)."""
        self._agid_to_physical[agid] = {
            "physical_node_id": physical_node_id,
            "region": region,
            "endpoint": endpoint,
            "metadata": metadata or {},
        }
        self._physical_to_agid[physical_node_id] = agid

    def resolve_agid(self, agid: str) -> Optional[Dict[str, Any]]:
        """Resolve AGID to physical mapping (node, region, endpoint). Returns None if not registered."""
        return self._agid_to_physical.get(agid)

    def resolve_physical(self, physical_node_id: str) -> Optional[str]:
        """Resolve physical node ID to AGID. Returns None if not registered."""
        return self._physical_to_agid.get(physical_node_id)

    def map_agid_to_region(self, agid: str) -> str:
        """Return region for AGID; defaults to configured default if not registered."""
        rec = self._agid_to_physical.get(agid)
        return rec["region"] if rec else self._default_region

    def batch_resolve(self, agid_list: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Resolve a list of AGIDs to their physical mappings."""
        return {agid: self.resolve_agid(agid) for agid in agid_list}

    def get_all_registered_agids(self) -> List[str]:
        """Return all AGIDs that have a physical mapping."""
        return list(self._agid_to_physical.keys())

    def auto_register(self, registry_path: str) -> int:
        """
        On startup: load physical node registry JSON and register each AGID -> (node, region, endpoint).
        Registry format: list of {"agid_or_id": str, "region": str, "endpoint": str (optional), "physical_node_id": str (optional)}.
        Returns count of registered entries.
        """
        import os
        import json
        if not os.path.isfile(registry_path):
            return 0
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return 0
        items = data if isinstance(data, list) else [data]
        count = 0
        for rec in items:
            agid = rec.get("agid") or rec.get("agid_or_id") or rec.get("id")
            region = (rec.get("region") or self._default_region).strip()
            endpoint = rec.get("endpoint") or ""
            physical_node_id = rec.get("physical_node_id") or agid or str(count)
            if not agid:
                continue
            self.register_physical_mapping(agid, physical_node_id, region, endpoint=endpoint or None)
            count += 1
        return count


# ------------------------------------------------------------------------------
# Default router singleton — mitigates registry single-point: load at first use
# ------------------------------------------------------------------------------
_default_router: Optional["NexusRouter"] = None


def get_default_router(registry_path: Optional[str] = None) -> "NexusRouter":
    """Return singleton NexusRouter; if registry_path is provided and file exists, auto_register once."""
    global _default_router
    if _default_router is None:
        _default_router = NexusRouter(default_region="NA")
        if registry_path:
            import os
            if os.path.isfile(registry_path):
                _default_router.auto_register(registry_path)
    elif registry_path:
        import os
        if os.path.isfile(registry_path):
            _default_router.auto_register(registry_path)
    return _default_router


# ------------------------------------------------------------------------------
# ComplianceGate — regional data privacy enforcement
# ------------------------------------------------------------------------------
class ComplianceGate:
    """
    Enforces regional data privacy: consent, data residency, and region-specific rules
    (e.g. GDPR, CCPA, APAC frameworks). All checks use professional English messages.
    """

    # Region -> list of required compliance tags
    REGIONAL_REQUIREMENTS = {
        "US": ["HIPAA", "CONSENT_RECORDED", "DATA_RESIDENCY_US"],
        "China": ["PIPL", "CONSENT_RECORDED", "DATA_RESIDENCY_CN"],
        "EU": ["GDPR", "CONSENT_RECORDED", "DATA_RESIDENCY_EU"],
        "UK": ["UK_GDPR", "CONSENT_RECORDED", "DATA_RESIDENCY_UK"],
        "California": ["CCPA", "CONSENT_RECORDED"],
        "NA": ["CONSENT_RECORDED"],
        "Asia-Pacific": ["APAC_PRIVACY", "CONSENT_RECORDED"],
        "Default": ["CONSENT_RECORDED"],
    }

    def __init__(self, strict_mode: bool = True):
        self._strict_mode = strict_mode
        self._consent_store: Dict[str, bool] = {}
        self._region_override: Optional[str] = None
        self._regional_requirements = self._load_regional_requirements()

    def _load_regional_requirements(self) -> Dict[str, List[str]]:
        """Load optional region requirements from amah_config.json with safe fallback."""
        cfg_path = os.path.join(os.path.dirname(__file__), "amah_config.json")
        try:
            if os.path.isfile(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                region_requirements = (cfg.get("compliance_policies") or {}).get("region_requirements") or {}
                if isinstance(region_requirements, dict) and region_requirements:
                    merged = dict(self.REGIONAL_REQUIREMENTS)
                    for k, v in region_requirements.items():
                        if isinstance(v, list):
                            merged[k] = list(v)
                    return merged
        except Exception:
            pass
        return dict(self.REGIONAL_REQUIREMENTS)

    def set_region_override(self, region: Optional[str]) -> None:
        """Override region for compliance checks (e.g. request context)."""
        self._region_override = region

    def require_region(self, region: str) -> List[str]:
        """Return list of required compliance tags for the given region."""
        return list(
            self._regional_requirements.get(
                region, self._regional_requirements["Default"]
            )
        )

    def record_consent(self, subject_id: str, region: str) -> None:
        """Record consent for a subject in a region (for compliance audit)."""
        self._consent_store[f"{region}:{subject_id}"] = True

    def has_consent(self, subject_id: str, region: str) -> bool:
        """Return whether consent is recorded for the subject in the region."""
        return self._consent_store.get(f"{region}:{subject_id}", False)

    def check_data_residency(self, region: str, data_region: str) -> Tuple[bool, str]:
        """
        Check whether data may be processed in the target region (data residency).
        Returns (allowed, message).
        """
        if region == data_region:
            return True, "Data residency satisfied: same region."
        if region in ("EU", "UK") and data_region not in ("EU", "UK", "EEA"):
            return False, "Data residency violation: EU/UK data must not leave designated area."
        if region == "US" and data_region not in ("US", "NA", "United States"):
            return False, "Data residency violation: US policy requires in-region processing."
        if region == "China" and data_region not in ("China", "CN"):
            return False, "Data residency violation: PIPL policy requires in-country processing."
        if region == "Asia-Pacific" and data_region not in ("Asia-Pacific", "APAC"):
            return False, "Data residency violation: APAC policy requires in-region processing."
        return True, "Data residency check passed under current policy."

    def enforce(
        self,
        region: str,
        subject_id: Optional[str] = None,
        data_region: Optional[str] = None,
        required_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run full compliance gate for a region. Optionally check consent (subject_id)
        and data residency (data_region). Returns status and list of satisfied/violated requirements.
        """
        effective_region = self._region_override or region
        required = required_tags or self.require_region(effective_region)
        satisfied = []
        violated = []

        if "CONSENT_RECORDED" in required:
            if subject_id and self.has_consent(subject_id, effective_region):
                satisfied.append("CONSENT_RECORDED")
            else:
                violated.append("CONSENT_RECORDED")

        if "DATA_RESIDENCY_EU" in required or "DATA_RESIDENCY_UK" in required:
            dr_tag = "DATA_RESIDENCY_EU" if "DATA_RESIDENCY_EU" in required else "DATA_RESIDENCY_UK"
            dr_region = "EU" if dr_tag == "DATA_RESIDENCY_EU" else "UK"
            allowed, _ = self.check_data_residency(dr_region, data_region or effective_region)
            if allowed:
                satisfied.append(dr_tag)
            else:
                violated.append(dr_tag)

        for tag in required:
            if tag in ("HIPAA", "PIPL", "GDPR", "UK_GDPR", "CCPA", "APAC_PRIVACY") and tag not in satisfied and tag not in violated:
                satisfied.append(tag)

        if violated and self._strict_mode:
            return {
                "allowed": False,
                "region": effective_region,
                "satisfied": satisfied,
                "violated": violated,
                "message": "Compliance gate failed: one or more requirements violated.",
            }
        return {
            "allowed": len(violated) == 0,
            "region": effective_region,
            "satisfied": satisfied,
            "violated": violated,
            "message": "Compliance gate passed." if not violated else "Compliance gate passed with warnings.",
        }


# ------------------------------------------------------------------------------
# Optional: combined Nexus + Compliance pipeline
# ------------------------------------------------------------------------------
def route_and_gate(
    router: NexusRouter,
    gate: ComplianceGate,
    agid: str,
    subject_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resolve AGID via NexusRouter and run ComplianceGate for the resolved region.
    Returns physical mapping plus compliance result.
    """
    physical = router.resolve_agid(agid)
    region = router.map_agid_to_region(agid) if router else "NA"
    compliance = gate.enforce(region, subject_id=subject_id, data_region=region) if gate else {"allowed": True}
    return {
        "agid": agid,
        "physical_mapping": physical,
        "region": region,
        "compliance": compliance,
    }


if __name__ == "__main__":
    router = NexusRouter(default_region="NA")
    router.register_physical_mapping("AGID-MAYO-NODE-ABC123", "PHY-JAX-001", "NA", endpoint="https://nexus.example/jax")
    print("Resolve AGID:", router.resolve_agid("AGID-MAYO-NODE-ABC123"))

    gate = ComplianceGate(strict_mode=True)
    gate.record_consent("user_1", "EU")
    print("Enforce EU:", gate.enforce("EU", subject_id="user_1"))
    print("Route and gate:", route_and_gate(router, gate, "AGID-MAYO-NODE-ABC123", subject_id="user_1"))
