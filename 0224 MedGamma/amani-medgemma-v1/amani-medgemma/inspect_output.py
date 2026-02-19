"""Quick test to inspect full pipeline JSON output for Case A"""

import sys
sys.path.insert(0, '.')

from app import run_full_pipeline
import json

clinical_note = "患者男性，52岁，非小细胞肺癌（腺癌）IIIB期。EGFR L858R阳性。三线治疗后进展。ECOG评分1分。患者强烈希望寻求基因治疗或CAR-T等前沿疗法。家属愿意承担跨境就医费用。"

result = run_full_pipeline(clinical_note, "case_a")

print("="*80)
print("FULL JSON OUTPUT FOR CASE A")
print("="*80)
print(json.dumps(result, indent=2, ensure_ascii=False))
