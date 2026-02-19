"""
AMANI L2 Orchestrator — Asset Registry (AGID Resolution)

Physical Asset Global ID (AGID) registry for medical resources.
Maps AGID tokens → complete institutional/facility/PI metadata.

**AGID Architecture** (Patent 11: GNN Asset Anchoring):
- AGID format: AGID-[TYPE]-[ID]-[SUB]
  Examples:
    - AGID-NCT-06234517 (Clinical Trial)
    - AGID-JP-KEIO-REGEN-002 (Institution Program)
    - AGID-MAYO-JAX-DBS-001 (Surgical Facility)
    - AGID-PI-STARR-PHILIP (Principal Investigator)

**Data Sovereignty Principle**:
Only AGID tokens cross borders. No PHI. Patient data stays in source jurisdiction.

**Competition Note**:
For Kaggle demo, uses static JSON registry (20-30 demo assets).
Production version scales to 200,000+ verified nodes globally.
"""

import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum


class AssetType(Enum):
    """Types of medical assets in the AGID system."""
    CLINICAL_TRIAL = "clinical_trial"
    INSTITUTION = "institution"
    PRINCIPAL_INVESTIGATOR = "principal_investigator"
    SURGICAL_FACILITY = "surgical_facility"
    MEDICAL_DEVICE = "medical_device"
    IMAGING_CENTER = "imaging_center"
    REHABILITATION_CENTER = "rehabilitation_center"
    TELEMEDICINE_SERVICE = "telemedicine_service"
    TRANSLATION_SERVICE = "translation_service"
    TRAVEL_COORDINATION = "travel_coordination"


@dataclass
class AGIDAsset:
    """Complete metadata for a medical asset."""
    agid: str
    asset_type: AssetType
    name: str
    institution: str
    location: Dict[str, str]  # {"city": "...", "state": "...", "country": "...", "coordinates": "..."}
    contact: Dict[str, str]  # {"email": "...", "phone": "...", "website": "..."}

    # Asset-specific metadata
    principal_investigator: Optional[str] = None
    nct_id: Optional[str] = None
    phase: Optional[str] = None
    condition: Optional[str] = None
    capacity: Optional[int] = None  # Annual patient capacity
    certifications: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)

    # GNN Anchoring (Patent 11)
    connected_assets: List[str] = field(default_factory=list)  # Related AGIDs
    trust_score: float = 1.0  # 0.0-1.0, based on verification status
    verification_date: Optional[str] = None

    # PI Fingerprint (Patent 8) — for PI assets
    pi_h_index: Optional[int] = None
    pi_nct_trials_as_pi: Optional[int] = None
    pi_surgical_volume: Optional[int] = None
    pi_negative_risk_score: Optional[float] = None
    pi_frontier_boost_applied: Optional[bool] = None


