"""
AMANI L2.5 — Value Orchestrator (The Business Soul)

Implementation of Patents 2 and 4:
  Patent 2: Shadow Billing — real-time commercial value attachment
  Patent 4: Lifecycle Strategy — progressive multi-stage treatment paths

The Value Layer transforms raw clinical matching into structured,
billable therapeutic pathways (TDLS: Total Disease Lifecycle Strategy).
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class LifecycleStage:
    """Single stage in a Total Disease Lifecycle Strategy."""
    stage_number: int
    title: str
    description: str
    agid: str = ""
    institution: str = ""
    estimated_duration_days: int = 0
    estimated_cost_usd: float = 0.0
    requires_travel: bool = False
    compliance_requirements: list = field(default_factory=list)


@dataclass
class TDLS:
    """Total Disease Lifecycle Strategy (Patent 4)."""
    case_id: str
    patient_summary: str
    stages: list[LifecycleStage] = field(default_factory=list)
    total_estimated_cost_usd: float = 0.0
    total_duration_days: int = 0
    shadow_quote_id: str = ""
    generated_at: str = ""
    compliance_notes: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "patient_summary": self.patient_summary,
            "stages": [
                {
                    "stage": s.stage_number,
                    "title": s.title,
                    "description": s.description,
                    "agid": s.agid,
                    "institution": s.institution,
                    "duration_days": s.estimated_duration_days,
                    "cost_usd": s.estimated_cost_usd,
                    "travel_required": s.requires_travel,
                    "compliance": s.compliance_requirements
                }
                for s in self.stages
            ],
            "total_cost_usd": self.total_estimated_cost_usd,
            "total_duration_days": self.total_duration_days,
            "shadow_quote_id": self.shadow_quote_id,
            "generated_at": self.generated_at,
            "compliance_notes": self.compliance_notes
        }


def generate_shadow_quote(d_value: float, tdls: TDLS) -> dict:
    """Shadow Quote Engine (Patent 2).
    
    Triggered when D ≤ 0.79. Attaches commercial valuation to each AGID node.
    """
    quote_id = f"SQ-{tdls.case_id}-{datetime.now().strftime('%Y%m%d%H%M')}"
    
    # Platform fee structure
    platform_fee_rate = 0.08  # 8% of total pathway value
    platform_fee = round(tdls.total_estimated_cost_usd * platform_fee_rate, 2)
    
    # Precision premium: lower D-value → higher precision → higher premium
    precision_multiplier = max(1.0, 2.0 - (d_value / 0.79))
    
    return {
        "shadow_quote_id": quote_id,
        "d_value": d_value,
        "precision_gate": "PASS" if d_value <= 0.79 else "FAIL",
        "total_pathway_value_usd": tdls.total_estimated_cost_usd,
        "platform_fee_usd": platform_fee,
        "precision_multiplier": round(precision_multiplier, 2),
        "adjusted_fee_usd": round(platform_fee * precision_multiplier, 2),
        "billing_points": len(tdls.stages),
        "per_stage_breakdown": [
            {
                "stage": s.stage_number,
                "title": s.title,
                "value_usd": s.estimated_cost_usd,
                "fee_usd": round(s.estimated_cost_usd * platform_fee_rate * precision_multiplier, 2)
            }
            for s in tdls.stages
        ]
    }


def generate_tdls(
    case_id: str,
    consensus_agid: str,
    patient_summary: str,
    scenario: str = "auto",
    urgency: str = "standard",
    diagnosis: str = ""
) -> TDLS:
    """Generate a Total Disease Lifecycle Strategy.
    
    Maps the treatment journey from intake to follow-up,
    with each stage anchored to a specific AGID.
    """
    now = datetime.now().isoformat()
    
    # Scenario-specific lifecycle generation
    if "lung_cancer" in scenario or "NCT-06234517" in consensus_agid:
        stages = [
            LifecycleStage(1, "Medical Record Translation & Preparation",
                "Translate Chinese medical records to English. Prepare oncology summary.",
                "AGID-TRANSLATE-001", "AMANI Translation Service", 5, 2500, False,
                ["HIPAA-compliant translation", "Certified medical translator"]),
            LifecycleStage(2, "Clinical Trial Eligibility Verification",
                "Remote pre-screening with MD Anderson trial coordinator.",
                "AGID-NCT-06234517", "MD Anderson Cancer Center", 14, 5000, False,
                ["IRB approval", "International patient protocol"]),
            LifecycleStage(3, "Travel & Enrollment",
                "Medical visa (B-2). Houston accommodation. Trial enrollment.",
                "AGID-TRAVEL-MDA-001", "AMANI Travel Coordination", 21, 15000, True,
                ["B-2 medical visa", "Travel insurance"]),
            LifecycleStage(4, "CAR-T / Gene Therapy Administration",
                "Treatment at MD Anderson. Inpatient monitoring 2-4 weeks.",
                "AGID-NCT-06234517", "MD Anderson Cancer Center", 30, 135000, True,
                ["FDA IND protocol", "Informed consent"]),
            LifecycleStage(5, "Post-Treatment Monitoring",
                "3-month on-site monitoring per trial protocol.",
                "AGID-MDA-FOLLOWUP-001", "MD Anderson Cancer Center", 90, 25000, True,
                ["Trial follow-up protocol"]),
            LifecycleStage(6, "Remote Follow-Up & Shanghai Rehab",
                "Telemedicine with PI. Local rehabilitation at partner clinic.",
                "AGID-REHAB-SH-001", "Shanghai Zhongshan Hospital", 180, 8000, False,
                ["Telemedicine cross-border agreement"]),
        ]
    
    elif "parkinson" in scenario or "bci" in scenario or "NCT-06578901" in consensus_agid:
        stages = [
            LifecycleStage(1, "DBS Programming Records Export",
                "Export DBS parameters from Chulalongkorn. MRI compatibility check.",
                "AGID-CHULA-NEURO-001", "Chulalongkorn University Hospital", 7, 3000, False,
                ["DBS device manufacturer clearance"]),
            LifecycleStage(2, "International Patient Application",
                "UCSF BCI trial pre-screening. Remote neurological evaluation.",
                "AGID-NCT-06578901", "UCSF Neurosurgery", 21, 8000, False,
                ["FDA IDE protocol", "International patient pathway"]),
            LifecycleStage(3, "Travel Coordination",
                "Medical visa. San Francisco accommodation 6-8 weeks.",
                "AGID-TRAVEL-UCSF-001", "AMANI Travel Coordination", 14, 20000, True,
                ["B-2 medical visa", "Caregiver accompaniment"]),
            LifecycleStage(4, "BCI Implantation Surgery",
                "Neural interface implantation at UCSF by Dr. Starr.",
                "AGID-NCT-06578901", "UCSF Medical Center", 7, 180000, True,
                ["FDA IDE", "Neurosurgery consent", "DBS interaction protocol"]),
            LifecycleStage(5, "Neurorehabilitation & Calibration",
                "4-6 week inpatient rehab. BCI device calibration.",
                "AGID-UCSF-REHAB-001", "UCSF Neurorehabilitation", 42, 85000, True,
                ["Rehab protocol", "Device calibration schedule"]),
            LifecycleStage(6, "Remote Monitoring",
                "Secure cloud portal for longitudinal BCI data. Bangkok neurology follow-up.",
                "AGID-CHULA-NEURO-001", "Chulalongkorn + UCSF Telemedicine", 365, 15000, False,
                ["Cross-border telemedicine agreement", "Data sovereignty compliance"]),
        ]
    
    elif "stem_cell" in scenario or "KEIO" in consensus_agid or "HELENE" in consensus_agid:
        stages = [
            LifecycleStage(1, "Pre-Screening & Cardiac Clearance",
                "Remote cardiac evaluation. Renal function assessment for MSC eligibility.",
                "AGID-KFSH-CARDIAC-001", "King Faisal Specialist Hospital, Riyadh", 10, 5000, False,
                ["Cardiac clearance for elective procedure"]),
            LifecycleStage(2, "Japan Medical Visa & Travel",
                "Medical visa processing. Tokyo accommodation 3 weeks.",
                "AGID-TRAVEL-JP-001", "AMANI Travel Coordination", 14, 12000, True,
                ["Japan medical visa", "Arabic interpreter arranged"]),
            LifecycleStage(3, "Keio University MSC Treatment",
                "Autologous adipose-derived MSC for bilateral knee OA.",
                "AGID-JP-KEIO-REGEN-002", "Keio University Hospital", 7, 45000, True,
                ["PMDA Regenerative Medicine Class II"]),
            LifecycleStage(4, "Helene Clinic Rejuvenation Program",
                "Comprehensive MSC-IV + PRP + Exosome program.",
                "AGID-JP-HELENE-001", "Helene Regenerative Medicine Clinic", 14, 95000, True,
                ["PMDA certification"]),
            LifecycleStage(5, "Post-Treatment Tokyo Monitoring",
                "2-week recovery monitoring in Tokyo.",
                "AGID-JP-KEIO-REGEN-002", "Keio University Hospital", 14, 8000, True, []),
            LifecycleStage(6, "Remote Follow-Up Riyadh",
                "Telemedicine with Keio. Local follow-up at KFSH.",
                "AGID-KFSH-REGEN-001", "King Faisal Specialist Hospital", 180, 5000, False,
                ["Cross-border telemedicine"]),
        ]
    
    else:
        stages = [
            LifecycleStage(1, "Initial Assessment", "Standard intake assessment.",
                consensus_agid, "AMANI Assessment", 7, 2000, False, [])
        ]
    
    total_cost = sum(s.estimated_cost_usd for s in stages)

    # Urgency-based timeline adjustment (M3)
    if urgency == "critical":
        for s in stages:
            s.estimated_duration_days = max(1, int(s.estimated_duration_days * 0.6))
    elif urgency == "elective":
        for s in stages:
            s.estimated_duration_days = int(s.estimated_duration_days * 1.3)

    total_days = sum(s.estimated_duration_days for s in stages)
    
    tdls = TDLS(
        case_id=case_id,
        patient_summary=patient_summary,
        stages=stages,
        total_estimated_cost_usd=total_cost,
        total_duration_days=total_days,
        generated_at=now,
        compliance_notes=[
            "All data processed under AMANI Sovereign Protocol",
            "No PHI transmitted across borders — AGID tokens only",
            "Resource Routing Pathway — Non-Diagnostic Asset Routing",
            "Mayo Strategic Reference / Institutional Decision Support Only"
        ]
    )
    
    return tdls


# --- CLI Test ---
if __name__ == "__main__":
    print("="*60)
    print("L2.5 Value Orchestrator — Test Suite")
    print("="*60)
    
    # Test: Lung cancer TDLS
    tdls = generate_tdls(
        "AMANI-DEMO-A",
        "AGID-NCT-06234517",
        "52M Chinese, NSCLC IIIB, EGFR L858R+, 3rd-line failure",
        scenario="lung_cancer"
    )
    print(f"\nTDLS for {tdls.case_id}:")
    print(f"  Stages: {len(tdls.stages)}")
    print(f"  Total cost: ${tdls.total_estimated_cost_usd:,.0f}")
    print(f"  Total duration: {tdls.total_duration_days} days")
    for s in tdls.stages:
        print(f"    Stage {s.stage_number}: {s.title} — ${s.estimated_cost_usd:,.0f} ({s.estimated_duration_days}d)")
    
    # Shadow Quote
    quote = generate_shadow_quote(0.31, tdls)
    print(f"\n  Shadow Quote: {quote['shadow_quote_id']}")
    print(f"  Platform fee: ${quote['adjusted_fee_usd']:,.0f}")
    print(f"  Precision multiplier: {quote['precision_multiplier']}x")
