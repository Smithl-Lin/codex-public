"""
AMANI L2 Orchestrator — Clinical Trial Matcher

High-level wrapper for MedGemma-powered trial eligibility matching.
Provides batch matching, ranking, and filtering capabilities.

**Integration with MedGemma**:
Uses MedGemmaEngine.match_trial_eligibility() for core semantic matching,
then adds:
- Trial database management (cached local JSON)
- Multi-trial ranking by match score
- Inclusion/exclusion criterion analysis
- NCT.gov metadata integration

**Competition Note**:
For Kaggle demo, uses pre-cached trial data to avoid API dependency.
Production version can integrate live ClinicalTrials.gov API.
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

# Import from sibling module
from l2_orchestrator.medgemma_engine import MedGemmaEngine, ClinicalProfile, TrialMatch


# --- Demo Trial Database (cached for competition) ---
DEMO_TRIALS_DB = [
    {
        "nct_id": "NCT-06234517",
        "title": "CAR-T Cell Therapy for EGFR-Positive Advanced NSCLC",
        "phase": "Phase I/II",
        "institution": "MD Anderson Cancer Center",
        "location": "Houston, TX, USA",
        "pi": "Dr. John Heymach",
        "agid": "AGID-NCT-06234517",
        "condition": "Non-Small Cell Lung Cancer",
        "inclusion_criteria": [
            "NSCLC Stage IIIB or IV",
            "EGFR mutation positive (L858R or exon 19 deletion)",
            "Failed ≥2 prior lines of systemic therapy",
            "ECOG performance status 0-2",
            "Adequate organ function"
        ],
        "exclusion_criteria": [
            "Active brain metastases (unless treated and stable)",
            "Prior CAR-T therapy",
            "Active autoimmune disease requiring systemic immunosuppression"
        ],
        "keywords": ["EGFR", "CAR-T", "NSCLC", "gene therapy", "immunotherapy"]
    },
    {
        "nct_id": "NCT-06578901",
        "title": "Implantable BCI for Motor Restoration in Advanced Parkinson's Disease",
        "phase": "Phase I Early Feasibility",
        "institution": "University of California San Francisco (UCSF)",
        "location": "San Francisco, CA, USA",
        "pi": "Dr. Philip Starr",
        "agid": "AGID-NCT-06578901",
        "condition": "Parkinson's Disease",
        "inclusion_criteria": [
            "Idiopathic Parkinson's disease, Hoehn & Yahr Stage 3-4",
            "Disease duration ≥10 years",
            "MDS-UPDRS Part III OFF score ≥50",
            "Prior bilateral STN-DBS with documented benefit (now declining)",
            "MoCA score ≥20 (adequate cognition for BCI training)",
            "Stable medical management ≥3 months"
        ],
        "exclusion_criteria": [
            "Atypical Parkinsonism",
            "Active psychiatric illness",
            "MRI-incompatible DBS hardware",
            "Coagulopathy or anticoagulation that cannot be stopped"
        ],
        "keywords": ["BCI", "brain-computer interface", "Parkinson", "DBS", "neuromodulation", "motor restoration"]
    },
    {
        "nct_id": "JP-KEIO-REGEN-002",
        "title": "Autologous Adipose-Derived MSC for Knee Osteoarthritis",
        "phase": "Clinical Study (PMDA-approved)",
        "institution": "Keio University Hospital",
        "location": "Tokyo, Japan",
        "pi": "Dr. Hideyuki Okano",
        "agid": "AGID-JP-KEIO-REGEN-002",
        "condition": "Knee Osteoarthritis",
        "inclusion_criteria": [
            "Bilateral or unilateral knee OA, Kellgren-Lawrence Grade II-IV",
            "Age 50-80 years",
            "Failed conservative management (≥6 months PT, NSAIDs, injections)",
            "No absolute indication for total knee arthroplasty",
            "Willing to undergo liposuction for MSC harvest"
        ],
        "exclusion_criteria": [
            "Active infection",
            "Malignancy within 5 years",
            "Severe cardiovascular disease (NYHA Class III-IV)",
            "eGFR <30 mL/min (severe CKD)"
        ],
        "keywords": ["MSC", "stem cell", "regenerative medicine", "knee", "osteoarthritis", "cartilage"]
    },
    {
        "nct_id": "JP-HELENE-001",
        "title": "Comprehensive MSC-IV Rejuvenation Program",
        "phase": "Commercial Program (PMDA Class II)",
        "institution": "Helene Regenerative Medicine Clinic",
        "location": "Tokyo, Japan",
        "pi": "Dr. Hiroshi Tanaka",
        "agid": "AGID-JP-HELENE-001",
        "condition": "Age-Related Functional Decline",
        "inclusion_criteria": [
            "Age 60-85 years",
            "Seeking comprehensive regenerative therapy",
            "Stable chronic conditions (cardiovascular, metabolic)",
            "Family or self-funded (not insurance-covered)"
        ],
        "exclusion_criteria": [
            "Active malignancy",
            "Uncontrolled diabetes (HbA1c >9%)",
            "Severe renal impairment (eGFR <30)",
            "Active autoimmune disease"
        ],
        "keywords": ["anti-aging", "rejuvenation", "MSC", "PRP", "exosome", "regenerative medicine"]
    },
    {
        "nct_id": "NCT-06123456",
        "title": "AAV2-hAADC Gene Therapy for Advanced Parkinson's Disease",
        "phase": "Phase II",
        "institution": "UCSF / Neurocrine Biosciences",
        "location": "San Francisco, CA, USA",
        "pi": "Dr. Krystof Bankiewicz",
        "agid": "AGID-NCT-AADC-PD",
        "condition": "Parkinson's Disease",
        "inclusion_criteria": [
            "Idiopathic PD, Hoehn & Yahr Stage 3-5",
            "Inadequate response to DBS or not a DBS candidate",
            "MDS-UPDRS Part III OFF ≥30",
            "≥4 hours/day in OFF state despite optimal medical management",
            "Dopamine-responsive (≥30% improvement with levodopa challenge)"
        ],
        "exclusion_criteria": [
            "GBA or LRRK2 mutation (requires enhanced safety monitoring — not exclusionary but flagged)",
            "Prior gene therapy",
            "Contraindication to MRI-guided neurosurgery",
            "Anti-AAV2 antibodies >1:400 titer"
        ],
        "keywords": ["AADC", "gene therapy", "Parkinson", "AAV2", "Putamen", "dopamine"]
    }
]


@dataclass
class RankedTrialMatch:
    """Extended TrialMatch with ranking metadata."""
    trial_match: TrialMatch
    rank: int  # 1-based ranking
    tier: str  # "highly_recommended" | "recommended" | "consider" | "marginal"
    inclusion_met_count: int
    exclusion_triggered_count: int


def load_trial_database(custom_path: Optional[str] = None) -> List[Dict]:
    """Load clinical trial database.

    For competition: uses embedded DEMO_TRIALS_DB.
    For production: can load from JSON file or ClinicalTrials.gov API.
    """
    if custom_path and os.path.exists(custom_path):
        with open(custom_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEMO_TRIALS_DB


def match_patient_to_trials(
    profile: ClinicalProfile,
    engine: MedGemmaEngine,
    trial_db: Optional[List[Dict]] = None,
    top_k: int = 3,
    min_score: float = 0.5
) -> List[RankedTrialMatch]:
    """Match a patient profile against a trial database.

    Uses MedGemma for semantic matching, then ranks and filters results.

    Args:
        profile: ClinicalProfile from medgemma_engine.parse_clinical_note()
        engine: MedGemmaEngine instance (handles MedGemma inference)
        trial_db: List of trial dicts (default: DEMO_TRIALS_DB)
        top_k: Return top K matches
        min_score: Minimum match score threshold (0.0-1.0)

    Returns:
        List of RankedTrialMatch, sorted by match_score descending
    """
    if trial_db is None:
        trial_db = DEMO_TRIALS_DB

    # Step 1: Match against each trial using MedGemma
    raw_matches = []
    for trial in trial_db:
        match = engine.match_trial_eligibility(profile, trial)
        if match.match_score >= min_score:
            raw_matches.append((match, trial))

    # Step 2: Sort by match score
    raw_matches.sort(key=lambda x: x[0].match_score, reverse=True)

    # Step 3: Rank and tier classification
    ranked_matches = []
    for rank, (match, trial) in enumerate(raw_matches[:top_k], start=1):
        # Tier classification
        if match.match_score >= 0.85:
            tier = "highly_recommended"
        elif match.match_score >= 0.70:
            tier = "recommended"
        elif match.match_score >= 0.55:
            tier = "consider"
        else:
            tier = "marginal"

        ranked_match = RankedTrialMatch(
            trial_match=match,
            rank=rank,
            tier=tier,
            inclusion_met_count=len(match.matching_criteria),
            exclusion_triggered_count=len(match.excluding_criteria)
        )
        ranked_matches.append(ranked_match)

    return ranked_matches


def filter_trials_by_keywords(
    trial_db: List[Dict],
    keywords: List[str]
) -> List[Dict]:
    """Pre-filter trials by keyword matching (fast filter before semantic matching)."""
    filtered = []
    keywords_lower = [k.lower() for k in keywords]

    for trial in trial_db:
        trial_keywords = [kw.lower() for kw in trial.get("keywords", [])]
        trial_text = (trial.get("title", "") + " " + trial.get("condition", "")).lower()

        # Match if any keyword appears
        if any(kw in trial_text or kw in trial_keywords for kw in keywords_lower):
            filtered.append(trial)

    return filtered


def get_trial_by_agid(agid: str, trial_db: Optional[List[Dict]] = None) -> Optional[Dict]:
    """Resolve AGID to full trial details."""
    if trial_db is None:
        trial_db = DEMO_TRIALS_DB

    for trial in trial_db:
        if trial.get("agid") == agid:
            return trial
    return None


# --- CLI Test ---
if __name__ == "__main__":
    print("="*60)
    print("AMANI Trial Matcher — Test Suite")
    print("="*60)

    # Initialize MedGemma engine (mock mode for testing)
    engine = MedGemmaEngine(mode="mock")

    # Test Case 1: Chinese lung cancer patient
    print("\n[Test 1] NSCLC EGFR+ Patient → Trial Matching")
    note = "患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。三线治疗后进展。寻求基因治疗或CAR-T临床试验。"
    profile = engine.parse_clinical_note(note, source_language="zh")

    matches = match_patient_to_trials(profile, engine, top_k=3)
    print(f"  Found {len(matches)} matching trials:")
    for m in matches:
        print(f"    #{m.rank} [{m.tier}] {m.trial_match.title}")
        print(f"        NCT: {m.trial_match.nct_id}, Score: {m.trial_match.match_score:.2f}")
        print(f"        Institution: {m.trial_match.institution}")
        print(f"        AGID: {m.trial_match.agid}")

    # Test Case 2: Keyword filtering
    print("\n[Test 2] Keyword Filter — Parkinson's + BCI")
    filtered = filter_trials_by_keywords(DEMO_TRIALS_DB, ["Parkinson", "BCI"])
    print(f"  Filtered to {len(filtered)} trials:")
    for t in filtered:
        print(f"    - {t['title']} ({t['nct_id']})")

    # Test Case 3: AGID resolution
    print("\n[Test 3] AGID Resolution")
    agid = "AGID-NCT-06234517"
    trial = get_trial_by_agid(agid)
    if trial:
        print(f"  AGID: {agid}")
        print(f"  → Title: {trial['title']}")
        print(f"  → Institution: {trial['institution']}")
        print(f"  → PI: {trial['pi']}")
