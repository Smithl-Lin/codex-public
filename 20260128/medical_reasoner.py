# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Phase 4: MedicalReasoner — MedGemma endpoint (or stub when not configured).
Orchestrator: sovereignty audit (reasoning cost + compliance; path truncation).
BatchProcessQueue: concurrency limit + progress callback for L4 feedback.
"""
import os
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# A.M.A.N.I. System Prompt for MedGemma — AGID-aware, L3 resource matching
# ------------------------------------------------------------------------------
AMANI_SYSTEM_PROMPT = """You are the clinical reasoning module of A.M.A.N.I. (Mayo AI Asset Hub).
You must output structured JSON with:
1. strategy: list of {stage, sequence, category, agid, d_context} (category in Gold Standard/Frontier/Recovery).
2. intent_summary: brief clinical intent.
3. resource_matching_suggestion: REQUIRED. List of L3 physical assets to mobilize, e.g.:
   - imaging: ["MRI", "CT"] or []
   - therapeutics: ["drug_name_or_class"] or []
   - pi_experts: ["specialty_or_role"] or []
   Use AGID format (AGID-<namespace>-<type>-<hash) when referring to specific agents/resources.
Output must be parseable JSON."""

def _get_endpoint() -> Optional[str]:
    try:
        from config import get_medgemma_endpoint
        return get_medgemma_endpoint()
    except Exception:
        return os.getenv("MEDGEMMA_ENDPOINT")

def _get_finetune_version() -> str:
    try:
        from config import get_finetune_version
        return get_finetune_version()
    except Exception:
        return os.getenv("MEDGEMMA_FINETUNE_VERSION", "")


class MedicalReasoner:
    """
    Role: MedGemma (or local/Vertex medical model). Endpoint from config/env.
    When MEDGEMMA_ENDPOINT is not set, returns stub output compatible with StaircaseMappingLLM.
    """

    def __init__(self, endpoint: Optional[str] = None):
        self._endpoint = endpoint or _get_endpoint()
        self._finetune_version = _get_finetune_version()

    def get_system_prompt(self) -> str:
        """A.M.A.N.I. five-layer system prompt; AGID-aware, enforces resource_matching_suggestion."""
        return AMANI_SYSTEM_PROMPT

    def reason(self, input_text: str, l1_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run clinical reasoning on input. When endpoint is set, call MedGemma; else return stub.
        Output MUST include resource_matching_suggestion (L3 assets: imaging, therapeutics, pi_experts).
        Stub structure: {"strategy": [...], "intent_summary", "resource_matching_suggestion", "source": "stub"|"medgemma"}.
        """
        if not self._endpoint or not self._endpoint.strip():
            return self._stub_reason(input_text, l1_context or {})
        try:
            out = self._call_endpoint(input_text, l1_context or {})
            out.setdefault("resource_matching_suggestion", _default_resource_suggestion(out))
            return out
        except Exception as e:
            logger.warning("MedGemma endpoint failed, fallback to stub: %s", e)
            return self._stub_reason(input_text, l1_context or {})

    def _stub_reason(self, input_text: str, l1_context: Dict[str, Any]) -> Dict[str, Any]:
        """Stub: rule-based structure compatible with StaircaseMappingLLM; includes resource_matching_suggestion."""
        import hashlib
        def to_agid(ns: str, nt: str, raw: Any) -> str:
            r = f"{ns}:{nt}:{raw}"
            sid = hashlib.sha256(str(r).encode()).hexdigest()[:12].upper()
            return f"AGID-{ns}-{nt}-{sid}"
        d_eff = l1_context.get("d_effective", 0.79)
        steps = ["Diagnosis", "Treatment", "Recovery", "Follow-up"]
        cats = ["Gold Standard", "Frontier", "Recovery", "Recovery"]
        strategy = []
        for i, (stage, cat) in enumerate(zip(steps, cats), 1):
            strategy.append({
                "stage": stage,
                "sequence": i,
                "category": cat,
                "agid": to_agid("L2", "STEP", f"{input_text[:20]}:{cat}:{stage}:{i}"),
                "d_context": d_eff,
            })
        resource = _default_resource_suggestion({"strategy": strategy, "intent_summary": input_text[:200]})
        return {
            "strategy": strategy,
            "intent_summary": input_text[:200],
            "d_effective": d_eff,
            "resource_matching_suggestion": resource,
            "source": "stub",
            "finetune_version": self._finetune_version,
        }

    def _call_endpoint(self, input_text: str, l1_context: Dict[str, Any]) -> Dict[str, Any]:
        """Call MedGemma endpoint (HTTPS). Sends A.M.A.N.I. system prompt; expects resource_matching_suggestion."""
        import urllib.request
        import json
        try:
            from privacy_guard import redact_text
            safe_text, redaction_stats = redact_text(input_text)
            if any(redaction_stats.values()):
                logger.info("Outbound payload redacted for MedGemma: %s", redaction_stats)
        except Exception:
            safe_text = input_text
        payload = {
            "input_text": safe_text[:2000],
            "l1_context": l1_context,
            "system_prompt": self.get_system_prompt(),
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self._endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            out = json.loads(resp.read().decode("utf-8"))
        out["source"] = "medgemma"
        out.setdefault("finetune_version", self._finetune_version)
        return out


def _default_resource_suggestion(out: Dict[str, Any]) -> Dict[str, List[str]]:
    """Default L3 resource suggestion when MedGemma omits it. Inline AGID-style hints."""
    return out.get("resource_matching_suggestion") or {
        "imaging": ["MRI"],
        "therapeutics": [],
        "pi_experts": ["General"],
    }


class Orchestrator:
    """
    Sovereignty audit: reasoning cost + compliance score; path truncation or forced desensitization
    when L1 high-entropy alarm (per amah_config.json orchestrator_audit).
    """

    def __init__(self, config_path: Optional[str] = None):
        self._config = _load_orchestrator_config(config_path)

    def run(
        self,
        medical_output: Dict[str, Any],
        mode: str = "structured",
        l1_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Audit MedGemma output: compute reasoning_cost and compliance_score.
        If L1 high variance or D over threshold, apply path truncation or forced desensitization per config.
        """
        l1 = l1_context or {}
        cfg = self._config
        d_eff = l1.get("d_effective") or medical_output.get("d_effective") or 0.79
        var_ent = l1.get("shannon_entropy_variance") or 0.0
        strategy = medical_output.get("strategy") or []

        reasoning_cost = _compute_reasoning_cost(medical_output)
        compliance_score = _compute_compliance_score(medical_output, cfg)

        truncate = False
        desensitize = False
        if cfg.get("path_truncation_on_high_entropy"):
            var_limit = cfg.get("variance_limit_for_truncation", 0.005)
            d_limit = cfg.get("d_threshold_for_truncation", 0.79)
            if var_ent > var_limit or d_eff > d_limit:
                truncate = True
            if compliance_score < cfg.get("compliance_score_min", 0.5) or reasoning_cost > cfg.get("reasoning_cost_max", 1.0):
                if cfg.get("force_desensitize_on_fail"):
                    desensitize = True

        payload = dict(medical_output)
        if truncate and strategy:
            payload["strategy"] = strategy[:1]
            payload["_audit_truncated"] = True
        if desensitize:
            payload["intent_summary"] = (payload.get("intent_summary") or "")[:50] + "..."
            payload["resource_matching_suggestion"] = _desensitize_resource(payload.get("resource_matching_suggestion"))
            payload["_audit_desensitized"] = True

        return {
            "payload": payload,
            "mode": mode,
            "orchestrator_version": "audit",
            "reasoning_cost": reasoning_cost,
            "compliance_score": compliance_score,
            "path_truncated": truncate,
            "desensitized": desensitize,
        }


def _load_orchestrator_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    import json
    path = config_path or os.path.join(os.path.dirname(__file__), "amah_config.json")
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("orchestrator_audit", {})
    except Exception as e:
        logger.warning("Failed to load orchestrator config from %s: %s", path, e)
    return {}


def _compute_reasoning_cost(medical_output: Dict[str, Any]) -> float:
    """Stub: normalize to [0,1]. Real impl could use token count or API cost."""
    s = medical_output.get("strategy") or []
    return min(1.0, 0.1 + len(s) * 0.1)


def _compute_compliance_score(medical_output: Dict[str, Any], _cfg: Dict[str, Any]) -> float:
    """Stub: 0..1 from category and resource_matching_suggestion presence."""
    score = 0.5
    if medical_output.get("resource_matching_suggestion"):
        score += 0.3
    cats = [st.get("category") for st in (medical_output.get("strategy") or []) if st.get("category")]
    if any(c in ("Gold Standard", "Frontier", "Recovery") for c in cats):
        score += 0.2
    return min(1.0, score)


def _desensitize_resource(r: Any) -> Dict[str, List[str]]:
    """Strip specifics for forced desensitization."""
    if isinstance(r, dict):
        return {k: [] for k in ("imaging", "therapeutics", "pi_experts") if k in r}
    return {"imaging": [], "therapeutics": [], "pi_experts": []}


# Batch_Process queue: concurrency limit + progress for L4 feedback loop
class BatchProcessQueue:
    """
    Queue for MedGemma batch (L4 image/report). Concurrency limit; progress callback for UI.
    Hook: L4 can poll get_job_status(job_id) for reasoning progress; TrinityBridge can pass progress_callback when running batch.
    """

    def __init__(self, max_concurrency: int = 2):
        self._queue: List[Dict[str, Any]] = []
        self._max_concurrency = max(1, max_concurrency)
        self._lock = threading.Lock()
        self._job_status: Dict[str, Dict[str, Any]] = {}
        self._progress_callback: Optional[Callable[[str, float, str], None]] = None

    def set_progress_callback(self, cb: Callable[[str, float, str], None]) -> None:
        """Set callback(job_id, progress_0_to_1, message) for L4 real-time progress."""
        self._progress_callback = cb

    def enqueue(self, item: Dict[str, Any]) -> str:
        """Enqueue item (e.g. {"image_path": ..., "report_text": ...}). Returns job_id."""
        job_id = f"batch_{int(time.time() * 1000)}_{id(item) & 0x7FFFFFFF}"
        with self._lock:
            self._queue.append({"job_id": job_id, "item": item, "status": "queued", "progress": 0.0})
            self._job_status[job_id] = {"status": "queued", "progress": 0.0, "message": "Queued"}
        return job_id

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """For L4: poll reasoning progress (progress 0..1, message)."""
        with self._lock:
            return dict(self._job_status.get(job_id, {"status": "unknown", "progress": 0.0, "message": ""}))

    def _emit_progress(self, job_id: str, progress: float, message: str) -> None:
        with self._lock:
            if job_id in self._job_status:
                self._job_status[job_id]["progress"] = progress
                self._job_status[job_id]["message"] = message
        if self._progress_callback:
            try:
                self._progress_callback(job_id, progress, message)
            except Exception as e:
                logger.warning("Progress callback failed for %s: %s", job_id, e)

    def process_all(self) -> List[Dict[str, Any]]:
        """
        Process queue with concurrency limit. Emits progress per job so L4 can show progress bar.
        Stub: simulates steps; real impl would call MedGemma and report progress.
        """
        results = []
        with self._lock:
            to_process = list(self._queue)
            self._queue.clear()
        for i, q in enumerate(to_process):
            job_id = q["job_id"]
            self._emit_progress(job_id, 0.1, "Starting reasoning")
            time.sleep(0.05)
            self._emit_progress(job_id, 0.5, "MedGemma inference")
            time.sleep(0.05)
            self._emit_progress(job_id, 1.0, "Done")
            with self._lock:
                self._job_status[job_id] = {"status": "completed", "progress": 1.0, "message": "Done", "result": None}
            results.append({"job_id": job_id, "status": "stub", "result": None})
        return results
