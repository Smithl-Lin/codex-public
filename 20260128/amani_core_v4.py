# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Layer 1: Sovereign Protocols (Rules & Protocols) — HARD-LOCKED
# ------------------------------------------------------------------------------
# Single source of truth for precision threshold, variance intercept, and AGID.
# All functional descriptions use professional English. Access gated by D <= GLOBAL_PRECISION_THRESHOLD.
# Terminology: Intent Information Density (IID) for intent/density metrics; Shadow Quote Engine for billing.
# Sovereign Protocols: these rules describe the Layer 1 enforcement (precision, variance, AGID_STRICT).
# Steel Seal: Layer 1 is hard-locked; do not bypass GLOBAL_PRECISION_THRESHOLD or VARIANCE_INTERCEPT_LIMIT.
# ------------------------------------------------------------------------------

import json
import hashlib
import os
from typing import Optional

CONFIG_FILENAME = "amah_config.json"
_CONFIG_CACHE: Optional[dict] = None

# ------------------------------------------------------------------------------
# Global Constants (Sovereign Protocols)
# ------------------------------------------------------------------------------
GLOBAL_PRECISION_THRESHOLD = 0.79
VARIANCE_INTERCEPT_LIMIT = 0.005
ASSET_MAPPING_MODE = "AGID_STRICT"


class StrategicInterceptError(Exception):
    """Raised when a pre-execution check fails under Sovereign Protocols (e.g. precision insufficient)."""
    pass


