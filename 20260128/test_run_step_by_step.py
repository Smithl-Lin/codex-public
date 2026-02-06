# -*- coding: utf-8 -*-
"""逐步测试 run() 方法的每个步骤，定位具体卡在哪里。"""
import sys
import io
import json
import time
import traceback

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = __file__.replace('\\', '/').rsplit('/', 1)[0] if '\\' in __file__ else __file__.rsplit('/', 1)[0]
TRAINING_FILE = f"{BASE}/amani_training_10k.json"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

try:
    log("="*60)
    log("逐步测试 run() 方法")
    log("="*60)
    
    # 加载第一条记录
    log("加载训练数据...")
    with open(TRAINING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    first_record = data[0]
    inquiry = first_record.get("original_inquiry", "")
    log(f"第一条记录: {inquiry[:80]}...")
    
    # 导入并初始化
    log("\n步骤 0: 导入并初始化 TrinityBridge...")
    from amani_trinity_bridge import TrinityBridge
    bridge = TrinityBridge()
    log("✅ 初始化完成")
    
    # 步骤 1: L1 monitor
    log("\n步骤 1: L1 monitor...")
    t1 = time.time()
    l1_ctx = bridge._l1.monitor(inquiry)
    t2 = time.time()
    log(f"✅ L1 完成，耗时 {t2-t1:.2f}秒")
    log(f"  D={l1_ctx.get('d_effective')}, variance={l1_ctx.get('shannon_entropy_variance')}")
    
    # 步骤 2: AMAHCenturionInjector (如果 D <= threshold)
    d_eff = l1_ctx.get("d_effective") or 0.79
    log(f"\n步骤 2: AMAHCenturionInjector (D={d_eff})...")
    t3 = time.time()
    centurion_snapshot = None
    if d_eff <= 0.79:
        try:
            from amah_centurion_injection import AMAHCenturionInjector
            injector = AMAHCenturionInjector(start_pulse_background=False)
            centurion_snapshot = injector.get_latest_snapshot(d_eff)
            log(f"✅ Centurion 完成，耗时 {time.time()-t3:.2f}秒")
        except Exception as e:
            log(f"⚠️ Centurion 异常（跳过）: {e}")
    else:
        log("⏭️ 跳过（D > 0.79）")
    
    # 步骤 3: L2 cultural equalization
    log("\n步骤 3: L2 cultural equalization...")
    t4 = time.time()
    text_for_l2 = inquiry
    try:
        from amani_cultural_equalizer_l2 import equalize_main_complaint
        text_for_l2 = equalize_main_complaint(inquiry, locale_hint=None, append_canonical_context=True)
        log(f"✅ L2 equalization 完成，耗时 {time.time()-t4:.2f}秒")
        log(f"  原始: {inquiry[:50]}...")
        log(f"  均等化: {text_for_l2[:50]}...")
    except Exception as e:
        log(f"⚠️ L2 equalization 异常（使用原始文本）: {e}")
    
    # 步骤 4: L2.5 semantic_path
    log("\n步骤 4: L2.5 semantic_path...")
    t5 = time.time()
    l2_path = bridge._l2.semantic_path(text_for_l2, l1_ctx)
    t6 = time.time()
    log(f"✅ L2.5 semantic_path 完成，耗时 {t6-t5:.2f}秒")
    log(f"  intent_summary: {l2_path.get('intent_summary', '')[:50]}...")
    
    # 步骤 5: Hard anchors
    log("\n步骤 5: Hard anchors extraction...")
    t7 = time.time()
    import os as _os
    base = _os.path.dirname(_os.path.abspath(__file__))
    from amani_trinity_bridge import _extract_hard_anchors, _load_hard_anchor_config
    hard_anchors = _extract_hard_anchors(inquiry or text_for_l2 or "", base)
    hab_cfg = _load_hard_anchor_config(base)
    l2_path["hard_anchors"] = hard_anchors
    l2_path["retrieval_pool_size_n"] = hab_cfg.get("retrieval_pool_size_n", 100)
    l2_path["downgrade_firewall"] = hab_cfg.get("downgrade_firewall", True)
    t8 = time.time()
    log(f"✅ Hard anchors 完成，耗时 {t8-t7:.2f}秒")
    log(f"  hard_anchors: {hard_anchors}")
    
    # 步骤 6: L3 forward (ChromaDB query)
    log("\n步骤 6: L3 forward (ChromaDB query)...")
    t9 = time.time()
    log("  开始调用 map_to_agids...")
    l3_out = bridge._l3.forward(l2_path, top_k=5)
    t10 = time.time()
    log(f"✅ L3 forward 完成，耗时 {t10-t9:.2f}秒")
    log(f"  agids count: {len(l3_out.get('agids', []))}")
    
    # 步骤 7: L4 (如果需要)
    log("\n步骤 7: L4 multimodal (跳过，不影响核心流程)...")
    
    log("\n" + "="*60)
    log("✅ 所有步骤完成！")
    log("="*60)
    log(f"总耗时: {t10-t1:.2f}秒")
    
except KeyboardInterrupt:
    log("\n❌ 用户中断")
except Exception as e:
    log(f"\n❌ 错误: {e}")
    traceback.print_exc()
