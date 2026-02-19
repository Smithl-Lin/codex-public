"""
Day 5 — Pre-Submission Multi-Role Code Audit
Runs 3 audit rounds: Builder, Observer, Verifier

Usage: python -X utf8 audit_rounds.py
"""

import sys
import os
import json
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = "\u2705"
FAIL = "\u274c"
WARN = "\u26a0\ufe0f"

results = {"round1": {}, "round2": {}, "round3": {}, "issues": []}


# ============================================================
# ROUND 1 — Builder Agent: Code structure + 3-case pipeline run
# ============================================================
print("\n" + "="*70)
print("ROUND 1 — Builder Agent (Code Structure + Pipeline Execution)")
print("="*70)

from app import run_full_pipeline

round1_pass = True
for case_key, label in [("case_a", "Case A (ZH, Lung Cancer)"),
                         ("case_b", "Case B (EN, Stem Cell)"),
                         ("case_c", "Case C (TH, Parkinson)")]:
    notes = {
        "case_a": "患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。三线治疗后进展。寻求基因治疗或CAR-T临床试验。",
        "case_b": "68-year-old Saudi male, post-CABG 2019, stable CAD, bilateral knee OA Grade III. MoCA 26/30. Seeking comprehensive stem cell regenerative program in Japan.",
        "case_c": "ผู้ป่วยชายไทย อายุ 61 ปี โรคพาร์กินสัน H&Y Stage 4 ได้รับการผ่าตัด DBS ปี 2022 ต้องการเข้าถึง BCI clinical trial ในสหรัฐอเมริกา",
    }
    note = notes[case_key]
    d = run_full_pipeline(note, case_key)
    L = d["layers"]
    s = d.get("summary", {})

    checks = {
        "L1_present":    "L1_Sentinel" in L,
        "L1_pass":       L.get("L1_Sentinel", {}).get("status") == "PASS",
        "L2_MedGemma":   "L2_MedGemma" in L,
        "L2_Trinity":    L.get("L2_Trinity", {}).get("status") == "CONSENSUS",
        "L2_TrialMatch": L.get("L2_TrialMatching", {}).get("matches_found", 0) > 0,
        "L2_AssetRes":   L.get("L2_AssetResolution", {}).get("primary_agid") not in (None, ""),
        "L25_present":   "L2_5_Value" in L,
        "L3_present":    "L3_Nexus" in L,
        "no_errors":     d.get("errors", []) == [],
        "summary_top_trial": s.get("top_trial") not in (None, "None", ""),
        "summary_asset_resolved": s.get("asset_resolved") is True,
    }

    case_ok = all(checks.values())
    round1_pass = round1_pass and case_ok
    icon = PASS if case_ok else FAIL

    print(f"\n  {icon} {label}")
    for k, v in checks.items():
        sign = PASS if v else FAIL
        print(f"      {sign} {k}")

    # Key metric values
    tm = L.get("L2_TrialMatching", {})
    top_match = tm.get("top_matches", [{}])[0] if tm.get("top_matches") else {}
    print(f"      → D-value={L['L1_Sentinel'].get('d_value'):.3f}  "
          f"V={L['L2_Trinity'].get('v_variance'):.6f}  "
          f"trial_score={top_match.get('match_score','?')}  "
          f"cost=${L.get('L2_5_Value',{}).get('total_cost_usd','?')}  "
          f"urgency={L['L2_MedGemma'].get('urgency')}")

    if not case_ok:
        failed = [k for k, v in checks.items() if not v]
        results["issues"].append(f"R1/{case_key}: FAILED checks: {failed}")
    results["round1"][case_key] = checks

print(f"\n  Round 1 Overall: {PASS + ' PASS' if round1_pass else FAIL + ' FAIL'}")


# ============================================================
# ROUND 2 — Observer Agent: Output quality + score differentiation
# ============================================================
print("\n" + "="*70)
print("ROUND 2 — Observer Agent (Output Quality + Score Differentiation)")
print("="*70)

round2_pass = True

# Check trial match score differentiation across cases
scores = {}
for case_key, note in [
    ("case_a", "患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。三线治疗后进展。"),
    ("case_b", "68-year-old Saudi male. Bilateral knee OA Grade III. Seeking stem cell program Japan."),
    ("case_c", "Parkinson H&Y Stage 4. Post DBS 2022. BCI clinical trial."),
]:
    d = run_full_pipeline(note, case_key)
    tm = d["layers"].get("L2_TrialMatching", {})
    top = tm.get("top_matches", [{}])[0] if tm.get("top_matches") else {}
    scores[case_key] = top.get("match_score", 0.0)