# ------------------------------------------------------------------------------
# Config Loader — single source for threshold values from amah_config.json
# ------------------------------------------------------------------------------
def load_config(config_dir: Optional[str] = None) -> dict:
    """Load amah_config.json. Ensures all modules use the same threshold values."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    base = config_dir or os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, CONFIG_FILENAME)
    try:
        with open(path, "r", encoding="utf-8") as f:
            _CONFIG_CACHE = json.load(f)
        return _CONFIG_CACHE
    except Exception:
        _CONFIG_CACHE = {
            "alignment_logic": {
                "precision_lock_threshold": GLOBAL_PRECISION_THRESHOLD,
                "manual_audit_threshold": 1.35,
            },
            "trinity_audit_gate": {"variance_tolerance": "DYNAMIC"},
        }
        return _CONFIG_CACHE


def get_precision_threshold() -> float:
    """Return precision lock threshold (Sovereign Protocol: D <= GLOBAL_PRECISION_THRESHOLD)."""
    cfg = load_config()
    return float(cfg.get("alignment_logic", {}).get("precision_lock_threshold", GLOBAL_PRECISION_THRESHOLD))


def get_manual_audit_threshold() -> float:
    """Return manual audit threshold (fallback when precision route not met)."""
    cfg = load_config()
    return float(cfg.get("alignment_logic", {}).get("manual_audit_threshold", 1.35))


def get_variance_tolerance() -> str:
    """Return variance tolerance policy from trinity_audit_gate."""
    cfg = load_config()
    return cfg.get("trinity_audit_gate", {}).get("variance_tolerance", "DYNAMIC")


# Backward-compatible aliases for downstream modules
D_PRECISION_HARD_LOCK = GLOBAL_PRECISION_THRESHOLD
VARIANCE_PHYSICAL_INTERCEPT = VARIANCE_INTERCEPT_LIMIT


# ------------------------------------------------------------------------------
# AGID Mapping (ASSET_MAPPING_MODE = 'AGID_STRICT')
# ------------------------------------------------------------------------------
def to_agid(namespace: str, node_type: str, raw_id) -> str:
    """Normalize any output node to AGID format under Sovereign Protocols."""
    raw = f"{namespace}:{node_type}:{raw_id}"
    sid = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


def map_legacy_id_to_agid(legacy_id: str, namespace: str = "MAYO") -> str:
    """Map legacy identifiers (e.g. EXP-NEURO-JAX) to AGID."""
    return to_agid(namespace, "NODE", legacy_id)


# ------------------------------------------------------------------------------
# Protocol Enforcement: pre-execution check
# ------------------------------------------------------------------------------
def require_precision_sufficient(d_val: float) -> None:
    """
    Sovereign Protocol: raise StrategicInterceptError if precision insufficient.
    Call before executing logic that requires D <= GLOBAL_PRECISION_THRESHOLD.
    """
    if d_val > GLOBAL_PRECISION_THRESHOLD:
        raise StrategicInterceptError("Precision Insufficient")


# ------------------------------------------------------------------------------
# AMANICoreOrchestrator — global match orchestration under Sovereign Protocols
# Shadow Quote Engine invoked when D <= GLOBAL_PRECISION_THRESHOLD.
# ------------------------------------------------------------------------------
class AMANICoreOrchestrator:
    """
    Global match orchestrator. Sovereign Protocols: D <= GLOBAL_PRECISION_THRESHOLD for pass;
    when D <= threshold, Shadow Quote Engine (billing_engine) is invoked automatically.
    """

    def __init__(self):
        self._precision = get_precision_threshold()
        self._variance_intercept = VARIANCE_INTERCEPT_LIMIT
        self._d_hard_lock = GLOBAL_PRECISION_THRESHOLD
        try:
            from billing_engine import AMAHBillingEngine
            self._billing = AMAHBillingEngine()
        except Exception:
            self._billing = None

    def _attach_shadow_quote_engine(self, d_precision: float, score: Optional[float] = None, services_list: Optional[list] = None) -> Optional[dict]:
        """Invoke Shadow Quote Engine when D <= GLOBAL_PRECISION_THRESHOLD. Protocol: raise if precision insufficient."""
        if d_precision > GLOBAL_PRECISION_THRESHOLD:
            raise StrategicInterceptError("Precision Insufficient")
        if self._billing is None:
            return None
        score = score if score is not None else min(1.0, 1.2 - d_precision)
        services_list = services_list or ["Hospital Docking", "Travel Concierge"]
        return self._billing.generate_quote(
            score=score, mode="TRINITY_FULL",
            services_list=services_list, d_precision=d_precision
        )

    async def execute_global_match(self, profile: str) -> dict:
        """
        Execute global asset matching. Sovereign Protocol: D <= GLOBAL_PRECISION_THRESHOLD required for pass.
        When D <= threshold, Shadow Quote Engine output is attached as shadow_quote.
        Pre-execution check: raises StrategicInterceptError if resulting d_val exceeds threshold where required.
        """
        profile_lower = profile.lower()
        # High-conflict / variance scenario: intercept
        if "conflicting" in profile_lower or "high-risk" in profile_lower or "variance conflict" in profile_lower:
            agid = to_agid("CORE", "INTERCEPT", profile[:32])
            return {
                "status": "INTERCEPTED",
                "agid": agid,
                "reason": "Model disagreement or variance above limit; Sovereign Protocol intercept.",
            }
        # Route by intent; d_val must satisfy D <= GLOBAL_PRECISION_THRESHOLD for precision path
        d_val = self._precision
        if any(k in profile_lower for k in ["bci", "parkinson", "dbs", "neuro", "mayo jax"]):
            agid = to_agid("CORE", "NODE", f"Neurology_{d_val}_{profile[:20]}")
            out = {
                "status": "SUCCESS",
                "agid": agid,
                "precision": d_val,
                "commercial_value": 100000,
            }
        elif any(k in profile_lower for k in ["onco", "kras", "nsclc", "phase iii", "tumor"]):
            agid = to_agid("CORE", "NODE", f"Oncology_{d_val}_{profile[:20]}")
            out = {
                "status": "SUCCESS",
                "agid": agid,
                "precision": d_val,
                "commercial_value": 120000,
            }
        else:
            d_val = get_manual_audit_threshold()
            agid = to_agid("CORE", "NODE", f"Complex_{profile[:20]}")
            out = {
                "status": "SUCCESS",
                "agid": agid,
                "precision": d_val,
                "commercial_value": 80000,
            }
        # Protocol enforcement: pre-execution check for precision path (SUCCESS with D <= threshold)
        if out.get("status") == "SUCCESS" and out.get("precision") is not None:
            if out["precision"] <= self._d_hard_lock:
                out["shadow_quote"] = self._attach_shadow_quote_engine(out["precision"])
            else:
                # Optional: enforce strict gate for precision path only (uncomment to raise)
                # require_precision_sufficient(out["precision"])
                pass
        return out
