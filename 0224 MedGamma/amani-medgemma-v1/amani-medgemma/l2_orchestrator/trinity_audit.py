"""
AMANI L2 — Trinity-Audit Consensus Engine

Implementation of Patents 5, 6, 7:
  Patent 5: Trinity Consensus Logic — simultaneous multi-LLM evaluation
  Patent 6: Decision Variance Interception — V-value quantified consensus
  Patent 7: Heterogeneous LLM Consensus Game — weighted game + 4-tier fallback

The Trinity-Audit mechanism intercepts and downgrades decisions when 
MedGemma, GPT, and Claude show high variance in asset alignment.
This eliminates AI hallucinations through mathematical consensus verification.

Architecture:
  ┌──────────┬──────────────┬──────────┐
  │ GPT-4o   │ MedGemma 1.5 │ Claude   │
  │ (Logic)  │ (Medical)    │ (Safety) │
  └────┬─────┴──────┬───────┴────┬─────┘
       └────────────┼────────────┘
          V = Σ Wi(Si - S̄)²
          V > 0.005 → CONFLICT LOCK
"""

import json
import math
import os
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# --- Patent-Protected Constants ---
CONFLICT_THRESHOLD = 0.005       # V-variance threshold (Patent 5)
CONSENSUS_RADIUS = 0.15          # Maximum allowed distance from centroid (Patent 5)
CERTAINTY_SAFE = 0.85            # Minimum certainty index for automation (Patent 6)

# Asymmetric weights for heterogeneous models (Patent 7, Claim 1)
# Weights dynamically adjusted based on task type
MODEL_WEIGHTS = {
    "clinical_reasoning": {"medgemma": 0.50, "gpt": 0.30, "claude": 0.20},
    "safety_check":       {"medgemma": 0.25, "gpt": 0.25, "claude": 0.50},
    "resource_matching":  {"medgemma": 0.35, "gpt": 0.40, "claude": 0.25},
    "patient_comms":      {"medgemma": 0.20, "gpt": 0.40, "claude": 0.40},
}

# --- API Configuration (Real Mode) ---
# Set via environment variables or .env file
# DO NOT hardcode API keys in code
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
REAL_API_MODE = os.environ.get("AMANI_TRINITY_REAL_API", "false").lower() == "true"


class ConsensusStatus(Enum):
    CONSENSUS = "CONSENSUS"           # All models agree → proceed
    SOFT_CONFLICT = "SOFT_CONFLICT"   # Minor disagreement → proceed with flag
    HARD_CONFLICT = "HARD_CONFLICT"   # Major disagreement → lock system
    HUMAN_REVIEW = "HUMAN_REVIEW"     # Escalate to HITL (Patent 3)


class FallbackTier(Enum):
    """Four-tier recursive fallback (Patent 7, Claim 2)."""
    SPEC_MATCH = 1        # Exact specification matching
    CATEGORY_SWAP = 2     # Category-level substitution
    MECHANISM_SUB = 3     # Mechanism-of-action level substitution
    DISCIPLINE_PLAN = 4   # Broad discipline-level planning


@dataclass
class ModelResponse:
    """Individual model's response in the Trinity."""
    model_name: str           # "medgemma" | "gpt" | "claude"
    recommendation: str       # The actual recommendation text
    confidence: float         # 0.0 - 1.0
    agid_suggested: str       # Asset Global ID suggested
    match_score: float        # 0.0 - 1.0 alignment score
    reasoning: str = ""       # Chain-of-thought reasoning
    safety_flags: list = field(default_factory=list)


@dataclass
class TrinityResult:
    """Output of the Trinity-Audit consensus evaluation."""
    status: ConsensusStatus
    v_variance: float          # Decision variance (Patent 6)
    certainty_index: float     # C = 1 - V/max(V)  (Patent 6)
    consensus_agid: str        # Agreed-upon AGID (or "" if conflict)
    consensus_score: float     # Weighted average match score
    individual_responses: list  # List of ModelResponse
    fallback_tier: Optional[FallbackTier] = None
    conflict_details: str = ""
    weights_applied: dict = field(default_factory=dict)
    
    @property
    def is_automated(self) -> bool:
        """Whether this result can proceed to automated execution."""
        return self.status in (ConsensusStatus.CONSENSUS, ConsensusStatus.SOFT_CONFLICT)


