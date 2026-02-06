# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# AMANI Value Layer V4 — Sovereign Protocols
# ------------------------------------------------------------------------------
# Commercial logic (Insurance, Family Office, Pharma), full-lifecycle asset chains,
# and billing matrix gated by D <= GLOBAL_PRECISION_THRESHOLD.
# To B / To C Bridge: default TO_B_STRICT; APH_RESERVE_BUFFER reserved for future To C.
# Language: Strictly English.
# ------------------------------------------------------------------------------

from typing import Any, Dict, List, Optional
import hashlib

# ------------------------------------------------------------------------------
# Sovereign Protocol: precision gate (align with amani_core_v4)
# ------------------------------------------------------------------------------
try:
    from amani_core_v4 import GLOBAL_PRECISION_THRESHOLD, StrategicInterceptError
except Exception:
    GLOBAL_PRECISION_THRESHOLD = 0.79

    class StrategicInterceptError(Exception):
        """Raised when precision insufficient under Sovereign Protocols."""
        pass


# ------------------------------------------------------------------------------
# To B / To C Bridge
# ------------------------------------------------------------------------------
TO_B_STRICT = "TO_B_STRICT"
TO_C_EXPANSION = "TO_C_EXPANSION"
APH_RESERVE_BUFFER = 0.0  # Reserved for future To C expansion; not applied in TO_B_STRICT


def _to_agid(namespace: str, node_type: str, raw_id: Any) -> str:
    raw = f"{namespace}:{node_type}:{raw_id}"
    sid = hashlib.sha256(str(raw).encode()).hexdigest()[:12].upper()
    return f"AGID-{namespace}-{node_type}-{sid}"


