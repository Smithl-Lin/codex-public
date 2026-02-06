# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
import json
import os

def verify_v4_locked():
    print("="*65)
    print("🔎 AMAH V4.0 核心基准自检：[20260128_SMITH_LIN_STRATEGY]")
    print("="*65)
    
    # 1. 验证 10 个核心文件的战略钢印
    core_files = [
        'amani_brain.py', 'amani_core_v4.py', 'conflict_governance_v2_5.py',
        'billing_engine.py', 'amah_weight_orchestrator.py', 'trinity_dispatcher_final.py',
        'app_v4.py', 'advanced_aggregator.py', 'auto_sync.py', 'ontology_engine.py'
    ]
    
    locked_count = 0
    for f in core_files:
        status = "❌ 缺失"
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file:
                header = file.readline()
                if "# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN" in header:
                    status = "✅ 锁定"
                    locked_count += 1
                else:
                    status = "⚠️ 钢印缺失"
        print(f"📄 {f:30} | 状态: {status}")

    # 2. 验证 0.79 专利阈值
    print("-" * 65)
    if os.path.exists('amah_config.json'):
        with open('amah_config.json', 'r') as f:
            config = json.load(f)
            threshold = config.get('alignment_logic', {}).get('precision_lock_threshold', 0.0)
            if threshold == 0.79:
                print(f"🎯 专利精度红线 (D-Value): {threshold} | 状态: ✅ 达标")
            else:
                print(f"🎯 专利精度红线 (D-Value): {threshold} | 状态: ❌ 偏离战略")
    
    print("="*65)
    if locked_count == len(core_files):
        print("🚀 结论：AMANI V4.0 底层架构已实现主权锁定，准备接受压测。")

if __name__ == "__main__":
    verify_v4_locked()