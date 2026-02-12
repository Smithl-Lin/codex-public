# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Trinity Neural Logic Bridge
# ------------------------------------------------------------------------------
# Flow: Input -> L1 (Entropy Gate) -> L2/2.5 (Semantic Path) -> L3 (GNN Mapping) -> L4 (Multi-modal UI).
# L1: ECNNSentinel monitors Shannon Entropy and enforces D <= 0.79.
# L2/2.5: StaircaseMappingLLM produces hierarchical strategy.
# L3: GNNAssetAnchor uses GAT-style logic to map intent to AGIDs.
# L4: Delegates to Interface Layer (UIPresenter). All docstrings in English.
# ------------------------------------------------------------------------------

import math
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None

# ------------------------------------------------------------------------------
# Layer 1 alignment (Sovereign Protocols)
# ------------------------------------------------------------------------------
try:
    from amani_core_v4 import (
        GLOBAL_PRECISION_THRESHOLD,
        to_agid,
        StrategicInterceptError,
    )
except Exception:
    GLOBAL_PRECISION_THRESHOLD = 0.79

    def to_agid(namespace: str, node_type: str, raw_id: Any) -> str:
        raw = f"{namespace}:{node_type}:{raw_id}"
        sid = hashlib.sha256(str(raw).encode()).hexdigest()[:12].upper()
        return f"AGID-{namespace}-{node_type}-{sid}"

    class StrategicInterceptError(Exception):
        """Raised when precision or entropy gate fails."""
        pass


logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# L1 (Sentinel): ECNNSentinel — Shannon Entropy gate, D <= 0.79
# ------------------------------------------------------------------------------
def _shannon_entropy(text: str, window_size: int = 5) -> Tuple[float, float]:
    """Compute Shannon entropy over sliding windows. Returns (mean_entropy, variance)."""
    tokens = list(text) if text else []
    if not tokens:
        return 0.0, 0.0
    entropies = []
    for i in range(len(tokens)):
        start = max(0, i - window_size // 2)
        end = min(len(tokens), i + window_size // 2 + 1)
        window = tokens[start:end]
        counts: Dict[str, int] = {}
        for t in window:
            counts[t] = counts.get(t, 0) + 1
        ent = 0.0
        n = len(window)
        for c in counts.values():
            p = c / n
            ent -= p * math.log2(p) if p > 0 else 0
        entropies.append(ent)
    mean_ent = sum(entropies) / len(entropies) if entropies else 0.0
    variance = sum((e - mean_ent) ** 2 for e in entropies) / len(entropies) if entropies else 0.0
    return mean_ent, variance


class ECNNSentinel:
    """
    L1 Sentinel: patent-aligned Shannon Entropy logic. D <= 0.79 gate is mandatory for all inputs.
    No input may proceed to L2 without passing the entropy gate and D threshold.
    """

    def __init__(self, d_threshold: float = GLOBAL_PRECISION_THRESHOLD, variance_limit: float = 0.005):
        self._d_threshold = d_threshold
        self._variance_limit = variance_limit
        assert d_threshold <= 0.79, "L1 hard-lock: D threshold must be <= 0.79"

    def gate(self, input_text: str) -> Tuple[bool, float, float, Optional[str]]:
        """
        Mandatory entropy gate for all inputs. Returns (passed, d_effective, entropy_variance, intercept_agid).
        D <= 0.79 is required; variance must not exceed limit. If failed, intercept_agid is set.
        """
        mean_ent, var_ent = _shannon_entropy(input_text)
        d_effective = min(1.0, 1.2 - mean_ent * 0.3)
        if var_ent > self._variance_limit:
            agid = to_agid("L1", "INTERCEPT", f"var_{var_ent:.6f}")
            return False, d_effective, var_ent, agid
        if d_effective > self._d_threshold:
            agid = to_agid("L1", "INTERCEPT", f"d_{d_effective:.4f}")
            return False, d_effective, var_ent, agid
        return True, d_effective, var_ent, None

    def monitor(self, input_text: str) -> Dict[str, Any]:
        """Monitor Shannon Entropy and D; return L1 status for downstream. Raises StrategicInterceptError if gate fails."""
        passed, d_eff, var_ent, intercept_agid = self.gate(input_text)
        if not passed:
            raise StrategicInterceptError(
                f"L1 Entropy Gate failed: D={d_eff:.4f} or variance={var_ent:.6f}; intercept={intercept_agid}"
            )
        return {
            "layer": "L1_Sentinel",
            "passed": True,
            "d_effective": d_eff,
            "shannon_entropy_variance": var_ent,
            "d_threshold": self._d_threshold,
        }


# ------------------------------------------------------------------------------
# L2/2.5 (Orchestrator): StaircaseMappingLLM — Gold Standard / Frontier / Recovery
# ------------------------------------------------------------------------------
ASSET_CATEGORY_GOLD_STANDARD = "Gold Standard"
ASSET_CATEGORY_FRONTIER = "Frontier"
ASSET_CATEGORY_RECOVERY = "Recovery"


class StaircaseMappingLLM:
    """
    L2/2.5 Orchestrator: categorizes assets into Gold Standard, Frontier, and Recovery.
    Generates hierarchical (staircase) strategy from input and L1 context.
    """

    def __init__(self, steps: Optional[List[str]] = None):
        self._default_steps = steps or ["Diagnosis", "Treatment", "Recovery", "Follow-up"]
        self._category_sequence = [ASSET_CATEGORY_GOLD_STANDARD, ASSET_CATEGORY_FRONTIER, ASSET_CATEGORY_RECOVERY]

    def _categorize_stage(self, stage: str, index: int) -> str:
        """Map stage to asset category: Gold Standard, Frontier, or Recovery."""
        if "Diagnosis" in stage or index == 1:
            return ASSET_CATEGORY_GOLD_STANDARD
        if "Treatment" in stage or index == 2:
            return ASSET_CATEGORY_FRONTIER
        return ASSET_CATEGORY_RECOVERY

    def generate(self, input_text: str, l1_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate hierarchical strategy with asset categories: Gold Standard, Frontier, Recovery.
        Each step has stage, sequence, category, and agid.
        """
        d_eff = l1_context.get("d_effective", 0.79)
        strategy = []
        for i, stage in enumerate(self._default_steps, 1):
            category = self._categorize_stage(stage, i)
            agid = to_agid("L2", "STEP", f"{input_text[:20]}:{category}:{stage}:{i}")
            strategy.append({
                "stage": stage,
                "sequence": i,
                "category": category,
                "agid": agid,
                "d_context": d_eff,
            })
        return strategy

    def semantic_path(self, input_text: str, l1_context: Dict[str, Any]) -> Dict[str, Any]:
        """L2.5 single semantic path: MedicalReasoner -> Orchestrator (amah_config.orchestrator_audit) -> L2 output. Fallback: StaircaseMappingLLM.generate."""
        try:
            from medical_reasoner import MedicalReasoner, Orchestrator
            reasoner = MedicalReasoner()
            out = reasoner.reason(input_text, l1_context)
            if out.get("strategy"):
                audit = Orchestrator().run(out, mode="structured", l1_context=l1_context)
                payload = audit.get("payload", out)
                return {
                    "layer": "L2_2_5_Orchestrator",
                    "strategy": payload.get("strategy", out["strategy"]),
                    "asset_categories": list(dict.fromkeys(s.get("category", "") for s in payload.get("strategy", []))),
                    "intent_summary": payload.get("intent_summary", input_text[:200]),
                    "d_effective": payload.get("d_effective", l1_context.get("d_effective")),
                    "reasoner_source": out.get("source", "stub"),
                    "resource_matching_suggestion": payload.get("resource_matching_suggestion"),
                    "orchestrator_audit": {
                        "reasoning_cost": audit.get("reasoning_cost"),
                        "compliance_score": audit.get("compliance_score"),
                        "path_truncated": audit.get("path_truncated"),
                        "desensitized": audit.get("desensitized"),
                    },
                }
        except Exception as e:
            logger.warning("L2.5 reasoner/orchestrator failed, fallback to local strategy: %s", e)
        steps = self.generate(input_text, l1_context)
        return {
            "layer": "L2_2_5_Orchestrator",
            "strategy": steps,
            "asset_categories": list(dict.fromkeys(s["category"] for s in steps)),
            "intent_summary": input_text[:200],
            "d_effective": l1_context.get("d_effective"),
        }


# ------------------------------------------------------------------------------
# Hard Anchor Boolean Interception: atomic technical terms and N=100 re-rank
# ------------------------------------------------------------------------------
def _load_hard_anchor_config(base_dir: str) -> Dict[str, Any]:
    """Load hard_anchor_boolean_interception from amah_config.json. Returns {} on error."""
    import os
    import json
    try:
        path = os.path.join(base_dir, "amah_config.json")
        if not os.path.isfile(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("hard_anchor_boolean_interception", {})
    except Exception:
        return {}


def _extract_hard_anchors(text: str, base_dir: str) -> List[str]:
    """
    Identify atomic-level technical terms (e.g. iPS, BCI, KRAS G12C) in case text.
    Returns list of terms that appear in text (case-insensitive substring match).
    """
    if not text:
        return []
    cfg = _load_hard_anchor_config(base_dir)
    terms = cfg.get("atomic_technical_terms") or [
        "iPS", "BCI", "DBS", "KRAS G12C", "G12C", "CAR-T", "ADC", "干细胞", "脑机接口",
        "Neural Interface", "Neuralink", "Dopaminergic", "Subthalamic", "mRNA Vaccine", "stem cell",
    ]
    text_lower = text.lower()
    found = []
    for t in terms:
        if t and t.lower() in text_lower:
            found.append(t)
    return found


# ------------------------------------------------------------------------------
# Protocol audit and concurrency guard (config-driven)
# ------------------------------------------------------------------------------
_bridge_semaphore = None
_bridge_semaphore_max = 0


def _get_bridge_semaphore(max_calls: int) -> Optional[Any]:
    """Return module-level semaphore for run_safe concurrency limit; create if needed."""
    global _bridge_semaphore, _bridge_semaphore_max
    if max_calls <= 0:
        return None
    if _bridge_semaphore is None or _bridge_semaphore_max != max_calls:
        try:
            import threading
            _bridge_semaphore = threading.Semaphore(max_calls)
            _bridge_semaphore_max = max_calls
        except Exception:
            return None
    return _bridge_semaphore


def _append_protocol_audit(base_dir: str, log_path: str, result: Dict[str, Any], intercepted: bool) -> None:
    """Append one line to sovereignty audit log: ts, intercepted, d_effective, variance, l3_origin."""
    import os as _os_audit
    import time
    path = log_path if _os_audit.path.isabs(log_path) else _os_audit.path.join(base_dir, log_path)
    l1 = result.get("l1_sentinel") or {}
    d = l1.get("d_effective")
    var = l1.get("shannon_entropy_variance")
    l3 = result.get("l3_nexus") or {}
    origin = l3.get("l3_origin", "")
    ts = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    line = f"{ts}\tintercepted={intercepted}\td_effective={d}\tvariance={var}\tl3_origin={origin}\n"
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
    except Exception:
        pass


# ------------------------------------------------------------------------------
# L3 (Nexus): GNNAssetAnchor — GAT-style mapping from intent to AGIDs
# ------------------------------------------------------------------------------
class GNNAssetAnchor:
    """
    L3 Nexus: maps intent (and L2 strategy) to AGIDs using GAT-style logic or ChromaDB.
    When chromadb_path/collection_name are set, queries ChromaDB; otherwise uses in-memory asset table.
    """

    def __init__(
        self,
        num_assets: int = 100,
        feature_dim: int = 64,
        chromadb_path: Optional[str] = None,
        collection_name: str = "expert_map_global",
    ):
        self._num_assets = num_assets
        self._feature_dim = feature_dim
        self._asset_embed: Optional[Any] = np.ndarray if np else None
        self._asset_agids: List[str] = []
        self._chroma_client = None
        self._chroma_collection = None
        self._cached_count = None  # Cache count() to avoid repeated slow calls
        if chromadb_path:
            try:
                import chromadb
                self._chroma_client = chromadb.PersistentClient(path=chromadb_path)
                self._chroma_collection = self._chroma_client.get_collection(collection_name)
                # Cache count on init to avoid slow calls during batch processing
                try:
                    self._cached_count = self._chroma_collection.count()
                except Exception:
                    self._cached_count = None
            except Exception:
                self._chroma_client = None
                self._chroma_collection = None
        if self._chroma_collection is None:
            self._init_fake_assets()
        else:
            self._asset_agids = []
            self._asset_embed = None

    def _init_fake_assets(self) -> None:
        """Initialize a small asset table with fake embeddings and AGIDs (fallback)."""
        if np is not None:
            self._asset_embed = np.random.randn(self._num_assets, self._feature_dim).astype(np.float32) * 0.1
        else:
            self._asset_embed = None
        self._asset_agids = [to_agid("L3", "ASSET", i) for i in range(self._num_assets)]

    def _intent_to_vector(self, intent_summary: str) -> Any:
        """Convert intent text to a feature vector (simple hash-based for non-torch)."""
        if np is None:
            return [hash(intent_summary + str(i)) % 1000 / 1000.0 for i in range(self._feature_dim)]
        vec = np.zeros(self._feature_dim, dtype=np.float32)
        for i, c in enumerate(intent_summary[: self._feature_dim]):
            vec[i % self._feature_dim] += hash(c) % 1000 / 1000.0
        if len(intent_summary) < self._feature_dim:
            vec[len(intent_summary) % self._feature_dim] = 1.0
        return vec / (np.linalg.norm(vec) + 1e-8)

    def map_to_agids(
        self,
        intent_summary: str,
        top_k: int = 5,
        retrieval_pool_n: Optional[int] = None,
        hard_anchors: Optional[List[str]] = None,
        downgrade_firewall: bool = True,
    ) -> List[Tuple[str, float]]:
        """
        Return top-k (agid, score). First retrieves up to retrieval_pool_n (default 100) candidates;
        if hard_anchors present and downgrade_firewall, re-ranks by hard-anchor coverage (firewall
        against downgrade matching), then returns top_k.
        """
        pool_n = retrieval_pool_n if retrieval_pool_n is not None else 100
        if self._chroma_collection is not None and intent_summary:
            try:
                # Use cached count to avoid slow repeated calls during batch processing
                total = self._cached_count if self._cached_count is not None else self._chroma_collection.count()
                n_results = min(max(pool_n, top_k), total) if total else top_k
                include = ["distances"]
                if hard_anchors and downgrade_firewall:
                    include = ["distances", "documents", "metadatas"]
                res = self._chroma_collection.query(
                    query_texts=[intent_summary[:2000]],
                    n_results=n_results,
                    include=include,
                )
                ids = (res.get("ids") or [[]])[0]
                dists = (res.get("distances") or [[]])[0]
                docs = (res.get("documents") or [[]])[0] if "documents" in include else []
                metas = (res.get("metadatas") or [[]])[0] if "metadatas" in include else []
                out = []
                for i, aid in enumerate(ids):
                    d = dists[i] if i < len(dists) else 0.0
                    score = max(0.0, 1.0 - d) if d else 1.0
                    out.append((aid, float(score), docs[i] if i < len(docs) else "", metas[i] if i < len(metas) else {}))
                if hard_anchors and downgrade_firewall and out:
                    # Re-rank: candidates that contain any hard_anchor go first, then by score
                    def _has_anchor(item: Tuple) -> bool:
                        _, _, doc, meta = item
                        text = (doc or "") + " " + str(meta or "")
                        text_lower = text.lower()
                        return any(a and a.lower() in text_lower for a in hard_anchors)
                    with_anchor = [(a, s) for a, s, d, m in out if _has_anchor((a, s, d, m))]
                    without_anchor = [(a, s) for a, s, d, m in out if not _has_anchor((a, s, d, m))]
                    with_anchor.sort(key=lambda x: x[1], reverse=True)
                    without_anchor.sort(key=lambda x: x[1], reverse=True)
                    out = with_anchor + without_anchor
                else:
                    out = [(a, s) for a, s, _, _ in out]
                    out.sort(key=lambda x: x[1], reverse=True)
                return out[:top_k]
            except Exception:
                pass
        # Fallback: original single-phase top_k (no pool)
        if self._chroma_collection is not None and intent_summary:
            try:
                res = self._chroma_collection.query(
                    query_texts=[intent_summary[:2000]],
                    n_results=min(top_k, self._chroma_collection.count()),
                    include=["distances"],
                )
                ids = (res.get("ids") or [[]])[0]
                dists = (res.get("distances") or [[]])[0]
                out = []
                for i, aid in enumerate(ids):
                    d = dists[i] if i < len(dists) else 0.0
                    score = max(0.0, 1.0 - d) if d else 1.0
                    out.append((aid, float(score)))
                if out:
                    return out
            except Exception:
                pass
        q = self._intent_to_vector(intent_summary)
        if np is not None and self._asset_embed is not None:
            q_arr = np.array(q, dtype=np.float32).reshape(1, -1)
            scores = np.dot(self._asset_embed, q_arr.T).flatten()
            top_indices = np.argsort(scores)[-top_k:][::-1]
            return [(self._asset_agids[i], float(scores[i])) for i in top_indices]
        out = []
        for i in range(min(top_k, len(self._asset_agids))):
            out.append((self._asset_agids[i], 1.0 - i * 0.1))
        return out

    def forward(self, semantic_path: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        """
        Map L2 semantic path to AGIDs. Uses retrieval_pool_n (default 100) and hard_anchors
        for secondary re-rank (downgrade firewall) when configured.
        """
        intent = semantic_path.get("intent_summary", "")
        hard_anchors = semantic_path.get("hard_anchors") or []
        retrieval_pool_n = semantic_path.get("retrieval_pool_size_n")
        downgrade_firewall = semantic_path.get("downgrade_firewall", True)
        agid_scores = self.map_to_agids(
            intent,
            top_k=top_k,
            retrieval_pool_n=retrieval_pool_n,
            hard_anchors=hard_anchors if hard_anchors else None,
            downgrade_firewall=downgrade_firewall,
        )
        l3_origin = "chromadb" if self._chroma_collection is not None else "fallback"
        return {
            "layer": "L3_Nexus",
            "agids": [a for a, _ in agid_scores],
            "scores": [s for _, s in agid_scores],
            "intent_summary": intent,
            "hard_anchors_used": hard_anchors if hard_anchors else None,
            "l3_origin": l3_origin,
        }


# ------------------------------------------------------------------------------
# End-to-end flow: Input -> L1 -> L2/2.5 -> L3 -> L4
# ------------------------------------------------------------------------------
class TrinityBridge:
    """
    Single entry for Trinity Neural Logic:
    Input -> L1 (Entropy Gate) -> L2/2.5 (Semantic Path) -> L3 (GNN Mapping) -> L4 (Multi-modal UI).
    """

    def __init__(
        self,
        l1_sentinel: Optional[ECNNSentinel] = None,
        l2_llm: Optional[StaircaseMappingLLM] = None,
        l3_anchor: Optional[GNNAssetAnchor] = None,
        chromadb_path: Optional[str] = None,
    ):
        import os
        import json
        base = os.path.dirname(os.path.abspath(__file__))
        variance_limit = 0.005
        try:
            cfg_path = os.path.join(base, "amah_config.json")
            if os.path.isfile(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                v = cfg.get("trinity_audit_gate", {}).get("variance_limit_numeric")
                if v is not None:
                    variance_limit = float(v)
        except Exception as e:
            logger.warning("Failed to load trinity_audit_gate config, using default variance_limit=0.005: %s", e)
        self._l1 = l1_sentinel or ECNNSentinel(variance_limit=variance_limit)
        self._l2 = l2_llm or StaircaseMappingLLM()
        chroma = chromadb_path or os.path.join(base, "amah_vector_db")
        self._l3 = l3_anchor or GNNAssetAnchor(chromadb_path=chroma if os.path.isdir(chroma) else None)

    def run(
        self,
        input_text: str,
        top_k_agids: int = 5,
        include_l4_output: bool = True,
    ) -> Dict[str, Any]:
        """
        Run full pipeline. If L1 gate fails, raises StrategicInterceptError.
        Otherwise returns aggregated L1/L2/L3 outputs and, if include_l4_output, L4 multi-modal payload.
        """
        l1_ctx = self._l1.monitor(input_text)
        d_eff = l1_ctx.get("d_effective") or 0.79
        centurion_snapshot = None
        if d_eff <= GLOBAL_PRECISION_THRESHOLD:
            import os as _os_b
            _base = _os_b.path.dirname(_os_b.path.abspath(__file__))
            _cfg_path = _os_b.path.join(_base, "amah_config.json")
            _cent_enabled = False
            _cent_timeout = 5.0
            try:
                import json as _json
                if _os_b.path.isfile(_cfg_path):
                    with open(_cfg_path, "r", encoding="utf-8") as _f:
                        _c = _json.load(_f)
                    _cent_cfg = _c.get("centurion_injection") or {}
                    _cent_enabled = _cent_cfg.get("enabled", False)
                    _cent_timeout = float(_cent_cfg.get("timeout_seconds", 5))
            except Exception as e:
                logger.warning("Failed to load centurion_injection config, using defaults: %s", e)
            if _cent_enabled:
                import threading as _th
                _result = [None]
                _exc = [None]
                def _get():
                    try:
                        from amah_centurion_injection import AMAHCenturionInjector
                        inj = AMAHCenturionInjector(start_pulse_background=False)
                        _result[0] = inj.get_latest_snapshot(d_eff)
                    except Exception as e:
                        _exc[0] = e
                _t = _th.Thread(target=_get, daemon=True)
                _t.start()
                _t.join(timeout=_cent_timeout)
                centurion_snapshot = _result[0] if not _exc[0] and not _t.is_alive() else None
        # L2 cultural equalization: multilingual/cultural chief complaint -> equitable text for model
        text_for_l2 = input_text
        try:
            from amani_cultural_equalizer_l2 import equalize_main_complaint
            text_for_l2 = equalize_main_complaint(input_text, locale_hint=None, append_canonical_context=True)
        except Exception as e:
            logger.warning("Cultural equalizer failed, using raw input: %s", e)
        l2_path = self._l2.semantic_path(text_for_l2, l1_ctx)
        # Hard Anchor Boolean Interception: atomic technical terms (iPS, BCI, KRAS G12C) and N=100 re-rank
        import os as _os
        base = _os.path.dirname(_os.path.abspath(__file__))
        hard_anchors = _extract_hard_anchors(input_text or text_for_l2 or "", base)
        hab_cfg = _load_hard_anchor_config(base)
        l2_path["hard_anchors"] = hard_anchors
        l2_path["retrieval_pool_size_n"] = hab_cfg.get("retrieval_pool_size_n", 100)
        l2_path["downgrade_firewall"] = hab_cfg.get("downgrade_firewall", True)
        l3_out = self._l3.forward(l2_path, top_k=top_k_agids)
        out = {
            "l1_sentinel": l1_ctx,
            "centurion_snapshot": centurion_snapshot,
            "l2_2_5_semantic_path": l2_path,
            "l3_nexus": l3_out,
            "d_effective": d_eff,
        }
        if text_for_l2 != input_text:
            out["l2_equalized_input"] = text_for_l2
        if include_l4_output:
            try:
                from amani_interface_layer_v4 import UIPresenter, PresentationMode
                presenter = UIPresenter()
                shadow_quote_stub = {
                    "status": "SUCCESS",
                    "total_quote": 0.0,
                    "currency": "USD",
                    "agid": l3_out.get("agids", [None])[0] if l3_out.get("agids") else None,
                    "breakdown": {},
                }
                out["l4_multimodal"] = {
                    "shadow_quote_structured": presenter.render_shadow_quote(shadow_quote_stub, PresentationMode.STRUCTURED),
                    "shadow_quote_html": presenter.render_shadow_quote(shadow_quote_stub, PresentationMode.HTML),
                    "shadow_quote_markdown": presenter.render_shadow_quote(shadow_quote_stub, PresentationMode.MARKDOWN),
                    "shadow_quote_text": presenter.render_shadow_quote(shadow_quote_stub, PresentationMode.TEXT),
                    "strategy_stages": l2_path.get("strategy", []),
                }
            except Exception:
                out["l4_multimodal"] = {"strategy_stages": l2_path.get("strategy", [])}
        return out

    def run_safe(self, input_text: str, top_k_agids: int = 5) -> Dict[str, Any]:
        """
        Single sovereign entry point for Trinity Neural Logic.
        Run pipeline; on L1 failure return intercept result instead of raising.
        Flow: Input -> L1 (Entropy Gate) -> L2/2.5 (Semantic Path) -> L3 (GNN Mapping) -> L4 (Multi-modal UI).
        Optional: protocol_audit log (D, variance, l3_origin, intercepted); concurrency_guard semaphore.
        """
        import os as _os_s
        _base_s = _os_s.path.dirname(_os_s.path.abspath(__file__))
        _cfg_path_s = _os_s.path.join(_base_s, "amah_config.json")
        _proto_enabled = False
        _proto_path = "sovereignty_audit.log"
        _guard_enabled = False
        _guard_max = 8
        _guard_timeout = 30.0
        try:
            import json as _json_s
            if _os_s.path.isfile(_cfg_path_s):
                with open(_cfg_path_s, "r", encoding="utf-8") as _f:
                    _c = _json_s.load(_f)
                _proto_cfg = _c.get("protocol_audit") or {}
                _proto_enabled = _proto_cfg.get("enabled", False)
                _proto_path = _proto_cfg.get("log_path", _proto_path)
                _guard_cfg = _c.get("concurrency_guard") or {}
                _guard_enabled = _guard_cfg.get("enabled", False)
                _guard_max = int(_guard_cfg.get("max_concurrent_bridge_calls", 8))
                _guard_timeout = float(_guard_cfg.get("timeout_seconds", 30))
        except Exception as e:
            logger.warning("Failed to load protocol_audit/concurrency_guard config, using defaults: %s", e)
        _sem = _get_bridge_semaphore(_guard_max)
        _acquired = False
        if _guard_enabled and _sem is not None:
            try:
                _acquired = _sem.acquire(timeout=_guard_timeout)
            except Exception:
                _acquired = False
            if not _acquired:
                result = {
                    "l1_sentinel": {"passed": False, "error": "Concurrency guard timeout"},
                    "l2_2_5_semantic_path": None,
                    "l3_nexus": None,
                    "intercepted": True,
                }
                if _proto_enabled:
                    _append_protocol_audit(_base_s, _proto_path, result, intercepted=True)
                return result
        try:
            result = self.run(input_text, top_k_agids=top_k_agids, include_l4_output=True)
            if _proto_enabled:
                _append_protocol_audit(_base_s, _proto_path, result, intercepted=False)
            return result
        except StrategicInterceptError as e:
            result = {
                "l1_sentinel": {"passed": False, "error": str(e)},
                "l2_2_5_semantic_path": None,
                "l3_nexus": None,
                "intercepted": True,
            }
            if _proto_enabled:
                _append_protocol_audit(_base_s, _proto_path, result, intercepted=True)
            return result
        finally:
            if _guard_enabled and _sem is not None and _acquired:
                _sem.release()


if __name__ == "__main__":
    bridge = TrinityBridge()
    result = bridge.run_safe("Patient with Parkinson's seeking DBS evaluation", top_k_agids=3)
    print("L1 passed:", result.get("l1_sentinel", {}).get("passed"))
    print("L3 AGIDs:", result.get("l3_nexus", {}).get("agids"))
    print("L4 keys:", list(result.get("l4_multimodal", {}).keys()) if result.get("l4_multimodal") else None)
