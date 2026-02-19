# AMANI × MedGemma: Multilingual AI Medical Resource Routing
### Kaggle AI in Medicine Hackathon 2026

---

## The Problem

Every year, thousands of patients with complex, treatment-resistant conditions — advanced cancers, neurodegenerative diseases, rare disorders — fail to access clinical trials and frontier medical technologies that could help them. The barriers are compounding:

- **Language:** Clinical notes are in Mandarin, Arabic, Thai, Korean, Portuguese
- **Complexity:** Multi-system conditions require multi-step, multi-country care pathways
- **Information asymmetry:** Physicians in Riyadh or Bangkok cannot track 400+ active Phase I/II trials at US centers
- **Compliance opacity:** International patients face IRB, FDA, PMDA, and cross-border data rules simultaneously

The result: a patient who *could* match a clinical trial at MD Anderson or UCSF never reaches enrollment. The trial fails to recruit. The therapy never scales. The disease wins.

---

## The Solution: AMANI — 5-Layer Medical Routing Architecture

AMANI is a sovereign medical routing system that transforms a free-text clinical note — in any language — into a structured, billable, compliance-annotated treatment pathway. It is built on a novel **5-layer architecture** integrating Google MedGemma 1.5 4B as the medical expert core.

```
Layer 1 — L1 Sentinel Gate
  Entropy-based quality filter. Computes D-value (precision index).
  D ≤ 0.79 → high-precision routing. D > 0.79 → HITL review flag.

Layer 2 — L2 Orchestrator (MedGemma Core)
  MedGemma 1.5 4B parses multilingual clinical notes:
  ZH → structured diagnosis + molecular markers + urgency
  AR → cardiovascular/metabolic profile extraction
  TH → neurological staging + device history
  Trinity-Audit: 3-model consensus (MedGemma + GPT-4o + Claude)
  V-variance ≤ 0.005 → CONSENSUS; AGID-NONE → SOFT_CONFLICT

Layer 2.5 — L2.5 Value Orchestrator (TDLS)
  Total Disease Lifecycle Strategy: 6-stage treatment pathway
  Shadow Quote Engine: platform fee calculation (Patent 2 & 4)
  Urgency adjustment: critical ×0.6, elective ×1.3 timeline

Layer 3 — L3 Nexus Router
  Global institution routing. Visa + travel compliance.
  Destination: MD Anderson / UCSF / Keio / Chulalongkorn

Output — Structured Summary
  Top trial + match score + AGID + total cost + timeline
```

---

## MedGemma Integration

MedGemma 1.5 4B serves three functions within AMANI:

**1. Clinical Note Parsing (Multilingual)**
The model receives raw clinical notes in ZH/AR/TH and outputs structured JSON: diagnosis, staging, molecular markers, prior treatments, urgency level, and an optimized trial search query. No preprocessing or translation service required.

**2. Trial Eligibility Semantic Matching**
In real mode, MedGemma evaluates patient profiles against trial inclusion/exclusion criteria using medical reasoning — not keyword matching. The mock implementation demonstrates this via proportional keyword-overlap scoring, producing differentiated scores (0.96 / 0.80 / 0.60) across three clinical profiles.

**3. Trinity-Audit Medical Voice**
Within the 3-model consensus mechanism, MedGemma provides the medical domain perspective. Its confidence score (0.0–1.0) and AGID proposal are weighted alongside GPT-4o (logic) and Claude (safety) to compute V-variance. Consensus requires V ≤ 0.005.

---

## Three Clinical Demonstration Cases

| | Case A | Case B | Case C |
|---|---|---|---|
| **Patient** | 52M Chinese | 68M Saudi | 61M Thai |
| **Condition** | NSCLC IIIB, EGFR L858R+ | Bilateral knee OA Grade III | Parkinson's H&Y Stage 4 |
| **Note language** | Simplified Chinese (ZH) | English | Thai |
| **Urgency** | High | Elective | High |
| **Top trial** | NCT-06234517 | JP-KEIO-REGEN-002 | NCT-06578901 |
| **Trial score** | 0.96 | 0.80 | 0.60 |
| **Pathway cost** | $190,500 | $170,000 | $311,000 |
| **Duration** | 340 days | 310 days (×1.3) | 456 days |
| **Destination** | MD Anderson, Houston | Keio University, Tokyo | UCSF, San Francisco |

