# -*- coding: utf-8 -*-
"""测试第一条记录的处理，带详细时间戳。"""
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
    log("开始测试第一条记录处理")
    
    # 加载第一条记录
    log("加载训练数据...")
    with open(TRAINING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    first_record = data[0]
    log(f"第一条记录: request_id={first_record.get('request_id')}, inquiry={first_record.get('original_inquiry', '')[:50]}...")
    
    # 导入 TrinityBridge
    log("导入 TrinityBridge...")
    from amani_trinity_bridge import TrinityBridge
    
    # 初始化
    log("初始化 TrinityBridge...")
    t0 = time.time()
    bridge = TrinityBridge()
    t1 = time.time()
    log(f"初始化完成，耗时 {t1-t0:.2f}秒")
    
    # 处理第一条记录
    log("开始处理第一条记录...")
    t2 = time.time()
    inquiry = first_record.get("original_inquiry", "")
    log(f"输入文本: {inquiry[:100]}...")
    
    result = bridge.run_safe(inquiry or " ", top_k_agids=5)
    t3 = time.time()
    log(f"处理完成，耗时 {t3-t2:.2f}秒")
    
    log(f"结果: intercepted={result.get('intercepted')}, agid_count={len(result.get('l3_nexus', {}).get('agids', []))}")
    log("✅ 第一条记录处理成功")
    
except Exception as e:
    log(f"❌ 错误: {e}")
    traceback.print_exc()