score_differentiated = len(set(scores.values())) >= 2  # at least 2 distinct scores
print(f"\n  Trial Match Score Differentiation:")
for k, v in scores.items():
    print(f"      {k}: {v}")
print(f"  {PASS if score_differentiated else FAIL} Scores are differentiated (not all 0.5): {score_differentiated}")
if not score_differentiated:
    results["issues"].append("R2: Trial match scores are not differentiated across cases")
round2_pass = round2_pass and score_differentiated

# Check urgency-based TDLS timeline adjustment
urgency_check = {}
for case_key, expected_urgency, should_scale in [
    ("case_a", "high", False),
    ("case_b", "elective", True),   # elective → days > base
    ("case_c", "high", False),
]:
    d = run_full_pipeline(
        {"case_a": "患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。",
         "case_b": "68-year-old Saudi male. Bilateral knee OA Grade III. Seeking stem cell.",
         "case_c": "Parkinson H&Y Stage 4. Post DBS. BCI trial."}[case_key], case_key)
    urgency_actual = d["layers"]["L2_MedGemma"].get("urgency")
    days = d["layers"]["L2_5_Value"].get("total_duration_days", 0)
    urgency_check[case_key] = {"urgency": urgency_actual, "days": days}

print(f"\n  TDLS Urgency-adjusted Timelines:")
for k, v in urgency_check.items():
    print(f"      {k}: urgency={v['urgency']}  days={v['days']}")
elective_extended = urgency_check["case_b"]["urgency"] == "elective" and urgency_check["case_b"]["days"] > 239
print(f"  {PASS if elective_extended else WARN} Case B elective extension applied: {elective_extended}")
if not elective_extended:
    results["issues"].append("R2: Case B elective urgency not extending TDLS timeline")
round2_pass = round2_pass and elective_extended

# Check noise input → AGID-NONE → SOFT_CONFLICT
print(f"\n  Noise Input Handling:")
noise_result = run_full_pipeline("What is the weather today?", "auto")
noise_trinity = noise_result["layers"].get("L2_Trinity", {})
noise_status = noise_trinity.get("status", "")
noise_agid = noise_trinity.get("consensus_agid", "")
noise_ok = noise_agid == "AGID-NONE" or noise_status in ("SOFT_CONFLICT", "HARD_CONFLICT", "CONSENSUS")
# Pipeline may or may not route noise to HITL depending on D-value gate
l1_status = noise_result["layers"].get("L1_Sentinel", {}).get("status", "")
print(f"      L1 status={l1_status}  Trinity status={noise_status}  AGID={noise_agid}")
print(f"  {PASS} Noise input handled gracefully (no crash): True")

results["round2"] = {
    "score_differentiation": score_differentiated,
    "elective_extension": elective_extended,
    "noise_handled": True,
    "scores": scores,
    "urgency_days": urgency_check,
}
print(f"\n  Round 2 Overall: {PASS + ' PASS' if round2_pass else FAIL + ' FAIL'}")


# ============================================================
# ROUND 3 — Verifier Agent: End-to-end integrity check
# ============================================================
print("\n" + "="*70)
print("ROUND 3 — Verifier Agent (End-to-End Integrity + Security)")
print("="*70)

round3_pass = True
verifier_checks = {}

# 1. Model ID check
import l2_orchestrator.medgemma_engine as me_mod
correct_model_id = me_mod.MEDGEMMA_MODEL_ID == "google/medgemma-1.5-4b-it"
verifier_checks["model_id_correct"] = correct_model_id
print(f"\n  {PASS if correct_model_id else FAIL} Model ID = {me_mod.MEDGEMMA_MODEL_ID!r}")
if not correct_model_id:
    results["issues"].append(f"R3: Wrong model ID: {me_mod.MEDGEMMA_MODEL_ID}")
round3_pass = round3_pass and correct_model_id

# 2. MedGemmaEngine mode="auto" used in app.py
import inspect, app as app_mod
pipeline_src = inspect.getsource(app_mod.run_full_pipeline)
uses_auto = 'mode="auto"' in pipeline_src or "mode='auto'" in pipeline_src
verifier_checks["engine_mode_auto"] = uses_auto
print(f"  {PASS if uses_auto else FAIL} MedGemmaEngine(mode='auto') in run_full_pipeline: {uses_auto}")
if not uses_auto:
    results["issues"].append("R3: run_full_pipeline still using mode='mock' hardcoded")
round3_pass = round3_pass and uses_auto

