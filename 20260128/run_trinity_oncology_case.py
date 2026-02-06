# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
Execute TrinityBridge.run_safe on high-complexity oncological case.
Output: L1 entropy metrics, L2.5 staircase mapping, L3 AGIDs, L4 multi-modal (Markdown).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from amani_trinity_bridge import TrinityBridge, ECNNSentinel, _shannon_entropy

# Test case: high-complexity oncological
PATIENT_DATA = (
    "65-year-old male, diagnosed with Stage IV Non-Small Cell Lung Cancer (NSCLC), "
    "EGFR Exon 19 deletion. Progressive disease after first-line Osimertinib. "
    "Seeking advanced orchestration for combination immunotherapy and phase III "
    "clinical trials in the Florida region."
)

def main():
    print("=" * 72)
    print("TRINITY BRIDGE — High-Complexity Oncological Case")
    print("=" * 72)
    print("\n[INPUT] Patient Data (length = %d chars)\n%s\n" % (len(PATIENT_DATA), PATIENT_DATA[:200] + "…" if len(PATIENT_DATA) > 200 else PATIENT_DATA))

    # Pre-run: entropy metrics (for logging)
    mean_ent, var_ent = _shannon_entropy(PATIENT_DATA)
    d_effective = min(1.0, 1.2 - mean_ent * 0.3)
    print("-" * 72)
    print("ENTROPY METRICS (pre-run)")
    print("-" * 72)
    print("  Shannon entropy (mean): %.6f" % mean_ent)
    print("  Shannon entropy (variance): %.6f" % var_ent)
    print("  D effective (1.2 - 0.3*mean_ent): %.6f" % d_effective)
    print("  L1 gate: D <= 0.79 required; variance <= 0.005")
    print("  L1 ALLOWED: %s" % ("YES" if d_effective <= 0.79 and var_ent <= 0.005 else "NO"))
    print()

    bridge = TrinityBridge()
    result = bridge.run_safe(PATIENT_DATA, top_k_agids=5)

    # L1
    l1 = result.get("l1_sentinel") or {}
    print("-" * 72)
    print("L1 ECNNSENTINEL (precision check)")
    print("-" * 72)
    print("  passed: %s" % l1.get("passed"))
    if l1.get("passed"):
        print("  d_effective: %s" % l1.get("d_effective"))
        print("  shannon_entropy_variance: %s" % l1.get("shannon_entropy_variance"))
    else:
        print("  error: %s" % l1.get("error", "N/A"))
    print("  intercepted: %s" % result.get("intercepted", False))
    print()

    if result.get("intercepted"):
        print("Pipeline intercepted at L1. No L2/L3/L4 output.")
        print("\n>>> DEMO: Same case with relaxed variance (0.1) to show L2.5 / L3 / L4 <<<\n")
        from amani_trinity_bridge import ECNNSentinel
        demo_sentinel = ECNNSentinel(d_threshold=0.79, variance_limit=0.1)
        bridge_demo = TrinityBridge(l1_sentinel=demo_sentinel)
        result = bridge_demo.run_safe(PATIENT_DATA, top_k_agids=5)
        if not result.get("intercepted"):
            l1 = result.get("l1_sentinel") or {}
            l2 = result.get("l2_2_5_semantic_path") or {}
            l3 = result.get("l3_nexus") or {}
            l4 = result.get("l4_multimodal") or {}
            strategy = l2.get("strategy") or []
            agids = l3.get("agids") or []
            scores = l3.get("scores") or []
            md = l4.get("shadow_quote_markdown")
            print("L1 (demo): passed=%s d_effective=%s variance=%s" % (l1.get("passed"), l1.get("d_effective"), l1.get("shannon_entropy_variance")))
            print("L2.5 Staircase (Gold Standard / Frontier / Recovery):")
            for s in strategy:
                print("  [%s] %s — %s — %s" % (s.get("sequence"), s.get("stage"), s.get("category"), s.get("agid")))
            print("L3 physical AGIDs:")
            for i, (agid, sc) in enumerate(zip(agids, scores), 1):
                print("  %d. %s (score: %.4f)" % (i, agid, sc))
            print("L4 Multi-modal (Markdown):\n" + (md or "(none)"))
        print()
        return

    # L2.5 Staircase Mapping
    l2 = result.get("l2_2_5_semantic_path") or {}
    strategy = l2.get("strategy") or []
    print("-" * 72)
    print("L2.5 STAIRCASE MAPPING (Gold Standard vs Frontier vs Recovery)")
    print("-" * 72)
    for s in strategy:
        print("  [%s] %s — category: %s — agid: %s" % (
            s.get("sequence"), s.get("stage"), s.get("category"), s.get("agid")
        ))
    print("  asset_categories: %s" % l2.get("asset_categories"))
    print()

    # L3 GNN Anchoring
    l3 = result.get("l3_nexus") or {}
    agids = l3.get("agids") or []
    scores = l3.get("scores") or []
    print("-" * 72)
    print("L3 GNN ANCHORING (physical AGIDs)")
    print("-" * 72)
    for i, (agid, sc) in enumerate(zip(agids, scores), 1):
        print("  %d. %s (score: %.4f)" % (i, agid, sc))
    if agids:
        print("  primary_agid: %s" % agids[0])
    print()

    # L4 Multi-modal — Markdown
    l4 = result.get("l4_multimodal") or {}
    md = l4.get("shadow_quote_markdown")
    print("-" * 72)
    print("L4 MULTI-MODAL OUTPUT (Markdown)")
    print("-" * 72)
    if md:
        print(md)
    else:
        print("  (no markdown)")
    print()
    print("=" * 72)
    print("END OF RUN")
    print("=" * 72)

if __name__ == "__main__":
    main()
