# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# AMANI Interface Layer V4 — UIPresenter (Shadow Quote rendering) & FeedbackOptimizer (asset weights)
# ------------------------------------------------------------------------------
# Multi-modal interface structure: text, structured, html, markdown. Professional English.
# ------------------------------------------------------------------------------

from typing import Any, Callable, Dict, List, Optional
from enum import Enum
from datetime import datetime


class PresentationMode(str, Enum):
    """Multi-modal output: text, structured data, HTML, or Markdown."""
    TEXT = "text"
    STRUCTURED = "structured"
    HTML = "html"
    MARKDOWN = "markdown"


# ------------------------------------------------------------------------------
# UIPresenter — render Shadow Quotes across modalities
# ------------------------------------------------------------------------------
class UIPresenter:
    """
    Renders Shadow Quote data in multiple modalities for different consumers
    (CLI, API, web UI, reports). Multi-modal interface structure.
    """

    def __init__(self, default_mode: PresentationMode = PresentationMode.STRUCTURED):
        self._default_mode = default_mode

    def render_shadow_quote(
        self,
        quote_data: Dict[str, Any],
        mode: Optional[PresentationMode] = None,
    ) -> Any:
        """
        Render Shadow Quote in the requested modality.
        quote_data: dict from billing_engine.generate_quote or value layer calculate_billing_matrix.
        mode: TEXT | STRUCTURED | HTML | MARKDOWN. Returns string or dict per mode.
        """
        effective = mode or self._default_mode
        if effective == PresentationMode.TEXT:
            return self._shadow_quote_text(quote_data)
        if effective == PresentationMode.HTML:
            return self._shadow_quote_html(quote_data)
        if effective == PresentationMode.MARKDOWN:
            return self._shadow_quote_markdown(quote_data)
        return self._shadow_quote_structured(quote_data)

    def _shadow_quote_text(self, q: Dict[str, Any]) -> str:
        """Plain text summary for CLI or logs."""
        lines = [
            "--- Shadow Quote ---",
            f"Status: {q.get('status', q.get('nexus_status', 'N/A'))}",
            f"Total: {q.get('total_quote', q.get('total_fee', 0))} {q.get('currency', 'USD')}",
        ]
        if "breakdown" in q:
            b = q["breakdown"]
            lines.append(f"  Base / audit: {b.get('base_audit_purchase', 0)}")
            lines.append(f"  Subscription: {b.get('subscription_monthly', 0)}")
            lines.append(f"  Value-added: {b.get('value_added_services_total', 0)}")
        if q.get("d_precision") is not None:
            lines.append(f"D precision: {q['d_precision']}")
        if q.get("agid"):
            lines.append(f"AGID: {q['agid']}")
        return "\n".join(lines)

    def _shadow_quote_structured(self, q: Dict[str, Any]) -> Dict[str, Any]:
        """Structured payload for API or programmatic use."""
        return {
            "type": "shadow_quote",
            "agid": q.get("agid"),
            "status": q.get("status", q.get("nexus_status")),
            "total": q.get("total_quote", q.get("total_fee", 0)),
            "currency": q.get("currency", "USD"),
            "breakdown": q.get("breakdown", {}),
            "d_precision": q.get("d_precision"),
            "matched_services": q.get("matched_services", []),
            "ts": datetime.utcnow().isoformat() + "Z",
        }

    def _shadow_quote_html(self, q: Dict[str, Any]) -> str:
        """HTML snippet for web UI embedding."""
        total = q.get("total_quote", q.get("total_fee", 0))
        currency = q.get("currency", "USD")
        status = q.get("status", q.get("nexus_status", "N/A"))
        agid = q.get("agid", "")
        b = q.get("breakdown") or {}
        return f"""
        <div class="amani-shadow-quote" data-agid="{agid}">
            <div class="quote-status">{status}</div>
            <div class="quote-total">{total} {currency}</div>
            <ul class="quote-breakdown">
                <li>Base / audit: {b.get('base_audit_purchase', 0)}</li>
                <li>Subscription: {b.get('subscription_monthly', 0)}</li>
                <li>Value-added: {b.get('value_added_services_total', 0)}</li>
            </ul>
        </div>
        """.strip()

    def _shadow_quote_markdown(self, q: Dict[str, Any]) -> str:
        """Markdown for reports or docs."""
        total = q.get("total_quote", q.get("total_fee", 0))
        currency = q.get("currency", "USD")
        status = q.get("status", q.get("nexus_status", "N/A"))
        b = q.get("breakdown") or {}
        md = [
            "## Shadow Quote",
            f"- **Status:** {status}",
            f"- **Total:** {total} {currency}",
            f"- **Base / audit:** {b.get('base_audit_purchase', 0)}",
            f"- **Subscription:** {b.get('subscription_monthly', 0)}",
            f"- **Value-added:** {b.get('value_added_services_total', 0)}",
        ]
        if q.get("agid"):
            md.append(f"- **AGID:** `{q['agid']}`")
        return "\n".join(md)

    def present(
        self,
        payload: Dict[str, Any],
        mode: Optional[PresentationMode] = None,
        kind: str = "shadow_quote",
    ) -> Any:
        """
        Generic multi-modal present: dispatch by kind (e.g. shadow_quote, journey_plan).
        Ensures a single entry point for all interface-layer rendering.
        """
        if kind == "shadow_quote":
            return self.render_shadow_quote(payload, mode)
        if kind == "journey_plan":
            return self._render_journey_plan(payload, mode or self._default_mode)
        return self._shadow_quote_structured(payload)

    def _render_journey_plan(self, plan: List[Dict[str, Any]], mode: PresentationMode) -> Any:
        """Render multi-point journey plan in the requested modality."""
        if mode == PresentationMode.TEXT:
            return "\n".join([f"{s.get('sequence', i)}. {s.get('stage', '')} ({s.get('agid', '')})" for i, s in enumerate(plan, 1)])
        if mode == PresentationMode.MARKDOWN:
            return "\n".join([f"{i}. **{s.get('stage', '')}** — `{s.get('agid', '')}`" for i, s in enumerate(plan, 1)])
        if mode == PresentationMode.HTML:
            items = "".join([f"<li data-agid=\"{s.get('agid', '')}\">{s.get('stage', '')}</li>" for s in plan])
            return f"<ul class=\"amani-journey-plan\">{items}</ul>"
        return {"type": "journey_plan", "stages": plan}


