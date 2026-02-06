# TrinityBridge.run_safe — High-Complexity Oncological Case Run Log

**Date:** 2026-01-28  
**Stamp:** V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN  
**Objective:** Verify L1 ECNNSentinel, demonstrate L2.5 Staircase Mapping, confirm L3 GNN Anchoring, output L4 Markdown.

---

## Test Case (Patient Data)

```
65-year-old male, diagnosed with Stage IV Non-Small Cell Lung Cancer (NSCLC), EGFR Exon 19 deletion. Progressive disease after first-line Osimertinib. Seeking advanced orchestration for combination immunotherapy and phase III clinical trials in the Florida region.
```

**Input length:** 264 characters.

---

## 1. L1 ECNNSentinel — Precision Check

**Result:** Query **not allowed** under sovereign variance limit (0.005).

| Metric | Value |
|--------|--------|
| Shannon entropy (mean) | 2.207645 |
| Shannon entropy (variance) | 0.044392 |
| D effective (1.2 − 0.3×mean_ent) | 0.537706 |
| L1 gate: D ≤ 0.79 | ✓ (D passed) |
| L1 gate: variance ≤ 0.005 | ✗ (variance 0.044 > 0.005) |
| **L1 ALLOWED** | **NO** |
| Intercept AGID | AGID-L1-INTERCEPT-94FA5F5A183E |

**Conclusion:** L1 ECNNSentinel correctly blocks the query due to **entropy variance** exceeding the sovereign limit. D effective (0.5377) satisfies D ≤ 0.79; the failure is variance-only.

---

## 2. Entropy Metrics (Logged)

```
Shannon entropy (mean):     2.207645
Shannon entropy (variance): 0.044392
D effective:                0.537706
L1 gate: D <= 0.79 required; variance <= 0.005
L1 ALLOWED: NO
```

---

## 3. Demo Run (Relaxed Variance 0.1) — Full Pipeline

To demonstrate L2.5, L3, and L4 on the **same** patient data, a demo run used `variance_limit=0.1` (illustration only; sovereign default remains 0.005).

### L1 (demo)

- **passed:** True  
- **d_effective:** 0.537706  
- **shannon_entropy_variance:** 0.044392  

### L2.5 Staircase Mapping (Gold Standard vs Frontier vs Recovery)

| Sequence | Stage      | Category      | AGID                  |
|----------|------------|---------------|------------------------|
| 1        | Diagnosis  | Gold Standard | AGID-L2-STEP-7505B7AB3151 |
| 2        | Treatment  | Frontier      | AGID-L2-STEP-12D82778463A |
| 3        | Recovery   | Recovery      | AGID-L2-STEP-3321964F5168 |
| 4        | Follow-up  | Recovery      | AGID-L2-STEP-2BD9F6C69607 |

**Asset categories:** Gold Standard, Frontier, Recovery.

### L3 GNN Anchoring (Physical AGIDs)

| Rank | AGID | Score  |
|------|------|--------|
| 1    | AGID-L3-ASSET-DBF7B7A869D7 | 0.2180 |
| 2    | AGID-L3-ASSET-8B1C23673BE1 | 0.2138 |
| 3    | AGID-L3-ASSET-962D183D258C | 0.2083 |
| 4    | AGID-L3-ASSET-9B4EA69912AC | 0.1760 |
| 5    | AGID-L3-ASSET-D84B76C02144 | 0.1713 |

**Primary AGID (L3):** AGID-L3-ASSET-DBF7B7A869D7

---

## 4. L4 Multi-Modal Output (Markdown)

```markdown
## Shadow Quote
- **Status:** SUCCESS
- **Total:** 0.0 USD
- **Base / audit:** 0
- **Subscription:** 0
- **Value-added:** 0
- **AGID:** `AGID-L3-ASSET-DBF7B7A869D7`
```

---

## 5. Summary

| Check | Result |
|-------|--------|
| L1 ECNNSentinel allows query (sovereign 0.005) | **No** — variance 0.044 > 0.005 |
| L2.5 Staircase Mapping (Gold / Frontier / Recovery) | **Yes** — 4 stages with categories and AGIDs |
| L3 GNN Anchoring to physical AGID | **Yes** — top-5 AGIDs with scores; primary AGID confirmed |
| L4 Multi-modal (Markdown) | **Yes** — Shadow Quote rendered in Markdown |

*End of Run Log*
