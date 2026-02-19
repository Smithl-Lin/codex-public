# AMANI — The Alpha Nexus for MedGemma

> **From Generative Possibilities to Deterministic Reality**

[![MedGemma Impact Challenge](https://img.shields.io/badge/Kaggle-MedGemma%20Impact%20Challenge-blue)](https://www.kaggle.com/competitions/med-gemma-impact-challenge)
[![Patents](https://img.shields.io/badge/Patents-11%20Pending-green)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-red)]()

## What is AMANI?

AMANI (**A**lpha **M**edical **A**sset **N**exus **I**ntelligence) is a 5-layer sovereign AI system that transforms MedGemma's medical generative capabilities into **deterministic global medical resource routing**. 

Instead of telling patients "there might be a treatment," AMANI connects them directly to the specific FDA clinical trial, the specific Principal Investigator, and the specific medical facility — anywhere in the world.

### The Problem

- A lung cancer patient in China needs gene therapy → The best trial is at MD Anderson, Texas
- An elderly patient in Saudi Arabia wants stem cell treatment → The best program is at Keio University, Tokyo  
- A Parkinson's patient in Thailand needs BCI → The clinical trial is at UCSF, San Francisco

**These connections exist. But patients can't find them.** Global medical resources are fragmented across 200K+ institutions, clinical trial registries, and PI networks. Information asymmetry costs lives.

### The Solution: 5-Layer Sovereign Architecture

```
L1: Sentinel Layer    — Entropy-based Intent Gate (D ≤ 0.79)
L2: Orchestrator      — MedGemma 1.5 4B + Trinity-Audit (GPT×MedGemma×Claude)
L2.5: Value Layer     — Total Disease Lifecycle Strategy + Shadow Quote
L3: Nexus Layer       — Global AGID Routing + HIPAA/GDPR/PIPL Compliance
L4: Interface Layer   — Gradio Demo (multilingual: EN/ZH/AR/TH)
```

### MedGemma Integration (4 Levels Deep)

1. **Multilingual Clinical Document Understanding** — Parse Chinese/Arabic/Thai clinical notes
2. **Medical Imaging Analysis** — MRI/CT interpretation via MedGemma 1.5 multimodal
3. **Clinical Trial Eligibility Matching** — Semantic alignment of patient profiles with trial criteria
4. **Trinity-Audit Medical Consensus** — MedGemma as the medical authority in the 3-model consensus engine

## Quick Start

### Prerequisites
- Python 3.8+
- (Optional) NVIDIA GPU with CUDA for real MedGemma inference
- (Optional) OpenAI & Anthropic API keys for Trinity-Audit real mode

### Installation

#### Option 1: Mock Mode (Demo/Evaluation — Recommended)
```bash
# Clone
git clone https://github.com/[your-repo]/amani-medgemma.git
cd amani-medgemma

# Install minimal dependencies
pip install gradio

# Run CLI demo (UTF-8 encoding on Windows)
python -X utf8 app.py --mode cli --case a   # Chinese lung cancer → US gene therapy
python -X utf8 app.py --mode cli --case b   # Saudi anti-aging → Japan stem cell
python -X utf8 app.py --mode cli --case c   # Thai Parkinson's → US BCI trial

# Run Gradio UI
python -X utf8 app.py --mode gradio
# Open browser: http://127.0.0.1:7861
```

#### Option 2: Real MedGemma Mode (GPU required)
```bash
# Install full dependencies
pip install -r requirements.txt

# Enable real MedGemma inference
export AMANI_MOCK_MODE=false  # Linux/Mac
# or on Windows: set AMANI_MOCK_MODE=false

python -X utf8 app.py --mode gradio
```

#### Option 3: Trinity-Audit Real API Mode (Production)
```bash
# Install API dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.trinity.example .env
# Edit .env and fill in:
#   OPENAI_API_KEY=sk-proj-...
#   ANTHROPIC_API_KEY=sk-ant-...
#   AMANI_TRINITY_REAL_API=true

# Run with real API calls
python -X utf8 app.py --mode gradio
```

**Cost Estimate** (Real API Mode):
- GPT-4o: ~$0.003/call
- Claude 3.5 Sonnet: ~$0.0045/call
- MedGemma: FREE (local)
- **Total**: ~$0.0075 per Trinity consensus (~0.75 cents)

## Demo Cases

| Case | Patient | Route | AGID Output | Cost | Timeline |
|------|---------|-------|-------------|------|----------|
| A | 52M Chinese, NSCLC IIIB, EGFR L858R+ | Shanghai → Houston | AGID-NCT-06234517 (MD Anderson CAR-T Trial) | $190,500 | 340 days |
| B | 68M Saudi, Post-CABG, Knee OA | Riyadh → Tokyo | AGID-JP-KEIO-REGEN-002 (Keio MSC Program) | ~$170K | ~270 days |
| C | 61M Thai, PD H&Y4, Post-DBS | Bangkok → San Francisco | AGID-NCT-06578901 (UCSF BCI Trial) | ~$311K | ~365 days |

**All cases validated end-to-end with complete 5-layer pipeline execution.**

## Project Structure

```
amani-medgemma/
├── app.py                          # Main application (CLI + Gradio UI)
├── requirements.txt                # Python dependencies
├── .env.trinity.example            # API configuration template
│
├── l1_sentinel/                    # Layer 1: Entropy-based Intent Gate
│   └── entropy_scanner.py          # D-value calculation (Patent 2)
│
├── l2_orchestrator/                # Layer 2: MedGemma + Trinity-Audit
│   ├── medgemma_engine.py          # MedGemma 1.5 4B integration
│   ├── trinity_audit.py            # Trinity consensus (Patents 5/6/7)
│   ├── trial_matcher.py            # Clinical trial semantic matching
│   └── asset_registry.py           # AGID asset database (200K+ nodes)
│
├── l2_5_value/                     # Layer 2.5: TDLS + Shadow Quote
│   └── tdls_engine.py              # Total Disease Lifecycle Strategy (Patent 4)
│
├── l3_nexus/                       # Layer 3: Global Routing + Compliance
│   ├── global_router.py            # AGID-based routing (Patent 11 GNN)
│   └── compliance_engine.py        # HIPAA/GDPR/PIPL framework mapping
│
├── tests/                          # Test suite
│   ├── test_gradio_ui.py           # UI build validation
│   ├── test_3_scenarios.py         # End-to-end 3-case validation
│   └── inspect_output.py           # JSON output inspection
│
└── screenshots/                    # Demo screenshots (12 PNGs)
    ├── case_a_tab1_analysis.png
    ├── case_a_tab2_routing.png
    └── ...
```

## Testing

### Automated Tests
```bash
# Test Gradio UI build
python -X utf8 test_gradio_ui.py

# Test all 3 scenarios end-to-end
python -X utf8 test_3_scenarios.py

# Expected output:
# ✅ PASS — Case A: Chinese Lung Cancer → US Gene Therapy
# ✅ PASS — Case B: Saudi Anti-Aging → Japan Stem Cell
# ✅ PASS — Case C: Thai Parkinson's → US BCI Trial
# 3/3 tests passed
```

### Manual Testing (Gradio UI)
```bash
# Start Gradio UI
python -X utf8 app.py --mode gradio

# Browser: http://127.0.0.1:7861
# 1. Select "Case A: Chinese Lung Cancer → US Gene Therapy"
# 2. Click "Load Demo Case"
# 3. Click "Run AMANI Pipeline"
# 4. Explore 4 tabs: Analysis, Routing, Full Report, About
```

## Technical Highlights

### Trinity-Audit Consensus Engine
- **3-Model Architecture**: GPT-4o (Logic) + MedGemma (Medical) + Claude (Safety)
- **V-variance Formula**: Decision variance ≤ 0.005 threshold (Patent 6)
- **Task-adaptive Weights**: Medical tasks favor MedGemma (0.5), Safety tasks favor Claude (0.5)
- **Automated HITL Escalation**: V > 0.005 triggers human-in-the-loop review

### Data Sovereignty Protocol
- **No PHI Transmission**: Only AGID tokens cross borders
- **Compliance Mapping**: Auto-detect source jurisdiction → map to destination framework
- **Example**: PIPL (China) + Cybersecurity Law → HIPAA (US)
- **Legal Requirements**: Auto-generated checklist (FDA IND, visa, consent, etc.)

### Shadow Quote Algorithm (Patent 4)
- **6-Stage TDLS**: Translation → Verification → Travel → Treatment → Monitoring → Recovery
- **Cost Components**: Medical ($135K-$250K) + Travel + Platform fee (14% precision tax)
- **Precision Multiplier**: 1.75x for D ≤ 0.20 (high-confidence gate)

## Intellectual Property

11 patent applications covering the complete pipeline:
- **Patent 1**: Progressive Clinical Strategy Staging (Staircase Mapping)
- **Patent 2**: Ontological Distance Formula (D ≤ 0.79 Gate)
- **Patents 5/6/7**: Trinity-Audit Multi-Model Consensus
- **Patent 11**: E-CNN Entropy Texture + GNN Asset Anchoring

## Author

**Smith Lin, MD, PhD**  
Research Fellow, Department of Neurologic Surgery  
Mayo Clinic Florida  
2,000+ DBS patients managed | AI/ML in Parkinson's Disease

## Disclaimer

AMANI provides Resource Routing Pathways, not medical advice. All outputs are for institutional decision support only. Mayo Strategic Reference / Non-Diagnostic Asset Routing.
