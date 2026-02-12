import hashlib
import os
import re
from typing import Dict, Tuple


_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){2}\d{4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CN_ID_RE = re.compile(r"\b\d{17}[\dXx]\b")


def _salted_token(label: str, raw: str) -> str:
    salt = os.getenv("PHI_REDACTION_SALT", "amani_default_salt")
    digest = hashlib.sha256(f"{salt}:{label}:{raw}".encode("utf-8")).hexdigest()[:12].upper()
    return f"<{label}:{digest}>"


def redact_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Redact common PHI/PII patterns before outbound model/API calls.
    Returns (redacted_text, redaction_stats).
    """
    if not text:
        return text, {"email": 0, "phone": 0, "ssn": 0, "cn_id": 0}

    stats = {"email": 0, "phone": 0, "ssn": 0, "cn_id": 0}

    def _repl_email(m):
        stats["email"] += 1
        return _salted_token("EMAIL", m.group(0))

    def _repl_phone(m):
        stats["phone"] += 1
        return _salted_token("PHONE", m.group(0))

    def _repl_ssn(m):
        stats["ssn"] += 1
        return _salted_token("SSN", m.group(0))

    def _repl_cn_id(m):
        stats["cn_id"] += 1
        return _salted_token("CN_ID", m.group(0))

    out = _EMAIL_RE.sub(_repl_email, text)
    out = _PHONE_RE.sub(_repl_phone, out)
    out = _SSN_RE.sub(_repl_ssn, out)
    out = _CN_ID_RE.sub(_repl_cn_id, out)
    return out, stats