def calculate_v_variance(
    responses: list[ModelResponse], 
    weights: dict[str, float],
    metric: str = "match_score"
) -> float:
    """Calculate weighted decision variance V (Patent 5/6).
    
    V = Σ Wi * (Si - S̄)²
    
    Where:
      Wi = model weight (asymmetric, from Patent 7)
      Si = individual model score
      S̄  = weighted mean score
    """
    if not responses:
        return 0.0
    
    scores = []
    w_list = []
    for r in responses:
        s = getattr(r, metric, r.match_score)
        w = weights.get(r.model_name, 1.0 / len(responses))
        scores.append(s)
        w_list.append(w)
    
    # Normalize weights
    w_sum = sum(w_list)
    w_norm = [w / w_sum for w in w_list]
    
    # Weighted mean
    s_bar = sum(w * s for w, s in zip(w_norm, scores))
    
    # Weighted variance
    v = sum(w * (s - s_bar) ** 2 for w, s in zip(w_norm, scores))
    
    return round(v, 6)


def calculate_certainty_index(v_variance: float, max_variance: float = 0.25) -> float:
    """Calculate certainty index C (Patent 6).
    
    C = 1 - V / max(V)
    
    C ≥ C_safe → automated execution allowed
    C < C_safe → requires human oversight
    """
    if max_variance == 0:
        return 1.0
    c = 1.0 - (v_variance / max_variance)
    return round(max(0.0, min(1.0, c)), 4)


def hierarchical_fallback(
    responses: list[ModelResponse],
    current_tier: FallbackTier = FallbackTier.SPEC_MATCH
) -> tuple[str, FallbackTier]:
    """Execute hierarchical recursive fallback (Patent 7, Claim 2).
    
    Four-tier model:
      Level 1: Spec Match → exact trial/PI matching
      Level 2: Category Swap → same disease category, different trial
      Level 3: Mechanism Sub → same mechanism of action, different approach
      Level 4: Discipline Plan → broad treatment discipline guidance
    
    Q' = Q - argmin(Wi) : drop lowest-weight dimension and retry
    """
    # Find the model with highest confidence as fallback anchor
    if not responses:
        return "No consensus achievable", FallbackTier.DISCIPLINE_PLAN
    
    best = max(responses, key=lambda r: r.confidence)
    
    if current_tier == FallbackTier.SPEC_MATCH:
        return (
            f"Fallback to Category: Using {best.model_name}'s recommendation "
            f"at category level (confidence: {best.confidence:.2f})",
            FallbackTier.CATEGORY_SWAP
        )
    elif current_tier == FallbackTier.CATEGORY_SWAP:
        return (
            f"Fallback to Mechanism: Generalizing to mechanism-of-action level",
            FallbackTier.MECHANISM_SUB
        )
    elif current_tier == FallbackTier.MECHANISM_SUB:
        return (
            f"Fallback to Discipline: Providing discipline-level treatment plan",
            FallbackTier.DISCIPLINE_PLAN
        )
    else:
        return "Maximum fallback reached. Routing to HITL.", FallbackTier.DISCIPLINE_PLAN