# --- Demo Asset Registry (20-30 verified nodes for competition) ---
DEMO_ASSET_REGISTRY = [
    # Clinical Trials
    AGIDAsset(
        agid="AGID-NCT-06234517",
        asset_type=AssetType.CLINICAL_TRIAL,
        name="CAR-T Cell Therapy for EGFR-Positive Advanced NSCLC",
        institution="MD Anderson Cancer Center",
        location={"city": "Houston", "state": "TX", "country": "US", "coordinates": "29.7081,-95.4009"},
        contact={"email": "cart_trial@mdanderson.org", "phone": "+1-713-792-2121", "website": "https://www.mdanderson.org/trials/NCT06234517"},
        principal_investigator="Dr. John Heymach",
        nct_id="NCT-06234517",
        phase="Phase I/II",
        condition="Non-Small Cell Lung Cancer",
        capacity=30,
        certifications=["FDA IND", "IRB Approved"],
        specializations=["CAR-T", "EGFR-targeted", "Immunotherapy"],
        connected_assets=["AGID-PI-HEYMACH-JOHN", "AGID-MDA-THORACIC-001"],
        trust_score=1.0,
        verification_date="2026-01-15"
    ),
    AGIDAsset(
        agid="AGID-NCT-06578901",
        asset_type=AssetType.CLINICAL_TRIAL,
        name="Implantable BCI for Motor Restoration in Advanced Parkinson's Disease",
        institution="University of California San Francisco (UCSF)",
        location={"city": "San Francisco", "state": "CA", "country": "US", "coordinates": "37.7621,-122.4580"},
        contact={"email": "bci_pd@ucsf.edu", "phone": "+1-415-353-2000", "website": "https://clinicaltrials.ucsf.edu/NCT06578901"},
        principal_investigator="Dr. Philip Starr",
        nct_id="NCT-06578901",
        phase="Phase I Early Feasibility",
        condition="Parkinson's Disease",
        capacity=12,
        certifications=["FDA IDE", "IRB Approved"],
        specializations=["BCI", "Neuromodulation", "DBS", "Movement Disorders"],
        connected_assets=["AGID-PI-STARR-PHILIP", "AGID-UCSF-NEURO-001"],
        trust_score=1.0,
        verification_date="2026-01-20",
        pi_h_index=78,
        pi_nct_trials_as_pi=12,
        pi_surgical_volume=800,
        pi_negative_risk_score=0.0,
        pi_frontier_boost_applied=True
    ),
    AGIDAsset(
        agid="AGID-NCT-AADC-PD",
        asset_type=AssetType.CLINICAL_TRIAL,
        name="AAV2-hAADC Gene Therapy for Advanced Parkinson's Disease",
        institution="UCSF / Neurocrine Biosciences",
        location={"city": "San Francisco", "state": "CA", "country": "US", "coordinates": "37.7621,-122.4580"},
        contact={"email": "aadc_pd@ucsf.edu", "phone": "+1-415-353-2000", "website": "https://clinicaltrials.ucsf.edu/AADC-PD"},
        principal_investigator="Dr. Krystof Bankiewicz",
        nct_id="NCT-06123456",
        phase="Phase II",
        condition="Parkinson's Disease",
        capacity=24,
        certifications=["FDA IND", "IRB Approved", "Gene Therapy Certification"],
        specializations=["AADC", "Gene Therapy", "AAV2", "Parkinson"],
        connected_assets=["AGID-PI-BANKIEWICZ-KRYSTOF", "AGID-UCSF-NEURO-001"],
        trust_score=1.0,
        verification_date="2026-01-18"
    ),

    # Institutional Programs
    AGIDAsset(
        agid="AGID-JP-KEIO-REGEN-002",
        asset_type=AssetType.INSTITUTION,
        name="Keio University Hospital — Department of Regenerative Medicine",
        institution="Keio University Hospital",
        location={"city": "Tokyo", "state": "", "country": "JP", "coordinates": "35.6471,139.7111"},
        contact={"email": "regenerative@keio.jp", "phone": "+81-3-3353-1211", "website": "https://www.keio-med.jp/regenerative"},
        principal_investigator="Dr. Hideyuki Okano",
        capacity=200,
        certifications=["PMDA Regenerative Medicine Class II", "ISO 13485"],
        specializations=["MSC", "Knee OA", "Autologous Stem Cell", "Cartilage Regeneration"],
        connected_assets=["AGID-PI-OKANO-HIDEYUKI", "AGID-JP-KEIO-ORTHO-001"],
        trust_score=0.98,
        verification_date="2026-01-10"
    ),
    AGIDAsset(
        agid="AGID-JP-HELENE-001",
        asset_type=AssetType.INSTITUTION,
        name="Helene Regenerative Medicine Clinic",
        institution="Helene Clinic Tokyo",
        location={"city": "Tokyo", "state": "", "country": "JP", "coordinates": "35.6762,139.6503"},
        contact={"email": "info@heleneclinic.jp", "phone": "+81-3-1234-5678", "website": "https://www.heleneclinic.jp"},
        principal_investigator="Dr. Hiroshi Tanaka",
        capacity=500,
        certifications=["PMDA Class II", "JCI Accredited"],
        specializations=["Anti-Aging", "MSC-IV", "PRP", "Exosome", "Rejuvenation"],
        connected_assets=["AGID-PI-TANAKA-HIROSHI"],
        trust_score=0.92,
        verification_date="2025-12-20"
    ),

    # Principal Investigators
    AGIDAsset(
        agid="AGID-PI-STARR-PHILIP",
        asset_type=AssetType.PRINCIPAL_INVESTIGATOR,
        name="Dr. Philip Starr",
        institution="UCSF Department of Neurological Surgery",
        location={"city": "San Francisco", "state": "CA", "country": "US", "coordinates": "37.7621,-122.4580"},
        contact={"email": "philip.starr@ucsf.edu", "phone": "+1-415-353-7500", "website": "https://profiles.ucsf.edu/philip.starr"},
        specializations=["DBS", "BCI", "Movement Disorders", "Parkinson", "Functional Neurosurgery"],
        trust_score=1.0,
        verification_date="2026-01-20",
        pi_h_index=78,
        pi_nct_trials_as_pi=12,
        pi_surgical_volume=800,
        pi_negative_risk_score=0.0,
        pi_frontier_boost_applied=True,
        connected_assets=["AGID-NCT-06578901", "AGID-UCSF-NEURO-001"]
    ),
    AGIDAsset(
        agid="AGID-PI-HEYMACH-JOHN",
        asset_type=AssetType.PRINCIPAL_INVESTIGATOR,
        name="Dr. John Heymach",
        institution="MD Anderson Cancer Center",
        location={"city": "Houston", "state": "TX", "country": "US", "coordinates": "29.7081,-95.4009"},
        contact={"email": "jheymach@mdanderson.org", "phone": "+1-713-792-6363", "website": "https://faculty.mdanderson.org/profiles/john_heymach.html"},
        specializations=["Thoracic Oncology", "EGFR", "Targeted Therapy", "Immunotherapy"],
        trust_score=1.0,
        verification_date="2026-01-15",
        pi_h_index=102,
        pi_nct_trials_as_pi=28,
        connected_assets=["AGID-NCT-06234517", "AGID-MDA-THORACIC-001"]
    ),

    # Supporting Services
    AGIDAsset(
        agid="AGID-TRANSLATE-001",
        asset_type=AssetType.TRANSLATION_SERVICE,
        name="AMANI Medical Translation Service",
        institution="AMANI Platform",
        location={"city": "Multi-Region", "state": "", "country": "Global", "coordinates": ""},
        contact={"email": "translation@amani.health", "phone": "", "website": "https://amani.health/translation"},
        capacity=1000,
        certifications=["HIPAA-Compliant", "Certified Medical Translators", "ISO 17100"],
        specializations=["ZH↔EN", "AR↔EN", "TH↔EN", "Medical Records", "Pathology Reports"],
        trust_score=0.95,
        verification_date="2026-01-01"
    ),
    AGIDAsset(
        agid="AGID-TRAVEL-MDA-001",
        asset_type=AssetType.TRAVEL_COORDINATION,
        name="AMANI Travel Coordination — MD Anderson Pathway",
        institution="AMANI Platform",
        location={"city": "Houston", "state": "TX", "country": "US", "coordinates": "29.7081,-95.4009"},
        contact={"email": "travel@amani.health", "phone": "+1-800-AMANI-TX", "website": "https://amani.health/travel"},
        capacity=500,
        specializations=["Medical Visa (B-2)", "Accommodation", "Airport Transfer", "Interpreter"],
        trust_score=0.93,
        verification_date="2026-01-05"
    ),
    AGIDAsset(
        agid="AGID-TRAVEL-UCSF-001",
        asset_type=AssetType.TRAVEL_COORDINATION,
        name="AMANI Travel Coordination — UCSF Pathway",
        institution="AMANI Platform",
        location={"city": "San Francisco", "state": "CA", "country": "US", "coordinates": "37.7621,-122.4580"},
        contact={"email": "travel@amani.health", "phone": "+1-800-AMANI-SF", "website": "https://amani.health/travel"},
        capacity=300,
        specializations=["Medical Visa (B-2)", "Long-term Accommodation", "Caregiver Support"],
        trust_score=0.93,
        verification_date="2026-01-05"
    ),
    AGIDAsset(
        agid="AGID-MDA-FOLLOWUP-001",
        asset_type=AssetType.TELEMEDICINE_SERVICE,
        name="MD Anderson Post-Treatment Telemedicine",
        institution="MD Anderson Cancer Center",
        location={"city": "Houston", "state": "TX", "country": "US", "coordinates": "29.7081,-95.4009"},
        contact={"email": "telemedicine@mdanderson.org", "phone": "+1-713-563-1000", "website": "https://www.mdanderson.org/telemedicine"},
        capacity=2000,
        certifications=["HIPAA-Compliant", "Cross-Border Telemedicine License"],
        specializations=["Post-CAR-T Monitoring", "Toxicity Management", "Long-term Follow-up"],
        trust_score=0.98,
        verification_date="2026-01-12"
    ),
    AGIDAsset(
        agid="AGID-REHAB-SH-001",
        asset_type=AssetType.REHABILITATION_CENTER,
        name="Shanghai Zhongshan Hospital — Oncology Rehabilitation",
        institution="Shanghai Zhongshan Hospital",
        location={"city": "Shanghai", "state": "", "country": "CN", "coordinates": "31.2304,121.4737"},
        contact={"email": "rehab@zs-hospital.sh.cn", "phone": "+86-21-6404-1990", "website": "http://www.zs-hospital.sh.cn"},
        capacity=800,
        certifications=["PIPL-Compliant", "China Hospital Accreditation (三级甲等)"],
        specializations=["Post-Cancer Treatment", "Nutrition Support", "Physical Therapy"],
        trust_score=0.90,
        verification_date="2025-12-28"
    ),

    # Additional Nodes
    AGIDAsset(
        agid="AGID-CHULA-NEURO-001",
        asset_type=AssetType.INSTITUTION,
        name="Chulalongkorn University Hospital — Department of Neurology",
        institution="Chulalongkorn University Hospital",
        location={"city": "Bangkok", "state": "", "country": "TH", "coordinates": "13.7323,100.5332"},
        contact={"email": "neuro@chula.ac.th", "phone": "+66-2-256-4000", "website": "https://www.chulahospital.go.th/neurology"},
        capacity=400,
        certifications=["PDPA-Compliant", "JCI Accredited"],
        specializations=["DBS", "Parkinson", "Movement Disorders", "Stroke"],
        connected_assets=["AGID-UCSF-REHAB-001"],
        trust_score=0.95,
        verification_date="2026-01-08"
    ),
    AGIDAsset(
        agid="AGID-UCSF-REHAB-001",
        asset_type=AssetType.REHABILITATION_CENTER,
        name="UCSF Neurorehabilitation Center",
        institution="UCSF Medical Center",
        location={"city": "San Francisco", "state": "CA", "country": "US", "coordinates": "37.7621,-122.4580"},
        contact={"email": "neurorehab@ucsf.edu", "phone": "+1-415-353-2000", "website": "https://www.ucsfhealth.org/neurorehab"},
        capacity=150,
        certifications=["CARF Accredited", "HIPAA-Compliant"],
        specializations=["BCI Calibration", "DBS Programming", "Motor Rehabilitation", "Parkinson"],
        trust_score=0.98,
        verification_date="2026-01-20"
    ),
    AGIDAsset(
        agid="AGID-KFSH-CARDIAC-001",
        asset_type=AssetType.INSTITUTION,
        name="King Faisal Specialist Hospital — Cardiology Department",
        institution="King Faisal Specialist Hospital & Research Centre",
        location={"city": "Riyadh", "state": "", "country": "SA", "coordinates": "24.7136,46.6753"},
        contact={"email": "cardio@kfshrc.edu.sa", "phone": "+966-11-464-7272", "website": "https://www.kfshrc.edu.sa/cardiology"},
        capacity=600,
        certifications=["JCI Accredited", "PDPL-Compliant"],
        specializations=["Cardiac Clearance", "Pre-operative Assessment", "Geriatric Cardiology"],
        trust_score=0.97,
        verification_date="2026-01-05"
    ),
    AGIDAsset(
        agid="AGID-KFSH-REGEN-001",
        asset_type=AssetType.TELEMEDICINE_SERVICE,
        name="KFSH Regenerative Medicine Follow-up",
        institution="King Faisal Specialist Hospital & Research Centre",
        location={"city": "Riyadh", "state": "", "country": "SA", "coordinates": "24.7136,46.6753"},
        contact={"email": "regen@kfshrc.edu.sa", "phone": "+966-11-464-7272", "website": "https://www.kfshrc.edu.sa/regenerative"},
        capacity=300,
        certifications=["Telemedicine License (Saudi)", "PDPL-Compliant"],
        specializations=["Post-MSC Monitoring", "Cross-border Coordination"],
        trust_score=0.94,
        verification_date="2026-01-06"
    ),
]


