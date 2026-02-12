# AUDIT_PLAN (law1)

## 0. Task Meta
- Date: 2026-02-12
- Owner (Team Lead): Codex
- Scope: Repository-level baseline audit bootstrap (workflow enablement + operational blockers)
- Target branch: current working branch

## 1. Objectives
- Primary objective: Execute first `law1` cycle and produce actionable task queue.
- Non-goals: Core logic refactor in hard-gate files.

## 2. Scan Plan (Phase 1)
- Modules/files to scan: `20260128/*.py`, top-level governance docs.
- Static checks to run: file inventory, secret pattern scan, dangerous call scan, compile sanity check.
- Expected output file: `AUDIT_FINDINGS.md`

## 3. Task Breakdown (Micro-tasks)
| task_id | risk_level | file_group | issue_type | owner | status |
|---|---|---|---|---|---|
| T-001 | high | validation pipeline | py_compile permission blockers | Code Fixer | pending |
| T-002 | medium | repository hygiene | anomalous file naming/path artifacts | Code Fixer | pending |
| T-003 | medium | qa workflow | standard regression command missing | QA Engineer | pending |

## 4. Execution Plan (Phase 2)
- Fix strategy by task: T-001 isolate write-free syntax checks; T-002 normalize/retire stray files; T-003 define deterministic test command.
- QA test plan by task: run smoke syntax + selected tests + full regression command.
- Failure loop rule: test fail => return to fixer.

## 5. Compliance Gate (Phase 3)
- Reviewer: Compliance Critic
- Checklist:
  - naming conventions
  - security checks
  - backward compatibility
  - comment/doc adequacy

## 6. Finalization Plan (Phase 4)
- Global validations to run: selected test files + syntax sanity command + import smoke.
- Merge/PR checklist: findings resolved, QA pass, compliance approved.

## 7. Human-in-the-loop Gate
- Does this cycle touch core-logic hard-gate files?
  - [x] No
  - [ ] Yes -> pause and request user approval before any core logic patch

## 8. Evidence Links
- Findings: `AUDIT_FINDINGS.md`
- QA report: `QA_REPORT.md`
- Compliance review: `COMPLIANCE_REVIEW.md`
- Final summary: `FINAL_AUDIT_SUMMARY.md`

---

## 9. Cycle 2026-02-12 (P0 Security/Compliance Hotfix)
- Date: 2026-02-12
- Owner (Team Lead): Codex
- Scope: P0 fixes from latest empirical audit report

### Phase 1: Scanning -> task mapping
- P0-PHI-001: Add outbound PHI/PII redaction utility and integrate external-call paths.
- P0-CFG-001: Fix config/key mismatch in Gemini demo audit script.
- P0-COMP-001: Regional compliance policy config (HIPAA/PIPL) and enforcement wiring.
- P0-OBS-001: Replace critical silent `except/pass` with observable logs/errors.

### Phase 2: Execution
- Completed (partial):
  - `privacy_guard.py` created.
  - redaction integrated in `trinity_api_connector.py`, `data_synthesizer.py`.
  - redaction integration started in `medical_reasoner.py` (hard-gate file).
- Pending:
  - finalize redaction integration in remaining outbound paths.
  - compliance policy wiring and config compatibility fix.

### Phase 3: Review Gate
- Compliance Critic checklist:
  - no raw PHI in outbound payload paths
  - hard-gate modifications approved by user
  - no silent fail on critical path

### Phase 4: Finalization
- run targeted smoke checks
- complete required artifacts
- produce final summary + worklogs

### Human-in-the-loop Gate (hard)
- Core-logic file touched in this cycle: `20260128/medical_reasoner.py`
- Action: pause and require explicit user approval before further core-logic edits.