# ------------------------------------------------------------------------------
# AMAHValueOrchestrator
# ------------------------------------------------------------------------------
class AMAHValueOrchestrator:
    """
    Value layer orchestrator under Sovereign Protocols.
    Handles Insurance, Family Office, and Pharma commercial logic;
    full-lifecycle asset chains (Treatment -> Recovery -> Psychology);
    billing matrix only active when D <= GLOBAL_PRECISION_THRESHOLD.
    Default mode: TO_B_STRICT; APH_RESERVE_BUFFER reserved for To C expansion.
    """

    def __init__(self, mode: str = TO_B_STRICT):
        self._mode = mode if mode in (TO_B_STRICT, TO_C_EXPANSION) else TO_B_STRICT
        self._aph_reserve = APH_RESERVE_BUFFER
        # Subscription tiers and per-match base rates (TO_B_STRICT)
        self._subscription_tiers = {
            "TRINITY_FULL": 299.0,
            "DEGRADED_DUAL": 149.0,
            "STRATEGIC_VETO": 0.0,
        }
        self._per_match_base = 500.0
        self._entity_handlers = {
            "Insurance": self._handle_insurance,
            "Family_Office": self._handle_family_office,
            "Pharma": self._handle_pharma,
        }
        self._lifecycle_chain = ["Treatment", "Recovery", "Psychology"]

    def _handle_insurance(self, asset_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Insurance entity: pre-auth, coverage validation, claims linkage."""
        return {
            "entity_type": "Insurance",
            "status": "PROCESSED",
            "pre_auth_eligible": asset_bundle.get("pre_auth_eligible", True),
            "coverage_tier": asset_bundle.get("coverage_tier", "STANDARD"),
            "claims_linked": True,
        }

    def _handle_family_office(self, asset_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Family Office entity: concierge, multi-jurisdiction, discretion."""
        return {
            "entity_type": "Family_Office",
            "status": "PROCESSED",
            "concierge_level": asset_bundle.get("concierge_level", "FULL"),
            "multi_jurisdiction": asset_bundle.get("multi_jurisdiction", True),
            "discretion": True,
        }

    def _handle_pharma(self, asset_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """Pharma entity: trial linkage, R&D alignment, compliance."""
        return {
            "entity_type": "Pharma",
            "status": "PROCESSED",
            "trial_linkage": asset_bundle.get("trial_linkage", False),
            "rd_alignment": asset_bundle.get("rd_alignment", True),
            "compliance_checked": True,
        }

    def process_commercial_logic(self, entity_type: str, asset_bundle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle commercial logic for Insurance, Family Office, or Pharma.
        entity_type: one of "Insurance", "Family_Office", "Pharma".
        asset_bundle: entity-specific parameters (coverage_tier, concierge_level, trial_linkage, etc.).
        Returns processed result under TO_B_STRICT (or To C when expanded).
        """
        handler = self._entity_handlers.get(entity_type)
        if handler is None:
            return {
                "entity_type": entity_type,
                "status": "UNSUPPORTED",
                "error": "Unknown entity type; supported: Insurance, Family_Office, Pharma.",
            }
        out = handler(asset_bundle)
        out["mode"] = self._mode
        return out

    def generate_full_lifecycle_strategy(self, initial_asset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a chain of assets: Treatment -> Recovery -> Psychology.
        initial_asset: seed asset (e.g. treatment or diagnosis); must contain at least "id" or "agid".
        Returns ordered list of lifecycle stages with derived AGIDs.
        """
        raw_id = initial_asset.get("id") or initial_asset.get("agid") or str(id(initial_asset))
        chain = []
        for i, stage_name in enumerate(self._lifecycle_chain):
            agid = _to_agid("VALUE", "LIFECYCLE", f"{raw_id}:{stage_name}")
            chain.append({
                "stage": stage_name,
                "sequence": i + 1,
                "agid": agid,
                "parent_id": raw_id,
                "metadata": initial_asset.get("metadata") or {},
            })
        return chain

    def calculate_billing_matrix(
        self,
        d_precision: float,
        agid_list: List[str],
        subscription_tier: Optional[str] = None,
        per_match_rates: Optional[Dict[str, float]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate fees only when D <= GLOBAL_PRECISION_THRESHOLD (Sovereign Protocol).
        If d_precision > 0.79, returns None (billing inactive).
        Fees: subscription-based (if subscription_tier provided) or per-match using per_match_rates or default base.
        """
        if d_precision > GLOBAL_PRECISION_THRESHOLD:
            return None
        n = len(agid_list) if agid_list else 0
        if n == 0:
            return {
                "active": True,
                "d_precision": d_precision,
                "agid_count": 0,
                "subscription_fee": 0.0,
                "per_match_total": 0.0,
                "total_fee": 0.0,
                "mode": self._mode,
            }
        # Subscription path
        if subscription_tier and subscription_tier in self._subscription_tiers:
            sub_fee = self._subscription_tiers[subscription_tier]
            per_match = (per_match_rates or {}).get(agid_list[0], self._per_match_base) if agid_list else 0.0
            # TO_B_STRICT: one subscription + optional per-match add-on for first asset
            per_match_total = per_match * min(n, 1) if self._mode == TO_B_STRICT else sum(
                (per_match_rates or {}).get(agid, self._per_match_base) for agid in agid_list
            )
            total = sub_fee + per_match_total + self._aph_reserve
            return {
                "active": True,
                "d_precision": d_precision,
                "agid_count": n,
                "subscription_tier": subscription_tier,
                "subscription_fee": sub_fee,
                "per_match_total": round(per_match_total, 2),
                "aph_reserve": self._aph_reserve,
                "total_fee": round(total, 2),
                "mode": self._mode,
            }
        # Per-match only
        rates = per_match_rates or {}
        per_match_total = sum(rates.get(agid, self._per_match_base) for agid in agid_list)
        total = per_match_total + self._aph_reserve
        return {
            "active": True,
            "d_precision": d_precision,
            "agid_count": n,
            "subscription_fee": 0.0,
            "per_match_total": round(per_match_total, 2),
            "aph_reserve": self._aph_reserve,
            "total_fee": round(total, 2),
            "mode": self._mode,
        }


if __name__ == "__main__":
    orch = AMAHValueOrchestrator()
    out = orch.process_commercial_logic("Insurance", {"coverage_tier": "PREMIUM"})
    print("Insurance:", out)
    chain = orch.generate_full_lifecycle_strategy({"id": "NCT123"})
    print("Lifecycle chain:", [c["stage"] for c in chain])
    matrix = orch.calculate_billing_matrix(0.75, ["AGID-VALUE-LIFECYCLE-ABC"], subscription_tier="TRINITY_FULL")
    print("Billing matrix (D<=0.79):", matrix)
    inactive = orch.calculate_billing_matrix(0.85, ["AGID-X"])
    print("Billing matrix (D>0.79):", inactive)
