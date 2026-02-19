# AMANI × MedGemma — Multilingual AI Medical Resource Routing

## TL;DR

I built a 5-layer AI pipeline that takes a clinical note in Chinese, Arabic, or Thai and routes the patient to the right clinical trial, institution, and care pathway — with match scores, full cost modeling, and compliance annotation. The medical AI core is **Google MedGemma 1.5 4B**.

---

## The Problem I'm Solving

Complex international patients — advanced cancer after third-line failure, late-stage neurological disease, rare conditions — systematically fail to reach trials that could help them. Not because the trials don't exist, but because the matching infrastructure doesn't.

A physician in Bangkok writing a note in Thai cannot efficiently cross-reference 400+ active Phase I/II trials at UCSF. A patient in Riyadh seeking regenerative medicine in Japan faces language barriers, compliance unknowns, and cost opacity simultaneously.

AMANI is the routing layer that closes this gap.

---

## Architecture: 5 Layers, 1 Pipeline

### L1 — Sentinel Gate
Every clinical note is scored with a D-value (precision index, 0–1). D ≤ 0.79 = high-precision routing. D > 0.79 = flag for human review. This prevents low-quality inputs from generating confident but wrong routing decisions.

### L2 — MedGemma Orchestrator
This is where **MedGemma 1.5 4B** (`google/medgemma-1.5-4b-it`) runs. Given a clinical note in any language, it outputs:
- Primary diagnosis + staging
- Molecular markers (EGFR, PD-L1, UPDRS, etc.)
- Prior treatment history
- Urgency level: `critical` / `high` / `standard` / `elective`
- Optimized search query for trial matching

No translation service. No preprocessing. MedGemma handles ZH/AR/TH natively.

Also in L2: **Trinity-Audit** — a 3-model consensus mechanism. MedGemma (medical), GPT-4o (logical), Claude (safety) independently evaluate the same case and propose an AGID routing target. V-variance ≤ 0.005 → CONSENSUS. AGID-NONE → SOFT_CONFLICT → escalate to HITL.

### L2.5 — Value Orchestrator (TDLS)
Once the AGID is resolved, the system generates a **Total Disease Lifecycle Strategy**: a 6-stage treatment pathway from intake to remote follow-up, with per-stage cost modeling and compliance annotations.

Urgency affects the timeline: `critical` → ×0.6 compression, `elective` → ×1.3 extension.

The **Shadow Quote Engine** attaches a platform fee (8% of pathway value, precision-premium adjusted) to each routed case.

### L3 — Nexus Router
Global institution routing, visa requirements, travel coordination, and destination selection based on AGID resolution.

### Output
```json
{
  "top_trial": "NCT-06234517",
  "top_trial_score": 0.96,
  "asset_resolved": true,
  "total_cost_usd": 190500,
  "urgency": "high",
  "destination": "United States"
}
```

---

## Three Real Clinical Cases

**Case A — Chinese NSCLC patient (Mandarin input)**
```
患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。三线治疗后进展。
```
MedGemma extracts: NSCLC Stage IIIB, EGFR L858R+, 3rd-line failure, urgency=high.
Routes to: NCT-06234517 (MD Anderson CAR-T trial), match score **0.96**.
6-stage TDLS: $190,500 over 340 days.

**Case B — Saudi regenerative medicine patient (English)**
```
68-year-old Saudi male, post-CABG 2019, bilateral knee OA Grade III. Seeking stem cell program Japan.
```
MedGemma extracts: stable CAD, bilateral knee OA Grade III, urgency=elective.
Routes to: Keio University Hospital Tokyo (AGID-JP-KEIO-REGEN-002), match score **0.80**.
6-stage TDLS: $170,000 over 310 days (elective ×1.3 applied).

**Case C — Thai Parkinson's patient (Thai input)**
```
ผู้ป่วยชายไทย อายุ 61 ปี โรคพาร์กินสัน H&Y Stage 4 ได้รับการผ่าตัด DBS ปี 2022
```
MedGemma extracts: PD H&Y Stage 4, post-DBS 2022 declining, BCI intent, urgency=high.
Routes to: NCT-06578901 (UCSF BCI trial), match score **0.60**.
6-stage TDLS: $311,000 over 456 days.

Each case gets a **different** score, a **different** AGID, a **different** institution. This is not a template system.

---

## What Makes This Different from a Chatbot

| Chatbot | AMANI |
|---------|-------|
| Answers questions | Routes patients |
| No audit trail | D-value gate + Trinity consensus + AGID provenance |
| No cost modeling | Full TDLS: per-stage cost + platform fee |
| English only | ZH / AR / TH / EN natively |
| No compliance | HIPAA/GDPR/PDPA sovereign routing via AGID tokens |
| Crashes on noise | Graceful SOFT_CONFLICT + HITL escalation |

---

## Pre-Submission Audit (3 Rounds, Multi-Role)

Before submitting, I ran a 3-round multi-role code audit (`audit_rounds.py`):

**Round 1 — Builder Agent:** Executed all 3 cases end-to-end. Checked 11 structural fields per case (33 total). All pass.

**Round 2 — Observer Agent:** Verified score differentiation (0.96 / 0.80 / 0.60 — all distinct), urgency timeline adjustment (Case B: 239 → 310 days), noise input handling (REVIEW → SOFT_CONFLICT → no crash).

**Round 3 — Verifier Agent:** Model ID correct (`google/medgemma-1.5-4b-it`), mode='auto' used, no hardcoded keys, Gradio builds, all imports clean.

Result: **✅ ALL AUDITS PASSED — SUBMISSION READY**

---

## Running It

```bash
# Mock mode (no GPU needed)
pip install -r requirements.txt
python -X utf8 app.py --mode cli --case a

# All 3 cases
python -X utf8 app.py --mode cli --case a
python -X utf8 app.py --mode cli --case b
python -X utf8 app.py --mode cli --case c

# Gradio UI
python app.py --mode gradio

# Audit
python -X utf8 audit_rounds.py
```

Set `AMANI_MOCK_MODE=false` + HuggingFace token for real MedGemma inference.

---

## Tech Stack

- **Google MedGemma 1.5 4B** — `google/medgemma-1.5-4b-it` via HuggingFace transformers
- **Gradio 4.x** — 4-tab interactive UI
- **Python 3.11** — Pure stdlib + transformers + torch
- **No external APIs required in mock mode**

---

## What I Learned

MedGemma's medical domain pretraining makes it surprisingly effective at extracting structured clinical information from free-text notes — especially in non-English languages. The model's keyword sensitivity to Thai neurological terms (พาร์กินสัน, DBS) and Arabic medical terminology was better than I expected from a 4B parameter model.

The hardest part was not the ML — it was designing a routing system that degrades gracefully. Real clinical systems can't crash. AGID-NONE must route somewhere sensible. D > 0.79 must warn without stopping. Trinity SOFT_CONFLICT must escalate without erroring. That edge-case architecture took more design work than the model integration.

---

**Model:** `google/medgemma-1.5-4b-it`
**Audit date:** 2026-02-18
**Verdict:** ✅ Submission ready
