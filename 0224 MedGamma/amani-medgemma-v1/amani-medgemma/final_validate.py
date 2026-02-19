import sys, os
sys.path.insert(0, r"C:\2025-12-01 Mayo-working\2026-01-22 Business projects\AMANI Project\0224 MedGamma\amani-medgemma-v1\amani-medgemma")
os.chdir(sys.path[0])

from app import run_full_pipeline

cases = [
    ("case_a", "患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。三线治疗后进展。寻求基因治疗或CAR-T临床试验。"),
    ("case_b", "68-year-old Saudi male, post-CABG 2019, stable CAD, bilateral knee OA Grade III. MoCA 26/30. Seeking stem cell regenerative program Japan."),
    ("case_c", "ผู้ป่วยชายไทย อายุ 61 ปี โรคพาร์กินสัน H&Y Stage 4 ได้รับการผ่าตัด DBS ปี 2022 ต้องการเข้าถึง BCI clinical trial ในสหรัฐอเมริกา"),
]

print("=== FINAL SUBMISSION VALIDATION ===")
all_ok = True
for key, note in cases:
    d = run_full_pipeline(note, key)
    s = d.get("summary", {})
    L = d["layers"]
    ok = (
        d.get("errors", []) == [] and
        s.get("top_trial") not in (None, "None", "") and
        s.get("asset_resolved") is True and
        L.get("L2_Trinity", {}).get("status") == "CONSENSUS"
    )
    all_ok = all_ok and ok
    cost = L.get("L2_5_Value", {}).get("total_cost_usd", 0)
    print(f"  {key}: {'PASS' if ok else 'FAIL'} | trial={s.get('top_trial')} score={s.get('top_trial_score')} cost=${cost:,.0f}")

print(f"All cases: {'PASS' if all_ok else 'FAIL'}")