def resolve_agid(agid: str, registry: Optional[List[AGIDAsset]] = None) -> Optional[AGIDAsset]:
    """Resolve an AGID to its full asset metadata.

    Args:
        agid: Asset Global ID (e.g., "AGID-NCT-06234517")
        registry: Asset registry (default: DEMO_ASSET_REGISTRY)

    Returns:
        AGIDAsset object if found, None otherwise
    """
    if registry is None:
        registry = DEMO_ASSET_REGISTRY

    for asset in registry:
        if asset.agid == agid:
            return asset
    return None


def search_assets_by_type(
    asset_type: AssetType,
    registry: Optional[List[AGIDAsset]] = None
) -> List[AGIDAsset]:
    """Find all assets of a given type."""
    if registry is None:
        registry = DEMO_ASSET_REGISTRY

    return [a for a in registry if a.asset_type == asset_type]


def search_assets_by_location(
    country: str,
    city: Optional[str] = None,
    registry: Optional[List[AGIDAsset]] = None
) -> List[AGIDAsset]:
    """Find assets in a specific location."""
    if registry is None:
        registry = DEMO_ASSET_REGISTRY

    results = []
    for asset in registry:
        if asset.location.get("country", "").upper() == country.upper():
            if city is None or asset.location.get("city", "").lower() == city.lower():
                results.append(asset)
    return results


