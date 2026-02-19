"""
AMANI L2 Orchestrator — MedGemma 1.5 4B Engine Interface

Unified interface for MedGemma integration within the AMANI Trinity Architecture.
MedGemma serves as the medical-domain expert in the Trinity-Audit consensus
mechanism (Patent 5/6/7), alongside GPT-4o (logic) and Claude (safety).

Capabilities:
  1. Multi-language clinical note parsing (ZH/AR/TH → EN structured profile)
  2. Medical imaging analysis (MRI/CT via MedGemma 1.5 multimodal)
  3. Clinical trial eligibility semantic matching
  4. FHIR-aware health record navigation

Environment:
  - GPU mode: Full MedGemma 1.5 4B inference via HuggingFace transformers
  - CPU mode: Reduced precision (bfloat16 → float32) with slower inference
  - Mock mode: Deterministic demo outputs for presentation/testing
"""

import json
import os
import logging
from dataclasses import dataclass, field
from typing import Optional, Any

logger = logging.getLogger(__name__)

# --- Configuration ---
MEDGEMMA_MODEL_ID = "google/medgemma-1.5-4b-it"
MOCK_MODE = os.environ.get("AMANI_MOCK_MODE", "true").lower() == "true"


@dataclass
class ClinicalProfile:
    """Structured clinical profile extracted from free-text notes."""
    patient_age: int = 0
    patient_sex: str = ""
    primary_diagnosis: str = ""
    staging: str = ""
    molecular_markers: dict = field(default_factory=dict)
    prior_treatments: list = field(default_factory=list)
    current_status: str = ""
    treatment_intent: str = ""
    urgency: str = "standard"  # "critical" | "high" | "standard" | "elective"
    language_source: str = "en"
    structured_json: dict = field(default_factory=dict)
    
    def to_search_query(self) -> str:
        """Generate optimized search query for AGID matching."""
        parts = [self.primary_diagnosis, self.staging, self.treatment_intent]
        if self.molecular_markers:
            parts.extend([f"{k}: {v}" for k, v in self.molecular_markers.items() 
                         if v and "positive" in str(v).lower()])
        return " | ".join(p for p in parts if p)


@dataclass
class TrialMatch:
    """Result of clinical trial eligibility matching."""
    nct_id: str = ""
    title: str = ""
    phase: str = ""
    institution: str = ""
    pi_name: str = ""
    match_score: float = 0.0
    matching_criteria: list = field(default_factory=list)
    excluding_criteria: list = field(default_factory=list)
    agid: str = ""