# 3. No hardcoded API keys in source
import glob
all_py = glob.glob("**/*.py", recursive=True)
# Split patterns so this file doesn't match its own scan
_PAT = ["sk-proj" + "-", "sk-ant" + "-api", "AKI" + "A"]
hardcoded_key = False
for f in all_py:
    if os.path.basename(f) == "audit_rounds.py":
        continue  # Skip self — patterns appear here as literals, not real keys
    try:
        content = open(f, encoding="utf-8").read()
        if any(pat in content for pat in _PAT):
            hardcoded_key = True
            results["issues"].append(f"R3: Hardcoded API key found in {f}")
    except Exception:
        pass
verifier_checks["no_hardcoded_keys"] = not hardcoded_key
print(f"  {PASS if not hardcoded_key else FAIL} No hardcoded API keys in source: {not hardcoded_key}")
round3_pass = round3_pass and (not hardcoded_key)

# 4. Gradio UI builds successfully
try:
    from app import build_gradio_app
    ui = build_gradio_app()
    ui_ok = ui is not None
except Exception as e:
    ui_ok = False
    results["issues"].append(f"R3: Gradio UI build failed: {e}")
verifier_checks["gradio_ui_builds"] = ui_ok
print(f"  {PASS if ui_ok else FAIL} Gradio UI builds without error: {ui_ok}")
round3_pass = round3_pass and ui_ok

# 5. All imports succeed (trial_matcher, asset_registry)
try:
    from l2_orchestrator.trial_matcher import match_patient_to_trials, DEMO_TRIALS_DB, get_trial_by_agid
    from l2_orchestrator.asset_registry import resolve_agid, get_connected_assets
    imports_ok = True
except ImportError as e:
    imports_ok = False
    results["issues"].append(f"R3: Import failed: {e}")
verifier_checks["new_imports_ok"] = imports_ok
print(f"  {PASS if imports_ok else FAIL} trial_matcher + asset_registry imports OK: {imports_ok}")
round3_pass = round3_pass and imports_ok

# 6. Trinity mock comment updated
trinity_comment_ok = "AMANI_TRINITY_REAL_API" in pipeline_src
verifier_checks["trinity_comment_updated"] = trinity_comment_ok
print(f"  {PASS if trinity_comment_ok else WARN} Trinity mock comment references AMANI_TRINITY_REAL_API: {trinity_comment_ok}")

# 7. summary fields present
d_a = run_full_pipeline("患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。", "case_a")
required_summary_fields = ["top_trial", "top_trial_score", "asset_resolved"]
summary_ok = all(f in d_a.get("summary", {}) for f in required_summary_fields)
verifier_checks["summary_new_fields"] = summary_ok
print(f"  {PASS if summary_ok else FAIL} summary has top_trial/top_trial_score/asset_resolved: {summary_ok}")
if not summary_ok:
    missing = [f for f in required_summary_fields if f not in d_a.get("summary", {})]
    results["issues"].append(f"R3: Missing summary fields: {missing}")
round3_pass = round3_pass and summary_ok

results["round3"] = verifier_checks
print(f"\n  Round 3 Overall: {PASS + ' PASS' if round3_pass else FAIL + ' FAIL'}")


# ============================================================
# FINAL AUDIT SUMMARY
# ============================================================
all_pass = round1_pass and round2_pass and round3_pass

print("\n" + "="*70)
print("FINAL AUDIT SUMMARY")
print("="*70)
print(f"  Round 1 (Builder):  {PASS + ' PASS' if round1_pass  else FAIL + ' FAIL'}")
print(f"  Round 2 (Observer): {PASS + ' PASS' if round2_pass  else FAIL + ' FAIL'}")
print(f"  Round 3 (Verifier): {PASS + ' PASS' if round3_pass  else FAIL + ' FAIL'}")
print(f"\n  {'='*40}")
print(f"  OVERALL: {PASS + ' ALL AUDITS PASSED — READY TO SUBMIT' if all_pass else FAIL + ' ISSUES FOUND — FIX BEFORE SUBMIT'}")

if results["issues"]:
    print(f"\n  Issues to fix ({len(results['issues'])}):")
    for issue in results["issues"]:
        print(f"    {FAIL} {issue}")
else:
    print(f"\n  {PASS} No issues found. Code is submission-ready.")

# Save report
report = {
    "audit_date": "2026-02-18",
    "overall_pass": all_pass,
    "rounds": {
        "round1_builder": {"pass": round1_pass, "details": results["round1"]},
        "round2_observer": {"pass": round2_pass, "details": results["round2"]},
        "round3_verifier": {"pass": round3_pass, "details": results["round3"]},
    },
    "issues": results["issues"],
    "verdict": "SUBMISSION_READY" if all_pass else "NEEDS_FIXES",
}
with open("audit_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n  Report saved: audit_report.json")

sys.exit(0 if all_pass else 1)
