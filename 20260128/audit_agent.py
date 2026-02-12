import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logger = logging.getLogger(__name__)


def _safe_redact(value):
    try:
        from privacy_guard import redact_text

        redacted, stats = redact_text(str(value))
        return redacted, stats
    except Exception:
        return value, {"email": 0, "phone": 0, "ssn": 0, "cn_id": 0}


def run_graph_audit(patient_info, trial_data):
    """
    Mayo expert dual-track audit engine.
    """
    target_api_key = os.getenv("OPENAI_API_KEY")
    if not target_api_key:
        return "Audit engine offline: OPENAI_API_KEY not configured."

    client = OpenAI(api_key=target_api_key)

    safe_patient_info, stats_a = _safe_redact(patient_info)
    safe_trial_data, stats_b = _safe_redact(trial_data)
    merged_stats = {
        "email": stats_a.get("email", 0) + stats_b.get("email", 0),
        "phone": stats_a.get("phone", 0) + stats_b.get("phone", 0),
        "ssn": stats_a.get("ssn", 0) + stats_b.get("ssn", 0),
        "cn_id": stats_a.get("cn_id", 0) + stats_b.get("cn_id", 0),
    }
    if any(merged_stats.values()):
        logger.info("Outbound payload redacted for audit_agent: %s", merged_stats)

    is_mayo = "Mayo Clinic" in str(safe_trial_data)
    mayo_bonus = (
        "Mayo internal green channel enabled: detected Mayo Clinic official project."
        if is_mayo
        else ""
    )

    system_prompt = f"""
You are a top medical and longevity management expert at Mayo Clinic.
You are auditing global medical asset scheduling for high-net-worth clients.

Responsibilities:
1) For clinical research, verify BCI/iPS technical alignment and block degraded matching.
2) For premium checkups, evaluate US resource asymmetry (e.g., liquid biopsy, AI MRI).
{mayo_bonus}
"""

    user_prompt = f"""
Client/Patient Profile: {safe_patient_info}
Matched Global Medical Assets: {safe_trial_data}

Output format:
1) Resource Alignment Verification
- Technical/project type
- Core alignment precision under D<=0.79

2) Strategic Risk and Value Assessment
- Risk intercept points
- US resource value-add analysis

3) Final Scheduling Recommendation
- Conclusion: Strongly Recommend / Consider with Caution / Reject
- Expert pathway recommendation
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Audit error: {str(e)}"