# ------------------------------------------------------------------------------
# FeedbackOptimizer — update asset weights from feedback
# ------------------------------------------------------------------------------
class FeedbackOptimizer:
    """
    Updates asset weights from user or system feedback. Supports per-AGID and
    per-category weights, with optional decay and bounds. Multi-modal input:
    single update, batch update, or feedback event payload.
    """

    def __init__(
        self,
        initial_weights: Optional[Dict[str, float]] = None,
        min_weight: float = 0.0,
        max_weight: float = 2.0,
        decay_factor: float = 1.0,
    ):
        self._weights: Dict[str, float] = dict(initial_weights or {})
        self._min_weight = min_weight
        self._max_weight = max_weight
        self._decay_factor = decay_factor
        self._feedback_log: List[Dict[str, Any]] = []

    def get_weight(self, asset_id: str) -> float:
        """Return current weight for an asset (AGID or legacy id). Default 1.0."""
        return self._weights.get(asset_id, 1.0)

    def update_asset_weights(
        self,
        asset_id: str,
        delta: Optional[float] = None,
        absolute: Optional[float] = None,
    ) -> float:
        """
        Update weight for one asset. Either delta (relative) or absolute.
        Returns new weight after clamp to [min_weight, max_weight].
        """
        current = self._weights.get(asset_id, 1.0)
        if absolute is not None:
            new_val = absolute
        elif delta is not None:
            new_val = current + delta
        else:
            return current
        new_val = max(self._min_weight, min(self._max_weight, new_val))
        self._weights[asset_id] = new_val
        self._feedback_log.append({
            "ts": datetime.utcnow().isoformat() + "Z",
            "asset_id": asset_id,
            "previous": current,
            "new": new_val,
        })
        return new_val

    def batch_update_weights(
        self,
        updates: List[Dict[str, Any]],
        use_delta: bool = True,
    ) -> Dict[str, float]:
        """
        Apply multiple weight updates. Each item: {"asset_id": str, "delta": float} or {"asset_id": str, "absolute": float}.
        use_delta: if True, prefer "delta" key; else prefer "absolute". Returns dict of asset_id -> new weight.
        """
        result = {}
        for u in updates:
            aid = u.get("asset_id") or u.get("agid")
            if not aid:
                continue
            delta = u.get("delta") if use_delta else None
            absolute = u.get("absolute")
            if not use_delta:
                delta = None
            result[aid] = self.update_asset_weights(aid, delta=delta, absolute=absolute)
        return result

    def apply_feedback_event(self, event: Dict[str, Any]) -> Dict[str, float]:
        """
        Multi-modal input: accept a feedback event (e.g. from UI or API).
        Expected keys: "asset_id" or "agid", "rating" or "delta" or "absolute".
        Optional "category" for category-level weight. Returns updated weights for affected assets.
        """
        aid = event.get("asset_id") or event.get("agid")
        if not aid:
            return {}
        rating = event.get("rating")
        if rating is not None:
            delta = (float(rating) - 0.5) * 0.2
            return {aid: self.update_asset_weights(aid, delta=delta)}
        return {aid: self.update_asset_weights(
            aid,
            delta=event.get("delta"),
            absolute=event.get("absolute"),
        )}

    def get_all_weights(self) -> Dict[str, float]:
        """Return current weight map (copy)."""
        return dict(self._weights)

    def apply_decay(self) -> None:
        """Apply decay factor to all weights (e.g. for time-based decay)."""
        for k in self._weights:
            self._weights[k] = max(
                self._min_weight,
                min(self._max_weight, self._weights[k] * self._decay_factor),
            )


