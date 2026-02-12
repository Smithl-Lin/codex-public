"""
Write-free deterministic QA smoke for local environments.
This script avoids bytecode writes and focuses on fast, reproducible checks.
"""
import ast
import os
import sys
from pathlib import Path


sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"


ROOT = Path(__file__).resolve().parent


def _ast_check(paths):
    for p in paths:
        src = p.read_text(encoding="utf-8", errors="replace")
        ast.parse(src)


def _functional_check():
    sys.path.insert(0, str(ROOT))
    from privacy_guard import redact_text
    from amani_nexus_layer_v3 import ComplianceGate

    redacted, stats = redact_text("john@example.com 555-123-4567 123-45-6789")
    if "<EMAIL:" not in redacted or "<PHONE:" not in redacted:
        raise RuntimeError("privacy_guard redaction failed")
    if stats["email"] < 1 or stats["phone"] < 1:
        raise RuntimeError("privacy_guard stats failed")

    gate = ComplianceGate(strict_mode=True)
    if gate.enforce("US", subject_id="u1", data_region="US")["allowed"]:
        raise RuntimeError("consent gate failed: expected blocked without consent")
    gate.record_consent("u1", "US")
    if not gate.enforce("US", subject_id="u1", data_region="US")["allowed"]:
        raise RuntimeError("consent gate failed: expected allowed with consent")


def main():
    targets = [
        ROOT / "privacy_guard.py",
        ROOT / "medical_reasoner.py",
        ROOT / "trinity_api_connector.py",
        ROOT / "data_synthesizer.py",
        ROOT / "amah_unified_synergy.py",
        ROOT / "amah_gemini_audit.py",
        ROOT / "amani_nexus_layer_v3.py",
    ]
    _ast_check(targets)
    _functional_check()
    print("QA_DETERMINISTIC_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
