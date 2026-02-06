# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
L2 Cultural Main Complaint Equalizer.
Incorporates different cultural/language patient chief complaints (主诉),
produces equitable, canonical text for downstream model analysis.
Data: asset_library_l2/cultural_complaint_mapping.json.
Layer: L2 (asset/orchestration); invoked before StaircaseMappingLLM/MedicalReasoner.
"""
import os
import re
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_LIB = os.path.join(SCRIPT_DIR, "asset_library_l2")
MAPPING_FILE = os.path.join(ASSET_LIB, "cultural_complaint_mapping.json")

_config: Optional[Dict[str, Any]] = None


def _load_config() -> Dict[str, Any]:
    global _config
    if _config is not None:
        return _config
    try:
        if os.path.isfile(MAPPING_FILE):
            import json
            with open(MAPPING_FILE, "r", encoding="utf-8") as f:
                _config = json.load(f)
                return _config
    except Exception:
        pass
    _config = {"phrase_mappings": [], "locale_detection_rules": {}, "output_language": "en"}
    return _config


def _detect_locale(text: str) -> str:
    """Heuristic locale from script; returns en, zh, ja, ko, ar, or default."""
    if not text or not text.strip():
        return "default"
    cfg = _load_config()
    rules = cfg.get("locale_detection_rules") or {}
    for locale, patterns in rules.items():
        if locale == "default":
            continue
        for pat in patterns:
            if re.search(pat, text):
                return locale
    return "default"


def _apply_phrase_mappings(text: str, locale_hint: Optional[str] = None) -> Tuple[str, List[str]]:
    """
    Replace known cultural/language phrases with canonical (English) equivalents.
    Returns (equalized_text, list of canonical phrases appended for context).
    """
    cfg = _load_config()
    mappings = cfg.get("phrase_mappings") or []
    equalized = text.strip()
    canonical_additions: List[str] = []

    for entry in mappings:
        source_phrases = entry.get("source_phrases") or []
        canonical = entry.get("canonical_complaint") or ""
        if not canonical:
            continue
        for phrase in source_phrases:
            if not phrase or len(phrase) < 2:
                continue
            # Prefer exact substring for CJK; case-insensitive for Latin
            if re.search(re.escape(phrase), equalized, re.IGNORECASE if phrase.isascii() else 0):
                equalized = re.sub(
                    re.escape(phrase), canonical, equalized,
                    count=1, flags=re.IGNORECASE if phrase.isascii() else 0
                )
                if canonical not in canonical_additions:
                    canonical_additions.append(canonical)

    return equalized.strip(), canonical_additions


def equalize_main_complaint(
    raw_text: str,
    locale_hint: Optional[str] = None,
    append_canonical_context: bool = True,
) -> str:
    """
    Equalize patient main complaint (主诉) from different cultural/language input
    into canonical, equitable text for model analysis.

    - raw_text: User/patient chief complaint in any supported language.
    - locale_hint: Optional locale (en, zh, zh-HK, zh-SG, en-GB, de, fr, etc.).
    - append_canonical_context: If True, append a short canonical summary line for model.

    Returns: Normalized text suitable for downstream (StaircaseMappingLLM, MedicalReasoner).
    """
    if not raw_text or not raw_text.strip():
        return raw_text

    equalized, canonical_list = _apply_phrase_mappings(raw_text, locale_hint)
    if append_canonical_context and canonical_list:
        suffix = " [Canonical: " + "; ".join(canonical_list[:5]) + "]"
        if suffix not in equalized:
            equalized = equalized + suffix

    return equalized if equalized else raw_text.strip()


def equalize_for_analysis(raw_text: str, locale_hint: Optional[str] = None) -> Dict[str, Any]:
    """
    Full equalization result for L2 pipeline: equalized text + metadata (locale, canonical list).
    Use equalized_text for downstream model input.
    """
    locale = locale_hint or _detect_locale(raw_text)
    equalized, canonical_list = _apply_phrase_mappings(raw_text, locale_hint)
    if canonical_list:
        equalized = equalized + " [Canonical: " + "; ".join(canonical_list[:5]) + "]"
    return {
        "raw_input": raw_text[:500],
        "equalized_text": equalized if equalized else raw_text.strip(),
        "detected_locale": locale,
        "canonical_phrases": canonical_list,
        "layer": "L2_Cultural_Equalizer",
    }


if __name__ == "__main__":
    t = "患者主诉：帕金森，寻求DBS评估。"
    out = equalize_for_analysis(t)
    print("equalized_text:", out["equalized_text"].encode("utf-8", errors="replace").decode("utf-8"))
    print("canonical_phrases:", out["canonical_phrases"])
    t2 = "Patient with Parkinson's seeking DBS evaluation."
    out2 = equalize_for_analysis(t2)
    print("en equalized:", out2["equalized_text"])