# ------------------------------------------------------------------------------
# Multi-modal interface facade (optional)
# ------------------------------------------------------------------------------
class InterfaceLayerV4:
    """
    Facade for Interface Layer V4: UIPresenter + FeedbackOptimizer.
    Single entry point for rendering and weight updates.
    """

    def __init__(self):
        self.presenter = UIPresenter()
        self.feedback_optimizer = FeedbackOptimizer()

    def render_shadow_quote(self, quote_data: Dict[str, Any], mode: Optional[PresentationMode] = None) -> Any:
        return self.presenter.render_shadow_quote(quote_data, mode)

    def update_asset_weights(self, asset_id: str, delta: Optional[float] = None, absolute: Optional[float] = None) -> float:
        return self.feedback_optimizer.update_asset_weights(asset_id, delta=delta, absolute=absolute)

    def present(self, payload: Dict[str, Any], mode: Optional[PresentationMode] = None, kind: str = "shadow_quote") -> Any:
        return self.presenter.present(payload, mode, kind)


# ------------------------------------------------------------------------------
# L4 Image upload stub (Phase 4) — reserve for MedGemma batch processing
# ------------------------------------------------------------------------------
def _get_batch_queue():
    """Singleton BatchProcessQueue for L4; hook for TrinityBridge progress_callback."""
    from medical_reasoner import BatchProcessQueue
    _queue = getattr(enqueue_image_for_batch, "_queue", None)
    if _queue is None:
        enqueue_image_for_batch._queue = BatchProcessQueue(max_concurrency=2)
        _queue = enqueue_image_for_batch._queue
    return _queue


def enqueue_image_for_batch(image_path_or_none: Optional[str] = None, report_text: Optional[str] = None) -> str:
    """
    Enqueue image + report for MedGemma Batch_Process. Returns job_id.
    Use get_batch_job_status(job_id) for L4 real-time progress (progress 0..1, message).
    """
    try:
        _queue = _get_batch_queue()
        job_id = _queue.enqueue({"image_path": image_path_or_none, "report_text": report_text or ""})
        return job_id
    except Exception:
        return "stub_job_0"


def get_batch_job_status(job_id: str) -> Dict[str, Any]:
    """
    L4 feedback: poll reasoning progress (progress 0..1, message) for UI progress bar.
    Hook: same queue as enqueue_image_for_batch; TrinityBridge can set progress_callback on this queue.
    """
    try:
        return _get_batch_queue().get_job_status(job_id)
    except Exception:
        return {"status": "unknown", "progress": 0.0, "message": ""}


def set_batch_progress_callback(callback: Optional[Callable[[str, float, str], None]]) -> None:
    """
    Set callback(job_id, progress_0_to_1, message) so L4/TrinityBridge feedback loop gets real-time progress.
    Call from app when rendering batch reasoning area; queue will invoke during process_all.
    """
    try:
        _get_batch_queue().set_progress_callback(callback)
    except Exception:
        pass


if __name__ == "__main__":
    q = {"status": "SUCCESS", "total_quote": 1234.56, "currency": "USD", "agid": "AGID-BILL-QUOTE-ABC", "breakdown": {"base_audit_purchase": 500, "subscription_monthly": 299, "value_added_services_total": 435.56}}
    presenter = UIPresenter()
    print("TEXT:", presenter.render_shadow_quote(q, PresentationMode.TEXT))
    print("STRUCTURED:", presenter.render_shadow_quote(q, PresentationMode.STRUCTURED))

    opt = FeedbackOptimizer()
    opt.update_asset_weights("AGID-MAYO-NODE-001", delta=0.1)
    print("Weights:", opt.get_all_weights())