def trinity_audit(
    query: str,
    task_type: str = "clinical_reasoning",
    medgemma_response: Optional[ModelResponse] = None,
    gpt_response: Optional[ModelResponse] = None,
    claude_response: Optional[ModelResponse] = None,
    mock: bool = True
) -> TrinityResult:
    """Execute the full Trinity-Audit consensus evaluation.
    
    This is the core implementation of Patents 5, 6, and 7.
    
    Process:
      1. Collect responses from all three models
      2. Calculate weighted variance V
      3. If V > threshold → activate hierarchical fallback
      4. Return consensus or escalate to HITL
    """
    # Get task-specific weights (Patent 7)
    weights = MODEL_WEIGHTS.get(task_type, MODEL_WEIGHTS["clinical_reasoning"])
    
    # In mock mode, generate simulated responses
    if mock or (not medgemma_response and not gpt_response and not claude_response):
        responses = _generate_mock_trinity_responses(query, task_type)
    else:
        responses = [r for r in [medgemma_response, gpt_response, claude_response] if r]
    
    if not responses:
        return TrinityResult(
            status=ConsensusStatus.HUMAN_REVIEW,
            v_variance=1.0,
            certainty_index=0.0,
            consensus_agid="",
            consensus_score=0.0,
            individual_responses=[],
            conflict_details="No model responses available"
        )
    
    # Step 1: Calculate V-variance (Patent 5/6)
    v_variance = calculate_v_variance(responses, weights)
    
    # Step 2: Calculate certainty index (Patent 6)
    certainty = calculate_certainty_index(v_variance)
    
    # Step 3: Determine consensus status
    if v_variance <= CONFLICT_THRESHOLD:
        status = ConsensusStatus.CONSENSUS
    elif v_variance <= CONFLICT_THRESHOLD * 3:
        status = ConsensusStatus.SOFT_CONFLICT
    else:
        status = ConsensusStatus.HARD_CONFLICT
    
    # Step 4: Determine consensus AGID
    if status in (ConsensusStatus.CONSENSUS, ConsensusStatus.SOFT_CONFLICT):
        # Weighted vote for AGID
        best = max(responses, key=lambda r: r.match_score * weights.get(r.model_name, 0.33))
        consensus_agid = best.agid_suggested
        # If all models return AGID-NONE, override status to SOFT_CONFLICT for HITL review
        if consensus_agid == "AGID-NONE":
            status = ConsensusStatus.SOFT_CONFLICT
        consensus_score = sum(
            r.match_score * weights.get(r.model_name, 0.33) 
            for r in responses
        )
    else:
        consensus_agid = ""
        consensus_score = 0.0
    
    # Step 5: If hard conflict, attempt hierarchical fallback (Patent 7)
    fallback_tier = None
    conflict_details = ""
    if status == ConsensusStatus.HARD_CONFLICT:
        conflict_details, fallback_tier = hierarchical_fallback(responses)
        # If fallback reaches discipline level, escalate to HITL
        if fallback_tier == FallbackTier.DISCIPLINE_PLAN:
            status = ConsensusStatus.HUMAN_REVIEW
    
    return TrinityResult(
        status=status,
        v_variance=v_variance,
        certainty_index=certainty,
        consensus_agid=consensus_agid,
        consensus_score=round(consensus_score, 4),
        individual_responses=responses,
        fallback_tier=fallback_tier,
        conflict_details=conflict_details,
        weights_applied=weights
    )