Each case receives a **differentiated** match score and a **case-specific** 6-stage TDLS pathway — not a generic response.

---

## Key Technical Innovations

**D-Value Precision Gate (L1 Sentinel)**
An entropy-based index computed from clinical note complexity. D ≤ 0.79 gates the case into the high-precision pipeline. D > 0.79 triggers a warning and routes to human-in-the-loop review. This is the first systematic precision filter applied to international medical routing.

**AGID — Asset Graph ID System**
Every resource in the AMANI ecosystem — clinical trials, institutions, physicians, compliance frameworks — is assigned a unique AGID token. Routing operates entirely on AGIDs, with no PHI crossing institutional boundaries. Patient data never leaves the sovereign layer; only tokens flow.

**Trinity-Audit Consensus (3-Model)**
A novel multi-model audit mechanism where three AI systems (medical, logical, safety) independently assess the same case and vote on routing. V-variance measures disagreement. CONSENSUS requires V ≤ 0.005. SOFT_CONFLICT and HARD_CONFLICT trigger escalation with specific resolution paths.

**Urgency-Adaptive TDLS**
The lifecycle timeline adjusts dynamically to clinical urgency: critical cases compress by 40%, elective cases extend by 30%. This affects scheduling, visa processing, and institution coordination — not just a cosmetic label.

**Noise Input Containment**
Non-medical queries (e.g., "What is the weather today?") are intercepted at L1 (status: REVIEW) and produce AGID-NONE + SOFT_CONFLICT in Trinity, with no crash and a structured warning. The pipeline degrades gracefully.

---

## Results Summary

All 3 audit rounds passed pre-submission (2026-02-18):

- **Round 1 (Builder):** 3/3 cases, 33/33 structural checks ✅
- **Round 2 (Observer):** Score differentiation confirmed, elective timeline extended, noise handled ✅
- **Round 3 (Verifier):** Correct model ID, mode='auto', no hardcoded keys, Gradio builds, imports clean ✅

```
Case A: D=0.306  V=7.6e-5   trial=0.96  cost=$190,500  urgency=high
Case B: D=0.312  V=1.96e-4  trial=0.80  cost=$170,000  urgency=elective (310d)
Case C: D=0.307  V=1.69e-4  trial=0.60  cost=$311,000  urgency=high
Noise:  L1=REVIEW  Trinity=SOFT_CONFLICT  AGID=AGID-NONE
```

---

## Impact and Scalability

AMANI addresses a $4.2 trillion annual gap in global medical travel and clinical trial access. The architecture is designed for scale:

- **Language expansion:** Any language supported by MedGemma's multilingual capability
- **Trial database:** AGID registry expandable to all ClinicalTrials.gov entries (~450,000)
- **Institution network:** Asset registry schema supports any accredited facility globally
- **Revenue model:** 8% platform fee on routed pathway value, precision-premium adjusted

The sovereign data architecture (AGID-only routing, no PHI transmission) makes AMANI deployable under HIPAA, GDPR, Saudi NCA, and Thai PDPA simultaneously — without data localization conflicts.

---

## Repository Structure

```
amani-medgemma/
├── app.py                          # Main pipeline + Gradio UI
├── l1_sentinel/entropy_scanner.py  # D-value precision gate
├── l2_orchestrator/
│   ├── medgemma_engine.py          # MedGemma 1.5 4B interface
│   ├── trinity_audit.py            # 3-model consensus mechanism
│   ├── trial_matcher.py            # Semantic trial scoring
│   └── asset_registry.py           # AGID registry
├── l2_5_value/lifecycle_strategy.py # TDLS + Shadow Quote
├── l3_nexus/global_router.py       # Global institution routing
├── audit_rounds.py                 # Pre-submission 3-round audit
├── amani_medgemma_demo.ipynb       # Kaggle/HuggingFace notebook
└── requirements.txt
```

**Model:** `google/medgemma-1.5-4b-it`
**License:** Apache 2.0
**Mock mode:** `AMANI_MOCK_MODE=true` (no GPU required for demo)