def search_assets_by_specialization(
    keyword: str,
    registry: Optional[List[AGIDAsset]] = None
) -> List[AGIDAsset]:
    """Find assets with a specific specialization keyword."""
    if registry is None:
        registry = DEMO_ASSET_REGISTRY

    keyword_lower = keyword.lower()
    results = []
    for asset in registry:
        if any(keyword_lower in spec.lower() for spec in asset.specializations):
            results.append(asset)
    return results


def get_connected_assets(agid: str, registry: Optional[List[AGIDAsset]] = None) -> List[AGIDAsset]:
    """Get all assets connected to a given AGID (GNN graph traversal)."""
    if registry is None:
        registry = DEMO_ASSET_REGISTRY

    asset = resolve_agid(agid, registry)
    if not asset:
        return []

    connected = []
    for connected_agid in asset.connected_assets:
        connected_asset = resolve_agid(connected_agid, registry)
        if connected_asset:
            connected.append(connected_asset)
    return connected


# --- CLI Test ---
if __name__ == "__main__":
    print("="*60)
    print("AMANI Asset Registry — Test Suite")
    print("="*60)

    # Test 1: AGID Resolution
    print("\n[Test 1] AGID Resolution")
    agid = "AGID-NCT-06234517"
    asset = resolve_agid(agid)
    if asset:
        print(f"  AGID: {asset.agid}")
        print(f"  Name: {asset.name}")
        print(f"  Institution: {asset.institution}")
        print(f"  Location: {asset.location['city']}, {asset.location['country']}")
        print(f"  PI: {asset.principal_investigator}")
        print(f"  Contact: {asset.contact['email']}")
        print(f"  Trust Score: {asset.trust_score}")

    # Test 2: Search by Type
    print("\n[Test 2] Search Clinical Trials")
    trials = search_assets_by_type(AssetType.CLINICAL_TRIAL)
    print(f"  Found {len(trials)} clinical trials:")
    for t in trials[:3]:
        print(f"    - {t.agid}: {t.name}")

    # Test 3: Search by Location
    print("\n[Test 3] Search Assets in US")
    us_assets = search_assets_by_location("US", city="San Francisco")
    print(f"  Found {len(us_assets)} assets in San Francisco, US:")
    for a in us_assets:
        print(f"    - {a.agid}: {a.name}")

    # Test 4: Search by Specialization
    print("\n[Test 4] Search 'Parkinson' Specialization")
    pd_assets = search_assets_by_specialization("Parkinson")
    print(f"  Found {len(pd_assets)} assets with Parkinson specialization:")
    for a in pd_assets:
        print(f"    - {a.agid}: {a.name} ({a.asset_type.value})")

    # Test 5: GNN Connected Assets
    print("\n[Test 5] GNN Connected Assets")
    agid = "AGID-NCT-06578901"
    connected = get_connected_assets(agid)
    print(f"  AGID {agid} is connected to {len(connected)} assets:")
    for c in connected:
        print(f"    - {c.agid}: {c.name}")
