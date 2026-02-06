import json
import pandas as pd

def run_audit():
    with open('amah_config.json', 'r') as f:
        config = json.load(f)
    
    print("="*60)
    print(f"🚀 AMAH SYSTEM AUDIT REPORT - {config['system_version']}")
    print(f"Timestamp: {config['audit_date']} | Location: {config['geographical_hardening']['primary_hub']}")
    print("="*60)
    
    print("\n[1] ASSET INVENTORY (资产清单)")
    for k, v in config['asset_metrics'].items():
        print(f" - {k.replace('_', ' ').title()}: {v:,}")
        
    print("\n[2] CORE ALGORITHM PARAMETERS (核心算法参数)")
    sl = config['logic_parameters']['staircase_logic']
    print(f" - Staircase Staging: Hard Boost ({sl['hard_boost_coefficient']}x), Frontier Multiplier ({sl['frontier_multiplier']}x)")
    
    oa = config['logic_parameters']['ontological_alignment']
    print(f" - Alignment Engine: Precision Threshold D <= {oa['lock_threshold_d']}")
    print(f" - Commercial Value: Shadow Billing per match ${oa['shadow_billing_unit']:,}")
    
    print("\n[3] TRINITY-AUDIT CONSENSUS (三位一体审计)")
    ta = config['logic_parameters']['trinity_audit']
    print(f" - Consensus Models: {', '.join(ta['models'])}")
    print(f" - Recursive Fallback Path: {' -> '.join(ta['fallback_tiers'])}")
    
    print("\n[4] IP STATUS (知识产权状态)")
    print(" - Status: PATENT PENDING (8 Core Patents Registered)")
    print("="*60)

if __name__ == "__main__":
    run_audit()
