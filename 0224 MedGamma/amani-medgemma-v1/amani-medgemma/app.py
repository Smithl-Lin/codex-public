"""
AMANI — The Alpha Nexus for MedGemma
From Generative Possibilities to Deterministic Reality

Main Demo Application for MedGemma Impact Challenge (Kaggle)
Demonstrates the full 5-layer pipeline:
  L1 Sentinel → L2 MedGemma Orchestrator → L2.5 Value Layer → L3 Global Router → L4 Interface

11 Patents Pending | 200K+ AGID Nodes | Mayo Clinic Research Foundation
"""

import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from l1_sentinel.entropy_scanner import sentinel_scan, StrategicInterceptError, PRECISION_THRESHOLD
from l2_orchestrator.medgemma_engine import MedGemmaEngine, ClinicalProfile
from l2_orchestrator.trinity_audit import trinity_audit, ConsensusStatus
from l2_orchestrator.trial_matcher import match_patient_to_trials, get_trial_by_agid
from l2_orchestrator.asset_registry import resolve_agid, get_connected_assets
from l2_5_value.lifecycle_strategy import generate_tdls, generate_shadow_quote
from l3_nexus.global_router import resolve_global_route, check_compliance

# Scenario-to-country mapping for demo cases
DEMO_SCENARIOS = {
    "case_a": {"source_country": "CN", "source_city": "Shanghai", "dest_country": "US", "scenario_tag": "lung_cancer"},
    "case_b": {"source_country": "SA", "source_city": "Riyadh", "dest_country": "JP", "scenario_tag": "stem_cell"},
    "case_c": {"source_country": "TH", "source_city": "Bangkok", "dest_country": "US", "scenario_tag": "parkinson_bci"},
}