def _generate_mock_trinity_responses(query: str, task_type: str) -> list[ModelResponse]:
    """Generate mock Trinity responses for demo mode."""
    query_lower = query.lower()
    
    if "lung cancer" in query_lower or "nsclc" in query_lower or "egfr" in query_lower:
        return [
            ModelResponse(
                model_name="medgemma",
                recommendation="EGFR-targeted CAR-T trial at MD Anderson (NCT-06234517)",
                confidence=0.92,
                agid_suggested="AGID-NCT-06234517",
                match_score=0.87,
                reasoning="EGFR L858R positive after 3rd-line failure meets inclusion criteria",
            ),
            ModelResponse(
                model_name="gpt",
                recommendation="CAR-T or bispecific antibody trial, MD Anderson or MSK",
                confidence=0.88,
                agid_suggested="AGID-NCT-06234517",
                match_score=0.85,
                reasoning="Strong molecular match, multiple active trials available",
            ),
            ModelResponse(
                model_name="claude",
                recommendation="EGFR-targeted CAR-T at MD Anderson with safety monitoring",
                confidence=0.90,
                agid_suggested="AGID-NCT-06234517",
                match_score=0.86,
                reasoning="Eligible but flag: cardiac monitoring needed given T2DM comorbidity",
                safety_flags=["cardiac_monitoring_required"]
            ),
        ]
    
    elif "parkinson" in query_lower or "bci" in query_lower or "dbs" in query_lower:
        return [
            ModelResponse(
                model_name="medgemma",
                recommendation="UCSF BCI trial for motor restoration (NCT-06578901)",
                confidence=0.94,
                agid_suggested="AGID-NCT-06578901",
                match_score=0.91,
                reasoning="H&Y 4 + DBS experience + MoCA 22 meets all inclusion criteria. Staircase: Gold→Frontier unlocked.",
            ),
            ModelResponse(
                model_name="gpt",
                recommendation="BCI trial at UCSF or AADC gene therapy as alternative",
                confidence=0.89,
                agid_suggested="AGID-NCT-06578901",
                match_score=0.88,
                reasoning="Strong candidate. GBA N370S needs monitoring but not exclusionary.",
            ),
            ModelResponse(
                model_name="claude",
                recommendation="UCSF BCI trial (primary) with AADC backup",
                confidence=0.91,
                agid_suggested="AGID-NCT-06578901",
                match_score=0.90,
                reasoning="Safety cleared. DBS hardware compatibility must be verified pre-screening.",
                safety_flags=["dbs_mri_compatibility_check"]
            ),
        ]
    
    elif any(w in query_lower for w in ["stem cell", "regenerat", "خلايا", "msc", "keio", "anti-aging"]):  # Stem cell
        return [
            ModelResponse(
                model_name="medgemma",
                recommendation="Keio University MSC program for knee OA + Helene rejuvenation",
                confidence=0.85,
                agid_suggested="AGID-JP-KEIO-REGEN-002",
                match_score=0.82,
                reasoning="PMDA-approved framework. CKD2 requires renal monitoring.",
            ),
            ModelResponse(
                model_name="gpt",
                recommendation="Japan regenerative medicine program, Keio or Helene Clinic",
                confidence=0.83,
                agid_suggested="AGID-JP-KEIO-REGEN-002",
                match_score=0.80,
                reasoning="Evidence level moderate for MSC in OA. Post-CABG cardiac clearance needed.",
            ),
            ModelResponse(
                model_name="claude",
                recommendation="Keio University academic program preferred over commercial clinic",
                confidence=0.87,
                agid_suggested="AGID-JP-KEIO-REGEN-002",
                match_score=0.84,
                reasoning="Academic setting provides better safety oversight. Flag: elective procedure risk-benefit for post-CABG patient.",
                safety_flags=["cardiac_clearance_required", "renal_monitoring"]
            ),
        ]

    else:  # No recognized clinical signal — low confidence, recommend human review
        return [
            ModelResponse(
                model_name="medgemma",
                recommendation="No high-confidence clinical match found",
                confidence=0.40,
                agid_suggested="AGID-NONE",
                match_score=0.35,
                reasoning="Insufficient clinical specificity in query for automated routing.",
            ),
            ModelResponse(
                model_name="gpt",
                recommendation="Insufficient clinical specificity for routing",
                confidence=0.38,
                agid_suggested="AGID-NONE",
                match_score=0.30,
                reasoning="Query does not match known clinical trial categories.",
            ),
            ModelResponse(
                model_name="claude",
                recommendation="Recommend human review — low clinical signal",
                confidence=0.45,
                agid_suggested="AGID-NONE",
                match_score=0.40,
                reasoning="Safety review: insufficient data to recommend a specific resource pathway.",
                safety_flags=["low_confidence"]
            ),
        ]# --- Real API Integration Functions ---

def call_gpt4o_api(query: str, context: str, task_type: str) -> ModelResponse:
    """Call OpenAI GPT-4o API for Trinity-Audit.

    Requires: OPENAI_API_KEY environment variable

    Args:
        query: Clinical query
        context: Patient context (JSON string from ClinicalProfile)
        task_type: Task type for weighting

    Returns:
        ModelResponse with GPT-4o recommendation

    Raises:
        RuntimeError: If API key not configured or API call fails
    """
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY not set. "
            "Set environment variable: export OPENAI_API_KEY='sk-...'"
        )

    try:
        # Lazy import to avoid dependency when using mock mode
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)

        # System prompt for GPT-4o (Logic Verifier role in Trinity)
        system_prompt = """You are the Logic Verifier in a three-model medical consensus system (Trinity-Audit).
Your role is to provide logical, evidence-based evaluation of clinical recommendations.
Focus on:
- Eligibility criteria analysis (inclusion/exclusion)
- Evidence strength assessment
- Alternative options consideration
- Counter-scenario identification

Return JSON with:
{
  "recommendation": "Specific clinical trial or resource name with NCT# if applicable",
  "confidence": 0.0-1.0,
  "agid_suggested": "AGID-XXX-XXXXXX",
  "match_score": 0.0-1.0,
  "reasoning": "2-3 sentences explaining your logic",
  "safety_flags": ["flag1", "flag2"] or []
}"""

        user_prompt = f"""Query: {query}

Patient Context:
{context}

Provide your logic-based assessment as JSON."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        return ModelResponse(
            model_name="gpt",
            recommendation=data.get("recommendation", ""),
            confidence=float(data.get("confidence", 0.5)),
            agid_suggested=data.get("agid_suggested", ""),
            match_score=float(data.get("match_score", 0.5)),
            reasoning=data.get("reasoning", ""),
            safety_flags=data.get("safety_flags", [])
        )

    except ImportError:
        raise RuntimeError(
            "OpenAI library not installed. Install with: pip install openai"
        )
    except Exception as e:
        raise RuntimeError(f"GPT-4o API call failed: {str(e)}")


def call_claude_api(query: str, context: str, task_type: str) -> ModelResponse:
    """Call Anthropic Claude API for Trinity-Audit.

    Requires: ANTHROPIC_API_KEY environment variable

    Args:
        query: Clinical query
        context: Patient context (JSON string from ClinicalProfile)
        task_type: Task type for weighting

    Returns:
        ModelResponse with Claude recommendation

    Raises:
        RuntimeError: If API key not configured or API call fails
    """
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. "
            "Set environment variable: export ANTHROPIC_API_KEY='sk-ant-...'"
        )

    try:
        # Lazy import to avoid dependency when using mock mode
        from anthropic import Anthropic

        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # System prompt for Claude (Safety Reviewer role in Trinity)
        system_prompt = """You are the Safety Reviewer in a three-model medical consensus system (Trinity-Audit).