class MedGemmaEngine:
    """Unified MedGemma 1.5 4B inference engine.
    
    Supports three modes:
      - "gpu": Full model loaded on CUDA
      - "cpu": Model on CPU (slow but functional)
      - "mock": Deterministic outputs for demo/testing
    """
    
    def __init__(self, mode: str = "auto"):
        if mode == "auto":
            if MOCK_MODE:
                self.mode = "mock"
            else:
                try:
                    import torch
                    self.mode = "gpu" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    self.mode = "mock"
        else:
            self.mode = mode
        
        self.model = None
        self.tokenizer = None
        self.processor = None
        
        if self.mode != "mock":
            self._load_model()
        
        logger.info(f"MedGemma Engine initialized in {self.mode} mode")
    
    def _load_model(self):
        """Load MedGemma model from HuggingFace."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            logger.info(f"Loading {MEDGEMMA_MODEL_ID}...")
            self.tokenizer = AutoTokenizer.from_pretrained(MEDGEMMA_MODEL_ID)
            
            dtype = torch.bfloat16 if self.mode == "gpu" else torch.float32
            device_map = "auto" if self.mode == "gpu" else "cpu"
            
            self.model = AutoModelForCausalLM.from_pretrained(
                MEDGEMMA_MODEL_ID,
                torch_dtype=dtype,
                device_map=device_map,
            )
            logger.info("MedGemma loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load MedGemma: {e}. Falling back to mock mode.")
            self.mode = "mock"
    
    def _generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text from MedGemma."""
        if self.mode == "mock":
            return self._mock_generate(prompt)
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if self.mode == "gpu":
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=0.3,
            do_sample=True,
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def _mock_generate(self, prompt: str) -> str:
        """Deterministic mock outputs for demo mode."""
        prompt_lower = prompt.lower()
        
        if "lung cancer" in prompt_lower or "肺癌" in prompt_lower or "nsclc" in prompt_lower:
            return json.dumps({
                "diagnosis": "Non-Small Cell Lung Cancer (NSCLC), Adenocarcinoma, Stage IIIB",
                "molecular": {"EGFR": "L858R mutation positive", "PD_L1": "60%", "TMB": "12 mut/Mb"},
                "prior_lines": 3,
                "current_status": "Third-line failure, progressive disease",
                "treatment_intent": "Gene therapy or CAR-T experimental options",
                "urgency": "high",
                "recommended_search": "EGFR+ NSCLC gene therapy CAR-T Phase I/II clinical trial"
            })
        
        elif "parkinson" in prompt_lower or "帕金森" in prompt_lower or "พาร์กินสัน" in prompt_lower or "dbs" in prompt_lower or "bci" in prompt_lower or "brain-computer" in prompt_lower or "สมอง" in prompt_lower or "กระตุ้น" in prompt_lower:
            return json.dumps({
                "diagnosis": "Parkinson's Disease, Hoehn & Yahr Stage 4",
                "disease_duration_years": 12,
                "motor": {"UPDRS_III_OFF": 62, "UPDRS_III_ON": 38, "LEDD": 1200},
                "genetic": {"GBA": "N370S heterozygous", "LRRK2": "Negative"},
                "prior_treatments": ["Levodopa (10yr)", "Bilateral STN-DBS (2022, declining)"],
                "staircase_status": "Gold Standard (DBS) completed → Frontier Tech (BCI) unlocked",
                "treatment_intent": "BCI clinical trial or AADC gene therapy",
                "urgency": "high",
                "recommended_search": "BCI implantable Parkinson Phase I OR AADC gene therapy PD"
            })
        
        elif any(w in prompt_lower for w in ["stem cell", "خلايا جذعية", "regenerat",
                                             "خلايا", "تجديد", "مكافحة الشيخوخة",
                                             "anti-aging", "knee", "ركبة", "osteoarthritis"]):
            return json.dumps({
                "primary_concern": "Age-related functional decline, regenerative medicine",
                "cardiovascular": "Stable CAD post-CABG, EF 55%",
                "metabolic": "T2DM HbA1c 7.2%",
                "musculoskeletal": "Bilateral knee OA Grade III",
                "cognitive": "MoCA 26/30, mild subjective memory complaints",
                "treatment_intent": "Comprehensive stem cell regenerative program",
                "urgency": "elective",
                "recommended_search": "MSC stem cell knee OA regenerative medicine Japan PMDA"
            })
        
        else:
            return json.dumps({
                "diagnosis": "Unspecified medical inquiry",
                "treatment_intent": "General medical resource search",
                "urgency": "standard",
                "recommended_search": prompt[:100]
            })
    
    def parse_clinical_note(self, text: str, source_language: str = "auto") -> ClinicalProfile:
        """Parse a clinical note into a structured ClinicalProfile.
        
        Uses MedGemma's text comprehension to extract:
        - Diagnosis + staging
        - Molecular markers
        - Treatment history
        - Current status + intent
        
        Supports multilingual input (ZH/AR/TH → EN).
        """
        prompt = f"""You are a medical AI assistant. Parse the following clinical note 
and extract structured information. Return ONLY valid JSON with these fields:
- diagnosis: primary diagnosis with staging
- molecular: dict of molecular markers (if any)
- prior_lines: number of prior treatment lines
- prior_treatments: list of prior treatments
- current_status: current clinical status
- treatment_intent: what the patient is seeking
- urgency: "critical" | "high" | "standard" | "elective"
- recommended_search: optimized search query for clinical trial matching

Clinical Note:
{text}

JSON output:"""
        
        response = self._generate(prompt)
        
        # Parse JSON from response
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(response[json_start:json_end])
            else:
                data = json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse MedGemma JSON output, using raw text")
            data = {"diagnosis": "Parse error", "treatment_intent": text[:200]}
        
        profile = ClinicalProfile(
            primary_diagnosis=data.get("diagnosis", ""),
            molecular_markers=data.get("molecular", {}),
            prior_treatments=data.get("prior_treatments", []),
            current_status=data.get("current_status", ""),
            treatment_intent=data.get("treatment_intent", ""),
            urgency=data.get("urgency", "standard"),
            language_source=source_language if source_language != "auto" else "en",
            structured_json=data
        )
        
        return profile
    
    def match_trial_eligibility(
        self,
        profile: ClinicalProfile,
        trial_criteria: dict
    ) -> TrialMatch:
        """Match a patient profile against a clinical trial's eligibility criteria.

        Uses MedGemma's medical reasoning to evaluate inclusion/exclusion criteria
        semantically (not just keyword matching). Mock mode uses keyword-overlap scoring.
        """
        # Mock mode: keyword-overlap scoring instead of LLM reasoning
        if self.mode == "mock":
            return self._mock_trial_match(profile, trial_criteria)

        prompt = f"""You are a clinical trial eligibility screener. Evaluate whether this
patient matches the trial criteria. Return JSON with:
- match_score: 0.0 to 1.0
- matching_criteria: list of met inclusion criteria
- excluding_criteria: list of potentially excluding criteria
- recommendation: "eligible" | "possibly_eligible" | "likely_ineligible"

Patient Profile:
{json.dumps(profile.structured_json, indent=2)}

Trial Criteria:
{json.dumps(trial_criteria, indent=2)}

JSON output:"""

        response = self._generate(prompt)

        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            data = json.loads(response[json_start:json_end])
        except (json.JSONDecodeError, ValueError):
            data = {"match_score": 0.5, "matching_criteria": [], "excluding_criteria": []}

        return TrialMatch(
            nct_id=trial_criteria.get("nct_id", ""),
            title=trial_criteria.get("title", ""),
            phase=trial_criteria.get("phase", ""),
            institution=trial_criteria.get("institution", ""),
            pi_name=trial_criteria.get("pi", ""),
            match_score=data.get("match_score", 0.5),
            matching_criteria=data.get("matching_criteria", []),
            excluding_criteria=data.get("excluding_criteria", []),
        )

    def _mock_trial_match(self, profile: ClinicalProfile, trial_criteria: dict) -> TrialMatch:
        """Keyword-overlap based trial matching for mock mode."""
        # Build patient keyword set from structured_json
        patient_text = json.dumps(profile.structured_json).lower()
        trial_text = (
            json.dumps(trial_criteria.get("inclusion_criteria", [])) + " " +
            trial_criteria.get("condition", "") + " " +
            " ".join(trial_criteria.get("keywords", []))
        ).lower()

        # Count keyword overlaps
        trial_keywords = trial_criteria.get("keywords", [])
        hits = sum(1 for kw in trial_keywords if kw.lower() in patient_text)
        total = max(len(trial_keywords), 1)
        score = round(min(hits / total * 1.2, 1.0), 2)  # Scale up slightly

        # Build matching criteria from inclusion list, proportional to score
        inclusion = trial_criteria.get("inclusion_criteria", [])
        matching = inclusion[:max(1, int(len(inclusion) * score))]

        return TrialMatch(
            nct_id=trial_criteria.get("nct_id", ""),
            title=trial_criteria.get("title", ""),
            phase=trial_criteria.get("phase", ""),
            institution=trial_criteria.get("institution", ""),
            pi_name=trial_criteria.get("pi", ""),
            match_score=score,
            matching_criteria=matching,
            excluding_criteria=[],
            agid=trial_criteria.get("agid", ""),
        )