def run_full_pipeline(clinical_note: str, scenario_key: str = "auto") -> dict:
    """Execute the complete AMANI 5-layer pipeline.
    
    Input: Free-text clinical note (any language)
    Output: Full structured result with AGID routing, TDLS, and compliance
    """
    results = {"layers": {}, "errors": []}
    
    # ═══════════════════════════════════════════════════
    # L1: SENTINEL — Intent Information Density Gate
    # ═══════════════════════════════════════════════════
    try:
        sentinel = sentinel_scan(clinical_note)
        results["layers"]["L1_Sentinel"] = {
            "status": sentinel.gate_status,
            "d_value": sentinel.d_value,
            "threshold": PRECISION_THRESHOLD,
            "language": sentinel.language_detected,
            "intent": sentinel.intent_classification,
            "entropy_global": sentinel.entropy_global,
            "confidence": sentinel.confidence,
            "low_entropy_spikes": len(sentinel.low_entropy_spikes),
        }
        if not sentinel.is_high_precision:
            results["warning"] = (
                f"Low precision detected (D={sentinel.d_value:.3f} > {PRECISION_THRESHOLD}). "
                "Results below are provided for reference but may lack clinical specificity. "
                "Human review recommended."
            )
            results["layers"]["L1_Sentinel"]["warning"] = results["warning"]
    except StrategicInterceptError as e:
        results["layers"]["L1_Sentinel"] = {"status": "INTERCEPTED", "error": e.message}
        results["error"] = "Input rejected — insufficient medical intent."
        results["summary"] = {"pipeline_status": "INTERCEPTED", "d_value": getattr(e, 'd_value', None)}
        results["errors"].append(f"L1 Intercept: {e.message}")
        return results
    
    # ═══════════════════════════════════════════════════
    # L2: MEDGEMMA ORCHESTRATOR — Clinical Analysis
    # ═══════════════════════════════════════════════════
    engine = MedGemmaEngine(mode="auto")
    profile = engine.parse_clinical_note(clinical_note, sentinel.language_detected)
    
    results["layers"]["L2_MedGemma"] = {
        "mode": engine.mode,
        "diagnosis": profile.primary_diagnosis,
        "molecular_markers": profile.molecular_markers,
        "treatment_intent": profile.treatment_intent,
        "urgency": profile.urgency,
        "search_query": profile.to_search_query(),
    }
    
    # ═══════════════════════════════════════════════════
    # L2: TRINITY-AUDIT — Multi-Model Consensus
    # ═══════════════════════════════════════════════════
    trinity = trinity_audit(
        profile.to_search_query(),
        task_type="clinical_reasoning",
        mock=True  # Mock for Trinity; real API requires GPT/Claude keys (set AMANI_TRINITY_REAL_API=true)
    )
    
    results["layers"]["L2_Trinity"] = {
        "status": trinity.status.value,
        "v_variance": trinity.v_variance,
        "certainty_index": trinity.certainty_index,
        "consensus_agid": trinity.consensus_agid,
        "consensus_score": trinity.consensus_score,
        "automated": trinity.is_automated,
        "weights": trinity.weights_applied,
        "models": [
            {
                "name": r.model_name,
                "confidence": r.confidence,
                "match_score": r.match_score,
                "agid": r.agid_suggested,
                "safety_flags": r.safety_flags
            }
            for r in trinity.individual_responses
        ]
    }
    
    if not trinity.is_automated:
        results["errors"].append("Trinity conflict — routing to HITL")
        return results

    # ═══════════════════════════════════════════════════
    # L2: TRIAL MATCHING (via MedGemma semantic matching)
    # ═══════════════════════════════════════════════════
    try:
        trial_matches = match_patient_to_trials(profile, engine, top_k=3)
        results["layers"]["L2_TrialMatching"] = {
            "matches_found": len(trial_matches),
            "top_matches": [
                {
                    "rank": m.rank,
                    "nct_id": m.trial_match.nct_id,
                    "title": m.trial_match.title,
                    "institution": m.trial_match.institution,
                    "pi": m.trial_match.pi_name,
                    "match_score": m.trial_match.match_score,
                    "tier": m.tier,
                    "agid": m.trial_match.agid,
                }
                for m in trial_matches
            ]
        }
    except Exception as e:
        trial_matches = []
        results["layers"]["L2_TrialMatching"] = {"matches_found": 0, "error": str(e)}

    # ═══════════════════════════════════════════════════
    # L2: AGID ASSET RESOLUTION
    # ═══════════════════════════════════════════════════
    try:
        primary_agid = trinity.consensus_agid
        resolved_asset = resolve_agid(primary_agid)
        connected = get_connected_assets(primary_agid)
        results["layers"]["L2_AssetResolution"] = {
            "primary_agid": primary_agid,
            "resolved": {
                "name": resolved_asset.name if resolved_asset else "Unknown",
                "institution": resolved_asset.institution if resolved_asset else "",
                "location": resolved_asset.location if resolved_asset else "",
                "asset_type": resolved_asset.asset_type.value if resolved_asset else "",
            } if resolved_asset else None,
            "connected_assets": len(connected),
        }
    except Exception as e:
        resolved_asset = None
        connected = []
        results["layers"]["L2_AssetResolution"] = {"primary_agid": trinity.consensus_agid, "error": str(e)}

    # ═══════════════════════════════════════════════════
    # L2.5: VALUE LAYER — Lifecycle Strategy + Shadow Quote
    # ═══════════════════════════════════════════════════
    # Auto-detect scenario
    if scenario_key == "auto":
        note_lower = clinical_note.lower()
        if any(w in note_lower for w in ["lung", "nsclc", "肺癌", "egfr"]):
            scenario_key = "case_a"
        elif any(w in note_lower for w in ["parkinson", "bci", "dbs", "帕金森", "พาร์กินสัน"]):
            scenario_key = "case_c"
        elif any(w in note_lower for w in ["stem cell", "regenerat", "خلايا", "anti-aging"]):
            scenario_key = "case_b"
        else:
            scenario_key = "case_a"  # default
    
    scenario = DEMO_SCENARIOS.get(scenario_key, DEMO_SCENARIOS["case_a"])
    
    tdls = generate_tdls(
        f"AMANI-{scenario_key.upper()}",
        trinity.consensus_agid,
        f"{profile.primary_diagnosis} — {profile.treatment_intent}",
        scenario=scenario["scenario_tag"],
        urgency=profile.urgency,
        diagnosis=profile.primary_diagnosis
    )
    
    shadow_quote = generate_shadow_quote(sentinel.d_value, tdls)
    
    results["layers"]["L2_5_Value"] = {
        "tdls_stages": len(tdls.stages),
        "total_cost_usd": tdls.total_estimated_cost_usd,
        "total_duration_days": tdls.total_duration_days,
        "shadow_quote_id": shadow_quote["shadow_quote_id"],
        "platform_fee_usd": shadow_quote["adjusted_fee_usd"],
        "precision_multiplier": shadow_quote["precision_multiplier"],
        "stages": [
            {
                "stage": s.stage_number,
                "title": s.title,
                "institution": s.institution,
                "agid": s.agid,
                "cost_usd": s.estimated_cost_usd,
                "duration_days": s.estimated_duration_days,
            }
            for s in tdls.stages
        ],
        "compliance_notes": tdls.compliance_notes,
    }
    
    # ═══════════════════════════════════════════════════
    # L3: NEXUS — Global Route + Compliance
    # ═══════════════════════════════════════════════════
    route = resolve_global_route(
        f"AMANI-{scenario_key.upper()}",
        scenario["source_country"],
        scenario["source_city"],
        trinity.consensus_agid,
        trinity.individual_responses[0].recommendation.split(" at ")[-1] if trinity.individual_responses else "",
        scenario["dest_country"]
    )
    
    results["layers"]["L3_Nexus"] = {
        "source": route.source_location,
        "destination": route.destination_institution,
        "destination_agid": route.destination_agid,
        "routing_hub": route.routing_hub,
        "compliant": route.compliance.compliant,
        "frameworks": f"{route.compliance.framework_source} → {route.compliance.framework_destination}",
        "requirements": route.compliance.requirements,
        "data_sovereignty": route.data_sovereignty_note,
        "route_steps": route.route_steps,
    }
    
    # ═══════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════
    results["summary"] = {
        "pipeline_status": "COMPLETE",
        "d_value": sentinel.d_value,
        "consensus": trinity.status.value,
        "consensus_agid": trinity.consensus_agid,
        "total_pathway_cost": tdls.total_estimated_cost_usd,
        "compliant": route.compliance.compliant,
        "top_trial": trial_matches[0].trial_match.nct_id if trial_matches else "None",
        "top_trial_score": trial_matches[0].trial_match.match_score if trial_matches else 0,
        "asset_resolved": bool(resolved_asset),
        "patent_references": [
            "Patent 1: Staircase Mapping (Gold→Frontier→Recovery)",
            "Patent 2: D-value Precision Gate (D≤0.79)",
            "Patent 5/6/7: Trinity-Audit Consensus",
            "Patent 4: Total Disease Lifecycle Strategy",
            "Patent 11: E-CNN Entropy Texture + GNN AGID Anchoring"
        ]
    }
    
    return results