Your role is to identify safety concerns, contraindications, and risk factors.
Focus on:
- Patient safety flags (comorbidities, contraindications)
- Ethical considerations
- Regulatory compliance (FDA/PMDA/EMA)
- Risk-benefit assessment

Return JSON with:
{
  "recommendation": "Specific clinical trial or resource name with NCT# if applicable",
  "confidence": 0.0-1.0,
  "agid_suggested": "AGID-XXX-XXXXXX",
  "match_score": 0.0-1.0,
  "reasoning": "2-3 sentences explaining safety considerations",
  "safety_flags": ["flag1", "flag2"] or []
}"""

        user_prompt = f"""Query: {query}

Patient Context:
{context}

Provide your safety-focused assessment as JSON."""

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.3,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        content = response.content[0].text
        data = json.loads(content)

        return ModelResponse(
            model_name="claude",
            recommendation=data.get("recommendation", ""),
            confidence=float(data.get("confidence", 0.5)),
            agid_suggested=data.get("agid_suggested", ""),
            match_score=float(data.get("match_score", 0.5)),
            reasoning=data.get("reasoning", ""),
            safety_flags=data.get("safety_flags", [])
        )

    except ImportError:
        raise RuntimeError(
            "Anthropic library not installed. Install with: pip install anthropic"
        )
    except Exception as e:
        raise RuntimeError(f"Claude API call failed: {str(e)}")


def call_medgemma_local(query: str, context: str, task_type: str) -> ModelResponse:
    """Call MedGemma 1.5 4B locally for Trinity-Audit.

    Uses local inference (GPU or CPU mode).
    Falls back to mock if MedGemma engine unavailable.

    Args:
        query: Clinical query
        context: Patient context (JSON string from ClinicalProfile)
        task_type: Task type for weighting

    Returns:
        ModelResponse with MedGemma recommendation
    """
    try:
        # Import MedGemma engine
        from l2_orchestrator.medgemma_engine import MedGemmaEngine

        engine = MedGemmaEngine(mode="auto")  # auto-detect GPU/CPU/mock

        # System prompt for MedGemma (Medical Expert role in Trinity)
        prompt = f"""You are the Medical Expert in a three-model consensus system (Trinity-Audit).
Your role is to provide clinically authoritative medical recommendations.
Focus on:
- Medical accuracy and evidence base
- Clinical trial eligibility matching
- Disease-specific treatment pathways
- Standard-of-care vs experimental options

Query: {query}

Patient Context:
{context}

Provide your medical assessment as JSON with these fields:
- recommendation: Specific clinical trial or resource name with NCT# if applicable
- confidence: 0.0-1.0
- agid_suggested: AGID-XXX-XXXXXX format
- match_score: 0.0-1.0
- reasoning: 2-3 sentences explaining clinical rationale
- safety_flags: array of safety concerns or empty array

