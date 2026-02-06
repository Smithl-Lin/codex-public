import json
import numpy as np

def run_med_gemini_demo():
    # Load locked genome parameters
    try:
        with open('amah_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: amah_config.json not found. Please ensure the config is generated.")
        return
    
    print("="*70)
    print("🧬 AMAH MED-GEMINI SUITABILITY AUDIT (PATENT 5, 6, 7)")
    print("="*70)
    
    # Simulating a high-complexity case for Jacksonville Roadshow
    case_description = "Stage IV NSCLC with Brain Metastasis. Testing Consensus Logic."
    print(f"Clinical Case: {case_description}\n")

    # Simulated heterogeneous scores (S) from Trinity models
    # S1 (GPT): 0.95, S2 (Gemini): 0.92, S3 (Claude): 0.75
    # S3 mimics a model disagreement (Variance trigger)
    scores = np.array([0.95, 0.92, 0.75])
    model_names = config['trinity_audit_gate']['consensus_models']
    
    # Calculate weighted variance (V)
    # Formula: V = sum(Wi * (Si - mean(S))^2)
    variance = np.var(scores)
    threshold = 0.01  # Strict threshold for clinical safety
    
    print("--- Trinity-Audit Execution ---")
    for name, score in zip(model_names, scores):
        print(f" > {name} Alignment Score: {score}")
    
    print(f"\nCalculated Decision Variance (V): {variance:.4f}")
    
    # Logic for Recursive Fallback (Patent 7)
    if variance > threshold:
        print("\n⚠️ [INTERCEPT] Variance exceeds threshold! Triggering Patent 7 Fallback.")
        fallback_path = config['trinity_audit_gate']['fallback_path']
        print(f"Recursive Path: {fallback_path[0]} -> {fallback_path[1]} (CATEGORY SWAP)")
        print("Status: AUTOMATION SUSPENDED. Routing to Expert Team (Smith Lin).")
    else:
        print("\n✅ [LOCKED] High Consensus. D-Value Alignment verified.")
        print(f"Commercial Shadow Billing Activated: ${config['alignment_logic']['shadow_billing_unit_usd']:,}")
    
    print("="*70)

if __name__ == "__main__":
    run_med_gemini_demo()
