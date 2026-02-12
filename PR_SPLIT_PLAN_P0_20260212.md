# PR_SPLIT_PLAN_P0_20260212

## Goal
Minimize review risk by splitting P0 fixes into focused PRs.

## PR-1: PHI/PII Outbound Redaction
### Files
- `20260128/privacy_guard.py`
- `20260128/medical_reasoner.py`
- `20260128/trinity_api_connector.py`
- `20260128/data_synthesizer.py`
- `20260128/amah_unified_synergy.py`

### Commit message
- `feat(security): add outbound PHI/PII redaction guard for model/API calls`

### Suggested commands
```bash
git add 20260128/privacy_guard.py
git add 20260128/medical_reasoner.py
git add 20260128/trinity_api_connector.py
git add 20260128/data_synthesizer.py
git add 20260128/amah_unified_synergy.py
git commit -m "feat(security): add outbound PHI/PII redaction guard for model/API calls"
```

---

## PR-2: Compliance Policy Hardening (HIPAA/PIPL)
### Files
- `20260128/amani_nexus_layer_v3.py`
- `20260128/amah_config.json`

### Commit message
- `feat(compliance): add HIPAA/PIPL regional policy branches and consent strictness`

### Suggested commands
```bash
git add 20260128/amani_nexus_layer_v3.py
git add 20260128/amah_config.json
git commit -m "feat(compliance): add HIPAA/PIPL regional policy branches and consent strictness"
```

---

## PR-3: Config Compatibility Fix
### Files
- `20260128/amah_gemini_audit.py`

### Commit message
- `fix(config): make gemini audit script tolerant to missing keys`

### Suggested commands
```bash
git add 20260128/amah_gemini_audit.py
git commit -m "fix(config): make gemini audit script tolerant to missing keys"
```

---

## PR-4: Audit Artifacts (law1/law2)
### Files
- `AUDIT_PLAN.md`
- `AUDIT_FINDINGS.md`
- `TASK_BOARD.md`
- `QA_REPORT.md`
- `COMPLIANCE_REVIEW.md`
- `FINAL_AUDIT_SUMMARY.md`
- `PR_SPLIT_PLAN_P0_20260212.md`
- `20260211/WORKLOG_20260212_000001.md`
- `20260211/WORKLOG_20260212_000002.md`
- `20260211/WORKLOG_20260212_000003.md`
- `20260211/WORKLOG_20260212_000004.md`

### Commit message
- `docs(audit): update law1/law2 artifacts for P0 remediation cycle`

### Suggested commands
```bash
git add AUDIT_PLAN.md AUDIT_FINDINGS.md TASK_BOARD.md QA_REPORT.md COMPLIANCE_REVIEW.md FINAL_AUDIT_SUMMARY.md PR_SPLIT_PLAN_P0_20260212.md
git add 20260211/WORKLOG_20260212_000001.md 20260211/WORKLOG_20260212_000002.md 20260211/WORKLOG_20260212_000003.md 20260211/WORKLOG_20260212_000004.md
git commit -m "docs(audit): update law1/law2 artifacts for P0 remediation cycle"
```
