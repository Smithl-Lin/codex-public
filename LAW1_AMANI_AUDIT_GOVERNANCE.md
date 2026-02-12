# law1 (AMANI Project Basic Law)

## 1. Scope
`law1` applies to all code-audit and code-change tasks in this repository.

## 2. Team-of-Five Roles
1. Team Lead
- Break down work, distribute context, merge approved changes.

2. Security Auditor
- Run static checks and structured code reading.
- Output findings with file path, severity, issue, and fix suggestion.

3. QA Engineer
- Create/maintain tests for bug reproduction and regression.
- Validate fixer outputs before review gate.

4. Code Fixer
- Implement precise changes from findings.
- Coordinate tightly with QA until tests pass.

5. Compliance Critic
- Perform second-pass review for AMANI coding standards.
- Reject non-compliant changes and return to fixer.

## 3. Four-Phase Iterative Workflow
### Phase 1: Scanning
- Lead assigns scan scope.
- Auditor produces finding list:
  - `task_id`
  - `file_path`
  - `risk_level` (`critical`/`high`/`medium`/`low`)
  - `description`
  - `suggested_fix`
- Lead converts findings into actionable micro-tasks.

Exit criteria:
- All findings mapped to task IDs.

### Phase 2: Execution
- Fixer claims task IDs and patches code.
- QA writes/runs tests in parallel.
- If tests fail: return to fixer.
- If tests pass: move to review.

Exit criteria:
- Task has code diff + test evidence.

### Phase 3: Review Gate
- Compliance Critic checks:
  - naming
  - readability
  - security hardening
  - no hidden behavior regressions
- Non-compliant tasks are rejected and loop back to fixer.

Exit criteria:
- Compliance approval recorded.

### Phase 4: Finalization
- Lead aggregates approved tasks.
- Run final project-level validation/build/tests.
- Prepare final merge/PR package.

Exit criteria:
- Global checks pass and merge package is ready.

## 4. Mandatory Operating Rules
1. Plan-first rule
- Before large or cross-file changes, create/update `AUDIT_PLAN.md`.

2. Micro-task rule
- Split by vulnerability type or file group.
- Each task should be small enough for ~5-10 minutes of focused execution.

3. Human-in-the-loop rule (hard gate)
- Before changing core logic, Team Lead must pause and ask for user approval.

## 5. Core-Logic Hard-Gate Files
Any logic change in the files below requires explicit user approval first:
- `20260128/amani_core_v4.py`
- `20260128/amani_trinity_bridge.py`
- `20260128/medical_reasoner.py`
- `20260128/amani_nexus_layer_v3.py`
- `20260128/amani_value_layer_v4.py`
- `20260128/amani_interface_layer_v4.py`

## 6. Required Artifacts Per Audit Cycle
- `AUDIT_PLAN.md`
- `AUDIT_FINDINGS.md`
- `TASK_BOARD.md`
- `QA_REPORT.md`
- `COMPLIANCE_REVIEW.md`
- optional final rollup: `FINAL_AUDIT_SUMMARY.md`

## 7. Definition of Done
A task is done only if:
1. Finding is fixed and linked to task ID.
2. Tests pass (including regression checks).
3. Compliance review is approved.
4. User approval exists for any core-logic change.
5. Final global validation passes.
6. A task-completion worklog is generated per `law2`.
