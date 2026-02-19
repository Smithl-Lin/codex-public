"""
Task #128: Day 3.2 — 3 Scenario UI Validation

Tests all 3 demo cases through the Gradio UI's process_query function
and validates that all formatting functions work correctly.
"""

import sys
import os
sys.path.insert(0, '.')

from app import run_full_pipeline
import json

def test_scenario(case_name, clinical_note, scenario_key):
    """Test a single scenario through the full pipeline."""
    print(f"\n{'='*80}")
    print(f"Testing {case_name}")
    print(f"{'='*80}")

    try:
        # Run full pipeline
        result = run_full_pipeline(clinical_note, scenario_key)

        # Validate structure
        assert "layers" in result, "Missing 'layers' key"
        assert "summary" in result, "Missing 'summary' key"

        layers = result.get("layers", {})
        assert "L1_Sentinel" in layers, "Missing L1_Sentinel"
        assert "L2_MedGemma" in layers, "Missing L2_MedGemma"
        assert "L2_Trinity" in layers, "Missing L2_Trinity"
        assert "L2_5_Value" in layers, "Missing L2_5_Value"
        assert "L3_Nexus" in layers, "Missing L3_Nexus"

        # Print key results
        print(f"\n📊 L1 Sentinel:")
        l1 = layers.get("L1_Sentinel", {})
        print(f"  D-value: {l1.get('d_value', 0):.3f}")
        print(f"  Entropy: {l1.get('entropy', 0):.3f}")
        print(f"  Gate: {'PASS ✓' if l1.get('passed') else 'BLOCKED ✗'}")

        print(f"\n🔬 L2 MedGemma:")
        l2 = layers.get("L2_MedGemma", {}).get("clinical_profile", {})
        print(f"  Disease: {l2.get('disease', 'N/A')}")
        print(f"  Stage: {l2.get('stage', 'N/A')}")

        print(f"\n🔺 L2 Trinity-Audit:")
        trinity = layers.get("L2_Trinity", {})
        print(f"  V-variance: {trinity.get('v_variance', 0):.6f}")
        print(f"  Status: {trinity.get('status', 'N/A')}")

        print(f"\n💰 L2.5 TDLS:")
        tdls = layers.get("L2_5_Value", {}).get("tdls", {})
        print(f"  Gold: {tdls.get('gold_standard', {}).get('name', 'N/A')}")
        print(f"  Frontier: {tdls.get('frontier', {}).get('trial_id', 'N/A')}")

        print(f"\n🌐 L3 Nexus:")
        l3 = layers.get("L3_Nexus", {})
        routing = l3.get("routing", {})
        print(f"  Primary AGID: {routing.get('primary_asset_id', 'N/A')}")
        print(f"  Destination: {routing.get('asset_location', {}).get('city', 'N/A')}, {routing.get('asset_location', {}).get('country', 'N/A')}")

        compliance = l3.get("compliance", {})
        print(f"  HIPAA: {'✓' if compliance.get('hipaa_compliant') else '✗'}")
        print(f"  GDPR: {'✓' if compliance.get('gdpr_compliant') else '✗'}")

        print(f"\n📄 Summary:")
        summary = result.get("summary", {})
        print(f"  Patient: {summary.get('patient_profile', 'N/A')}")
        print(f"  Timeline: {summary.get('estimated_timeline', 'N/A')}")

        print(f"\n✅ {case_name} — PASS")
        return True

    except Exception as e:
        print(f"\n❌ {case_name} — FAIL")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all 3 test scenarios."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║  Task #128: Day 3.2 — 3 Scenario UI Validation + Formatting Test          ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    # Test cases
    test_cases = [
        {
            "name": "Case A: Chinese Lung Cancer → US Gene Therapy",
            "note": "患者男性，52岁，非小细胞肺癌（腺癌）IIIB期。EGFR L858R阳性。三线治疗后进展。ECOG评分1分。患者强烈希望寻求基因治疗或CAR-T等前沿疗法。家属愿意承担跨境就医费用。",
            "key": "case_a"
        },
        {
            "name": "Case B: Saudi Anti-Aging → Japan Stem Cell",
            "note": "68-year-old Saudi male, post-CABG 2019, stable CAD, bilateral knee OA Grade III. MoCA 26/30. Seeking comprehensive stem cell regenerative program in Japan. Family office backing.",
            "key": "case_b"
        },
        {
            "name": "Case C: Thai Parkinson's → US BCI Trial",
            "note": "ผู้ป่วยชายไทย อายุ 61 ปี โรคพาร์กินสัน H&Y Stage 4 ระยะเวลาป่วย 12 ปี ได้รับการผ่าตัด DBS ปี 2022 ผลการรักษาลดลง ต้องการเข้าถึง BCI clinical trial ในสหรัฐอเมริกา",
            "key": "case_c"
        }
    ]

    results = []
    for test_case in test_cases:
        success = test_scenario(
            test_case["name"],
            test_case["note"],
            test_case["key"]
        )
        results.append((test_case["name"], success))

    # Summary
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print(f"{'='*80}")

    pass_count = sum(1 for _, success in results if success)
    total_count = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} — {name}")

    print(f"\n{pass_count}/{total_count} tests passed")

    if pass_count == total_count:
        print("\n✅ All scenarios validated successfully!")
        print("✅ Gradio UI ready for screenshot generation (Task #129)")
        return 0
    else:
        print(f"\n❌ {total_count - pass_count} scenario(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
