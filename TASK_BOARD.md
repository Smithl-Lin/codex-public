# TASK_BOARD (law1)

| task_id | title | owner_role | status | dependency | acceptance |
|---|---|---|---|---|---|
| T-001 | Make validation write-free and deterministic | Code Fixer + QA Engineer | completed | none | Syntax/test checks pass without `.pyc` write dependency |
| T-002 | Normalize artifact-like file names | Code Fixer | completed | none | Stray naming artifacts removed/renamed with reference safety |
| T-003 | Clarify `merged_data.json.py` ownership | Code Fixer | completed | none | Purpose explicit and naming unambiguous |
| T-004 | Normalize special-glyph reference file naming | Code Fixer | completed | none | Cross-platform safe filename and location |
| T-005 | Define canonical regression command | QA Engineer | completed | T-001 | One repeatable QA command set documented and runnable |

## Current Phase
- Phase 1 complete
- Ready for Phase 2 execution

---

## P0 Cycle 2026-02-12
| task_id | title | owner_role | status | dependency | acceptance |
|---|---|---|---|---|---|
| P0-PHI-001 | Enforce outbound PHI/PII redaction on all external-call paths | Code Fixer + Security Auditor + QA Engineer | completed | none | No raw PHI patterns in outbound payload tests/log samples |
| P0-CFG-001 | Repair config key mismatch in Gemini audit script | Code Fixer | completed | none | Script runs without KeyError using current config |
| P0-COMP-001 | Add HIPAA/PIPL policy branches and enforce route-level compliance | Code Fixer + Compliance Critic | completed | none | Region policy test cases pass for US/CN/EU |
| P0-OBS-001 | Replace silent pass in critical paths with observable failure signals | Code Fixer + Compliance Critic | completed | none | Key path exceptions produce structured error evidence |