def build_gradio_app():
    """Build the Gradio demo interface with 4-tab layout."""
    try:
        import gradio as gr
    except ImportError:
        print("Gradio not installed. Run: pip install gradio")
        return None

    # Demo clinical notes
    demo_notes = {
        "Case A: Chinese Lung Cancer → US Gene Therapy":
            "患者男性，52岁，非小细胞肺癌（腺癌）IIIB期。EGFR L858R阳性。三线治疗后进展。ECOG评分1分。患者强烈希望寻求基因治疗或CAR-T等前沿疗法。家属愿意承担跨境就医费用。",
        "Case B: Saudi Anti-Aging → Japan Stem Cell":
            "68-year-old Saudi male, post-CABG 2019, stable CAD, bilateral knee OA Grade III. MoCA 26/30. Seeking comprehensive stem cell regenerative program in Japan. Family office backing.",
        "Case C: Thai Parkinson's → US BCI Trial":
            "ผู้ป่วยชายไทย อายุ 61 ปี โรคพาร์กินสัน H&Y Stage 4 ระยะเวลาป่วย 12 ปี ได้รับการผ่าตัด DBS ปี 2022 ผลการรักษาลดลง ต้องการเข้าถึง BCI clinical trial ในสหรัฐอเมริกา"
    }

    def process_query(clinical_note, scenario):
        """Process clinical note through full pipeline."""
        scenario_map = {
            "Case A: Chinese Lung Cancer → US Gene Therapy": "case_a",
            "Case B: Saudi Anti-Aging → Japan Stem Cell": "case_b",
            "Case C: Thai Parkinson's → US BCI Trial": "case_c",
            "Auto-detect": "auto",
        }
        key = scenario_map.get(scenario, "auto")
        result = run_full_pipeline(clinical_note, key)

        # Extract components for different tabs
        l1_text = format_l1_sentinel(result.get("layers", {}).get("L1_Sentinel", {}))
        l2_text = format_l2_analysis(result.get("layers", {}))
        l3_text = format_l3_routing(result.get("layers", {}))
        full_json = result  # Return dict directly for gr.JSON
        summary_text = format_summary(result.get("summary", {}))

        # Combine L1 + L2 for first tab
        l1_l2_combined = f"{l1_text}\n\n---\n\n{l2_text}"

        return l1_l2_combined, l3_text, summary_text, full_json


    def format_l1_sentinel(l1_data):
        """Format L1 Sentinel results as readable text."""
        if not l1_data:
            return "No L1 data available."

        gate_emoji = "✅" if l1_data.get("status") == "PASS" else "⚠️"
        return f"""## L1 Sentinel — Intent Information Density Gate

{gate_emoji} **Gate Status**: {l1_data.get('status', 'UNKNOWN')}

**D-value**: {l1_data.get('d_value', 0):.4f} (Threshold: {l1_data.get('threshold', 0.79)})
**Language Detected**: {l1_data.get('language', 'unknown').upper()}
**Intent Classification**: {l1_data.get('intent', 'unknown')}
**Confidence**: {l1_data.get('confidence', 0):.2%}

**Entropy Analysis**:
- Global Entropy: {l1_data.get('entropy_global', 0):.4f}
- Low-Entropy Spikes: {l1_data.get('low_entropy_spikes', 0)} detected

**Patent Reference**: Patent 2 (D-value Precision Gate), Patent 11 (E-CNN Entropy Texture)
"""

    def format_l2_analysis(layers):
        """Format L2 MedGemma + Trinity analysis."""
        l2_medgemma = layers.get("L2_MedGemma", {})
        l2_trinity = layers.get("L2_Trinity", {})

        trinity_emoji = "✅" if l2_trinity.get("status") == "CONSENSUS" else "⚠️"

        medgemma_text = f"""## L2 MedGemma Orchestrator — Clinical Analysis

**Mode**: {l2_medgemma.get('mode', 'unknown').upper()}
**Diagnosis**: {l2_medgemma.get('diagnosis', 'N/A')}
**Treatment Intent**: {l2_medgemma.get('treatment_intent', 'N/A')}
**Urgency**: {l2_medgemma.get('urgency', 'standard')}

**Molecular Markers**:
"""
        for marker, value in l2_medgemma.get('molecular_markers', {}).items():
            medgemma_text += f"- {marker}: {value}\n"

        trinity_text = f"""
## L2 Trinity-Audit — Multi-Model Consensus

{trinity_emoji} **Consensus Status**: {l2_trinity.get('status', 'UNKNOWN')}
**V-variance**: {l2_trinity.get('v_variance', 0):.6f} (Threshold: 0.005)
**Certainty Index**: {l2_trinity.get('certainty_index', 0):.4f}
**Consensus AGID**: {l2_trinity.get('consensus_agid', 'N/A')}
**Automated**: {'Yes' if l2_trinity.get('automated') else 'No'}

**Model Weights** (clinical_reasoning):
"""
        for model, weight in l2_trinity.get('weights', {}).items():
            trinity_text += f"- {model.capitalize()}: {weight:.2f}\n"

        trinity_text += "\n**Individual Models**:\n"
        for m in l2_trinity.get('models', []):
            trinity_text += f"- **{m['name'].upper()}**: confidence={m['confidence']:.2f}, match_score={m['match_score']:.2f}\n"

        trinity_text += "\n**Patent Reference**: Patent 5/6/7 (Trinity-Audit Consensus)\n"

        return medgemma_text + trinity_text

    def format_l3_routing(layers):
        """Format L2.5 Value + L3 Nexus routing."""
        l2_5 = layers.get("L2_5_Value", {})
        l3 = layers.get("L3_Nexus", {})

        value_text = f"""## L2.5 Value Layer — Total Disease Lifecycle Strategy

**TDLS Stages**: {l2_5.get('tdls_stages', 0)}
**Total Cost**: ${l2_5.get('total_cost_usd', 0):,.0f} USD
**Total Duration**: {l2_5.get('total_duration_days', 0)} days
**Shadow Quote ID**: {l2_5.get('shadow_quote_id', 'N/A')}
**Platform Fee**: ${l2_5.get('platform_fee_usd', 0):,.2f} USD
**Precision Multiplier**: {l2_5.get('precision_multiplier', 1.0):.2f}x

**Treatment Stages**:
"""
        for stage in l2_5.get('stages', []):
            value_text += f"{stage['stage']}. **{stage['title']}** ({stage['institution']})\n"
            value_text += f"   - Cost: ${stage['cost_usd']:,} | Duration: {stage['duration_days']} days\n"
            value_text += f"   - AGID: {stage['agid']}\n"

        value_text += "\n**Patent Reference**: Patent 4 (TDLS), Patent 2 (Shadow Quote)\n"

        nexus_emoji = "✅" if l3.get('compliant') else "❌"
        nexus_text = f"""
## L3 Nexus Layer — Global Routing & Compliance

{nexus_emoji} **Compliance**: {l3.get('compliant', False)}
**Source**: {l3.get('source', 'N/A')}
**Destination**: {l3.get('destination', 'N/A')}
**Destination AGID**: {l3.get('destination_agid', 'N/A')}
**Routing Hub**: {l3.get('routing_hub', 'N/A')}

**Regulatory Frameworks**: {l3.get('frameworks', 'N/A')}

**Compliance Requirements**:
"""
        for req in l3.get('requirements', []):
            nexus_text += f"- {req}\n"

        nexus_text += f"""
**Data Sovereignty Note**:
{l3.get('data_sovereignty', 'N/A')}

**Patent Reference**: Patent 11 (GNN Asset Anchoring)
"""

        return value_text + nexus_text

    def format_summary(summary):
        """Format executive summary."""
        text = f"""## Executive Summary

**Pipeline Status**: {summary.get('pipeline_status', 'UNKNOWN')}
**D-value**: {summary.get('d_value', 0):.4f}
**Consensus**: {summary.get('consensus', 'N/A')}
**Consensus AGID**: {summary.get('consensus_agid', 'N/A')}
**Total Pathway Cost**: ${summary.get('total_pathway_cost', 0):,} USD
**Compliant**: {'✅ Yes' if summary.get('compliant') else '❌ No'}

**Patent Portfolio** (11 Patents Pending):
"""
        for patent in summary.get('patent_references', []):
            text += f"- {patent}\n"
        return text

    # Build Gradio interface with 4 tabs
    with gr.Blocks(
        title="AMANI — The Alpha Nexus for MedGemma"
    ) as app:
        gr.Markdown("""
        # 🏛️ AMANI — The Alpha Nexus for MedGemma
        ### From Generative Possibilities to Deterministic Reality

        **Global Medical Resource Sovereign Router** | 11 Patents Pending | 200K+ AGID Nodes

        *Enter a clinical note in any language. AMANI will analyze it through 5 sovereign layers
        and route to the optimal global medical resource.*

        ---
        **For Kaggle MedGemma Impact Challenge** | Mayo Clinic Research Foundation | Smith Lin, MD/PhD
        """)

        # Input Section
        with gr.Row():
            scenario_dropdown = gr.Dropdown(
                choices=list(demo_notes.keys()) + ["Auto-detect"],
                value="Auto-detect",
                label="📋 Demo Scenario",
                info="Select a pre-loaded demo case or use auto-detect"
            )
            load_btn = gr.Button("📥 Load Demo Case", variant="secondary", size="sm")

        clinical_input = gr.Textbox(
            lines=6,
            placeholder="Enter clinical note (支持中文、العربية، ไทย, English)...",
            label="🩺 Clinical Note Input",
            info="Paste clinical note or load a demo case above"
        )

        run_btn = gr.Button("🚀 Run AMANI Pipeline", variant="primary", size="lg")

        # Output Tabs
        with gr.Tabs() as tabs:
            with gr.Tab("📊 Analysis (L1+L2)"):
                l1_output = gr.Markdown(label="L1 Sentinel + L2 Analysis")

            with gr.Tab("🗺️ Routing (L2.5+L3)"):
                l3_output = gr.Markdown(label="L2.5 Value + L3 Nexus")

            with gr.Tab("📄 Full Report"):
                with gr.Row():
                    summary_output = gr.Markdown(label="Executive Summary")
                with gr.Row():
                    json_output = gr.JSON(label="Complete Pipeline Output (JSON)")

            with gr.Tab("ℹ️ About"):
                gr.Markdown("""
                ## About AMANI

                **AMANI** (Alpha Medical Asset Nexus Intelligence) is a 5-layer sovereign AI system
                that transforms MedGemma's medical generative capabilities into deterministic global
                medical resource routing.

                ### Five-Layer Architecture

                1. **L1 Sentinel** — Entropy-based Intent Information Density (IID) gate (D ≤ 0.79)
                2. **L2 Orchestrator** — MedGemma 1.5 4B + Trinity-Audit (GPT/MedGemma/Claude)
                3. **L2.5 Value** — Total Disease Lifecycle Strategy (TDLS) + Shadow Quote
                4. **L3 Nexus** — Global AGID routing + HIPAA/GDPR/PIPL compliance
                5. **L4 Interface** — This Gradio UI (multilingual: EN/ZH/AR/TH)

                ### Patent Portfolio (11 Patents Pending)

                - Patent 1: Staircase Mapping (Gold → Frontier → Recovery)
                - Patent 2: D-value Precision Gate (D ≤ 0.79)
                - Patent 4: Total Disease Lifecycle Strategy (TDLS)
                - Patent 5/6/7: Trinity-Audit Multi-Model Consensus
                - Patent 8: PI Fingerprint Enhancement
                - Patent 11: E-CNN Entropy Texture + GNN Asset Anchoring

                ### Clinical Authority

                **Smith Lin, MD/PhD**
                Research Fellow, Department of Neurologic Surgery
                Mayo Clinic Florida
                2,000+ DBS patients managed | AI/ML in Parkinson's Disease

                ### Disclaimer

                AMANI provides Resource Routing Pathways, not medical advice. All outputs are for
                institutional decision support only. Mayo Strategic Reference / Non-Diagnostic Asset Routing.

                ---

                **Competition**: Kaggle MedGemma Impact Challenge 2026
                **Source Code**: https://github.com/[submission]
                **Contact**: [Mayo Clinic Research Foundation]
                """)

        # Event handlers
        def load_demo(scenario):
            return demo_notes.get(scenario, "")

        load_btn.click(load_demo, inputs=[scenario_dropdown], outputs=[clinical_input])
        run_btn.click(
            process_query,
            inputs=[clinical_input, scenario_dropdown],
            outputs=[l1_output, l3_output, summary_output, json_output],
            api_name="process_clinical_note"
        )

    return app


