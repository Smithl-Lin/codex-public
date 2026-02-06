# -*- coding: utf-8 -*-
"""详细测试 run_safe，捕获所有异常。"""
import sys
import io
import traceback

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from amani_trinity_bridge import TrinityBridge
    
    print("="*60)
    print("测试 run_safe - 详细异常捕获")
    print("="*60)
    
    bridge = TrinityBridge()
    print("✅ TrinityBridge 初始化成功")
    
    # 测试 1: 会触发 L1 拦截的文本
    print("\n测试 1: 触发 L1 拦截的文本")
    try:
        result = bridge.run_safe("测试文本：帕金森病患者寻求BCI治疗方案", top_k_agids=5)
        print(f"  结果类型: {type(result)}")
        print(f"  结果: {result}")
        if result:
            print(f"  intercepted: {result.get('intercepted')}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        traceback.print_exc()
    
    # 测试 2: 简单英文文本（应该能通过 L1）
    print("\n测试 2: 简单英文文本")
    try:
        result = bridge.run_safe("Patient seeking treatment", top_k_agids=5)
        print(f"  结果类型: {type(result)}")
        print(f"  结果: {result}")
        if result:
            print(f"  intercepted: {result.get('intercepted')}")
            print(f"  l3_nexus: {result.get('l3_nexus')}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        traceback.print_exc()
    
    # 测试 3: 空字符串
    print("\n测试 3: 空字符串")
    try:
        result = bridge.run_safe(" ", top_k_agids=5)
        print(f"  结果类型: {type(result)}")
        print(f"  结果: {result}")
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ 导入或初始化失败: {e}")
    traceback.print_exc()