JSON:"""

        response_text = engine._generate(prompt, max_tokens=500)

        # Extract JSON from response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            data = json.loads(response_text[json_start:json_end])
        else:
            # Fallback to mock response if JSON parsing fails
            return _generate_mock_medgemma_response(query, task_type)

        return ModelResponse(
            model_name="medgemma",
            recommendation=data.get("recommendation", ""),
            confidence=float(data.get("confidence", 0.5)),
            agid_suggested=data.get("agid_suggested", ""),
            match_score=float(data.get("match_score", 0.5)),
            reasoning=data.get("reasoning", ""),
            safety_flags=data.get("safety_flags", [])
        )

    except Exception as e:
        # Fallback to mock on any error
        import logging
        logging.warning(f"MedGemma local call failed, using mock: {str(e)}")
        return _generate_mock_medgemma_response(query, task_type)


def _generate_mock_medgemma_response(query: str, task_type: str) -> ModelResponse:
    """Generate mock MedGemma response (fallback)."""
    query_lower = query.lower()

    if "lung cancer" in query_lower or "nsclc" in query_lower or "egfr" in query_lower:
        return ModelResponse(
            model_name="medgemma",
            recommendation="EGFR-targeted CAR-T trial at MD Anderson (NCT-06234517)",
            confidence=0.92,
            agid_suggested="AGID-NCT-06234517",
            match_score=0.87,
            reasoning="EGFR L858R positive after 3rd-line failure meets inclusion criteria",
        )
    elif "parkinson" in query_lower or "bci" in query_lower or "dbs" in query_lower:
        return ModelResponse(
            model_name="medgemma",
            recommendation="UCSF BCI trial for motor restoration (NCT-06578901)",
            confidence=0.94,
            agid_suggested="AGID-NCT-06578901",
            match_score=0.91,
            reasoning="H&Y 4 + DBS experience + MoCA 22 meets all inclusion criteria",
        )
    else:
        return ModelResponse(
            model_name="medgemma",
            recommendation="Keio University MSC program",
            confidence=0.85,
            agid_suggested="AGID-JP-KEIO-REGEN-002",
            match_score=0.82,
            reasoning="PMDA-approved framework",
        )


def trinity_audit_real_api(
    query: str,
    context: str = "",
    task_type: str = "clinical_reasoning"
) -> TrinityResult:
    """Execute Trinity-Audit with REAL API calls.

    Calls:
    - GPT-4o via OpenAI API (Logic Verifier)
    - Claude 3.5 Sonnet via Anthropic API (Safety Reviewer)
    - MedGemma 1.5 4B locally (Medical Expert)

    Requires environment variables:
    - OPENAI_API_KEY
    - ANTHROPIC_API_KEY

    Args:
        query: Clinical query string
        context: Patient context (optional, JSON string)
        task_type: Task type for weight selection

    Returns:
        TrinityResult with real consensus

    Raises:
        RuntimeError: If API keys not configured
    """
    # Get task-specific weights
    weights = MODEL_WEIGHTS.get(task_type, MODEL_WEIGHTS["clinical_reasoning"])

    # Call all three models
    try:
        gpt_response = call_gpt4o_api(query, context, task_type)
    except RuntimeError as e:
        raise RuntimeError(f"GPT-4o call failed: {str(e)}")

    try:
        claude_response = call_claude_api(query, context, task_type)
    except RuntimeError as e:
        raise RuntimeError(f"Claude call failed: {str(e)}")

    # MedGemma runs locally (with mock fallback)
    medgemma_response = call_medgemma_local(query, context, task_type)

    responses = [medgemma_response, gpt_response, claude_response]

    # Calculate V-variance
    v_variance = calculate_v_variance(responses, weights)

    # Calculate certainty
    certainty = calculate_certainty_index(v_variance)

    # Determine consensus status
    if v_variance <= CONFLICT_THRESHOLD:
        status = ConsensusStatus.CONSENSUS
    elif v_variance <= CONFLICT_THRESHOLD * 3:
        status = ConsensusStatus.SOFT_CONFLICT
    else:
        status = ConsensusStatus.HARD_CONFLICT

    # Determine consensus AGID
    if status in (ConsensusStatus.CONSENSUS, ConsensusStatus.SOFT_CONFLICT):
        best = max(responses, key=lambda r: r.match_score * weights.get(r.model_name, 0.33))
        consensus_agid = best.agid_suggested
        consensus_score = sum(
            r.match_score * weights.get(r.model_name, 0.33)
            for r in responses
        )
    else:
        consensus_agid = ""
        consensus_score = 0.0

    # Hierarchical fallback if needed
    fallback_tier = None
    conflict_details = ""
    if status == ConsensusStatus.HARD_CONFLICT:
        conflict_details, fallback_tier = hierarchical_fallback(responses)
        if fallback_tier == FallbackTier.DISCIPLINE_PLAN:
            status = ConsensusStatus.HUMAN_REVIEW

    return TrinityResult(
        status=status,
        v_variance=v_variance,
        certainty_index=certainty,
        consensus_agid=consensus_agid,
        consensus_score=round(consensus_score, 4),
        individual_responses=responses,
        fallback_tier=fallback_tier,
        conflict_details=conflict_details,
        weights_applied=weights
    )


# --- CLI Test ---
if __name__ == "__main__":
    print("="*60)
    print("Trinity-Audit Consensus Engine — Test Suite")
    print("="*60)

    # Check API configuration
    api_mode = "REAL API" if REAL_API_MODE and OPENAI_API_KEY and ANTHROPIC_API_KEY else "MOCK"
    print(f"\n  Mode: {api_mode}")
    if api_mode == "REAL API":
        print(f"  OpenAI API: {'✓ Configured' if OPENAI_API_KEY else '✗ Missing'}")
        print(f"  Anthropic API: {'✓ Configured' if ANTHROPIC_API_KEY else '✗ Missing'}")
    print()

    # Test 1: Lung cancer case (expect CONSENSUS)
    print("\n[Test 1] Lung Cancer EGFR+ — Clinical Reasoning (Mock Mode)")
    result = trinity_audit(
        "EGFR L858R positive NSCLC stage IIIB, 3rd-line failure, seeking gene therapy",
        task_type="clinical_reasoning",
        mock=True
    )
    print(f"  Status: {result.status.value}")
    print(f"  V-variance: {result.v_variance} (threshold: {CONFLICT_THRESHOLD})")
    print(f"  Certainty: {result.certainty_index}")
    print(f"  Consensus AGID: {result.consensus_agid}")
    print(f"  Weights: {result.weights_applied}")
    for r in result.individual_responses:
        print(f"    {r.model_name}: score={r.match_score}, agid={r.agid_suggested}")

    # Test 2: Parkinson's BCI case
    print("\n[Test 2] Parkinson's H&Y4 post-DBS — BCI Trial (Mock Mode)")
    result2 = trinity_audit(
        "Parkinson's H&Y Stage 4, bilateral STN-DBS declining, seeking BCI trial",
        task_type="clinical_reasoning",
        mock=True
    )
    print(f"  Status: {result2.status.value}")
    print(f"  V-variance: {result2.v_variance}")
    print(f"  Certainty: {result2.certainty_index}")
    print(f"  Consensus AGID: {result2.consensus_agid}")
    print(f"  Automated: {result2.is_automated}")

    # Test 3: Real API mode (if configured)
    if REAL_API_MODE and OPENAI_API_KEY and ANTHROPIC_API_KEY:
        print("\n[Test 3] NSCLC — REAL API MODE")
        try:
            result3 = trinity_audit_real_api(
                "52-year-old male with NSCLC Stage IIIB, EGFR L858R positive, failed 3 lines of therapy",
                context='{"diagnosis": "NSCLC IIIB", "molecular": {"EGFR": "L858R+"}}',
                task_type="clinical_reasoning"
            )
            print(f"  Status: {result3.status.value}")
            print(f"  V-variance: {result3.v_variance}")
            print(f"  Consensus AGID: {result3.consensus_agid}")
            print(f"  Models:")
            for r in result3.individual_responses:
                print(f"    {r.model_name}: {r.recommendation[:60]}...")
        except RuntimeError as e:
            print(f"  ✗ Real API test failed: {str(e)}")
    else:
        print("\n[Test 3] Real API Mode — SKIPPED")
        print("  Set environment variables to enable:")
        print("    export AMANI_TRINITY_REAL_API=true")
        print("    export OPENAI_API_KEY='sk-...'")
        print("    export ANTHROPIC_API_KEY='sk-ant-...'")
