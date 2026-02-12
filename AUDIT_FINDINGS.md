# AUDIT_FINDINGS (law1 cycle 2026-02-12)

## Summary
Phase 1 scanning completed for baseline governance execution.

## Findings
| task_id | file_path | risk_level | description | suggested_fix |
|---|---|---|---|---|
| T-001 | `20260128/**/__pycache__` | high | Syntax/compile sanity command fails with repeated permission errors when Python attempts to write `.pyc` files in current environment. This blocks deterministic validation. | Adopt write-free syntax check strategy (e.g., explicit no-bytecode workflow) and ensure CI/local validation does not rely on writable `__pycache__`. |
| T-002 | `20260128/nano blitz_expansion_v2.py` | medium | File name contains leading tool artifact pattern (`nano ` prefix) and whitespace, increasing risk of accidental execution/omission. | Confirm intent; rename or remove artifact file, update references if needed. |
| T-003 | `20260128/merged_data.json.py` | medium | Ambiguous file naming (`.json.py`) can confuse ownership, import, and tooling behavior. | Clarify purpose; rename to a clear script name or relocate as data asset. |
| T-004 | `20260128/Mayo Internal Ref VERIFIED` | low | Non-standard file name with special glyph/punctuation may reduce cross-platform reliability. | Normalize file naming and move to docs/reference folder if needed. |
| T-005 | repository-wide | medium | No single documented regression command found for repeatable QA handoff in this cycle. | Define one canonical QA command set and record in `QA_REPORT.md` + project docs. |

## Notes
- No direct hardcoded key patterns were matched in this quick scan set.
- No obvious `eval`/`exec`/`subprocess.run`/`os.system` usage was matched in the quick scan set.

---

## Findings (P0 cycle 2026-02-12)
| task_id | file_path | risk_level | description | suggested_fix |
|---|---|---|---|---|
| P0-PHI-001 | `20260128/medical_reasoner.py`, `20260128/trinity_api_connector.py`, `20260128/data_synthesizer.py`, `20260128/amah_unified_synergy.py` | critical | Outbound API/model payloads carry user/case raw text; PHI/PII leakage risk. | Introduce centralized redaction utility and enforce before all outbound calls. |
| P0-CFG-001 | `20260128/amah_gemini_audit.py` + `20260128/amah_config.json` | high | Script references config keys not present (`fallback_path`, `shadow_billing_unit_usd`). | Add compatibility keys or code fallback handling with explicit defaults. |
| P0-COMP-001 | `20260128/amani_nexus_layer_v3.py` | high | Compliance matrix misses explicit HIPAA/PIPL profile while docs claim region-specific governance. | Move policy matrix to config and add HIPAA/PIPL branches with enforce path. |
| P0-OBS-001 | `20260128/*.py` key paths | medium | Critical chain has silent `except/pass`, reducing incident visibility. | Replace with structured logging or controlled failure returns with error code. |

## Remediation Status
- P0-PHI-001: Completed (utility + key outbound path integration + smoke validation).
- P0-CFG-001: Completed.
- P0-COMP-001: Completed.
- P0-OBS-001: Completed for critical chain in this cycle (observable exception logging added in key paths).