# --- Main Entry Point ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AMANI MedGemma Demo")
    parser.add_argument("--mode", choices=["cli", "gradio"], default="cli")
    parser.add_argument("--case", choices=["a", "b", "c"], default="a")
    args = parser.parse_args()
    
    if args.mode == "gradio":
        app = build_gradio_app()
        if app:
            app.launch(
                server_name="127.0.0.1",
                server_port=7861
            )
    else:
        # CLI mode — run all three demo cases
        demo_inputs = {
            "a": ("患者男性，52岁，非小细胞肺癌IIIB期。EGFR L858R阳性。三线治疗后进展。寻求基因治疗或CAR-T临床试验。", "case_a"),
            "b": ("68-year-old Saudi male, post-CABG 2019, bilateral knee OA Grade III. Seeking comprehensive stem cell regenerative program in Japan.", "case_b"),
            "c": ("61-year-old Thai male with Parkinson's disease H&Y Stage 4. Post bilateral STN-DBS 2022 declining. Seeking BCI clinical trial in US.", "case_c"),
        }
        
        note, scenario = demo_inputs[args.case]
        print(f"\n{'='*70}")
        print(f"AMANI Pipeline — Demo Case {args.case.upper()}")
        print(f"{'='*70}")
        print(f"Input: {note[:80]}...")
        
        result = run_full_pipeline(note, scenario)
        print(json.dumps(result, indent=2, ensure_ascii=False))