# --- CLI Test ---
if __name__ == "__main__":
    print("Initializing MedGemma Engine (mock mode for testing)...")
    engine = MedGemmaEngine(mode="mock")
    print(f"Mode: {engine.mode}")
    
    # Test Case A: Chinese lung cancer
    print("\n" + "="*60)
    print("Test: Chinese NSCLC clinical note parsing")
    note_zh = "患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。三线治疗后进展。寻求基因治疗或CAR-T临床试验。"
    profile = engine.parse_clinical_note(note_zh, source_language="zh")
    print(f"  Diagnosis: {profile.primary_diagnosis}")
    print(f"  Molecular: {profile.molecular_markers}")
    print(f"  Intent: {profile.treatment_intent}")
    print(f"  Urgency: {profile.urgency}")
    print(f"  Search query: {profile.to_search_query()}")
    
    # Test Case C: Thai PD patient
    print("\n" + "="*60)
    print("Test: Thai Parkinson's clinical note parsing")
    note_pd = "61-year-old male with Parkinson's disease H&Y Stage 4. Post bilateral STN-DBS 2022, benefit declining. Seeking BCI clinical trial."
    profile_pd = engine.parse_clinical_note(note_pd, source_language="en")
    print(f"  Diagnosis: {profile_pd.primary_diagnosis}")
    print(f"  Intent: {profile_pd.treatment_intent}")
    print(f"  Urgency: {profile_pd.urgency}")
    print(f"  Structured: {json.dumps(profile_pd.structured_json, indent=2)}")
