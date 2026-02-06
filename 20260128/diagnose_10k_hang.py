# -*- coding: utf-8 -*-
"""
诊断 10k 任务卡住的原因：逐步测试 TrinityBridge 初始化和单次调用。
"""
import sys
import time
import traceback
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = Path(__file__).resolve().parent

def test_step(step_name: str, func, timeout: int = 30):
    """测试一个步骤，带超时检测。"""
    print(f"\n{'='*60}")
    print(f"测试步骤: {step_name}")
    print(f"{'='*60}")
    start = time.time()
    try:
        result = func()
        elapsed = time.time() - start
        print(f"✅ 成功 ({elapsed:.2f}秒)")
        return True, result, None
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ 失败 ({elapsed:.2f}秒)")
        print(f"错误: {e}")
        traceback.print_exc()
        return False, None, str(e)

def test_import():
    """测试导入 TrinityBridge。"""
    def _import():
        from amani_trinity_bridge import TrinityBridge
        return TrinityBridge
    return test_step("1. 导入 TrinityBridge", _import)

def test_init():
    """测试 TrinityBridge 初始化。"""
    def _init():
        from amani_trinity_bridge import TrinityBridge
        bridge = TrinityBridge()
        return bridge
    return test_step("2. TrinityBridge() 初始化", _init, timeout=60)

def test_chromadb():
    """测试 ChromaDB 连接。"""
    def _chroma():
        import chromadb
        chroma_path = BASE / "amah_vector_db"
        if chroma_path.is_dir():
            client = chromadb.PersistentClient(path=str(chroma_path))
            collection = client.get_collection("expert_map_global")
            count = collection.count()
            print(f"  ChromaDB 集合 'expert_map_global' 包含 {count} 条记录")
            return count
        else:
            print(f"  ChromaDB 路径不存在: {chroma_path}")
            return 0
    return test_step("3. ChromaDB 连接测试", _chroma, timeout=60)

def test_l1_only():
    """测试仅 L1（不涉及 L2/L3）。"""
    def _l1():
        from amani_trinity_bridge import ECNNSentinel
        sentinel = ECNNSentinel()
        result = sentinel.monitor("测试文本：帕金森病患者寻求BCI治疗方案")
        print(f"  L1 结果: D={result.get('d_effective')}, variance={result.get('shannon_entropy_variance')}")
        return result
    return test_step("4. L1 ECNNSentinel 单独测试", _l1)

def test_run_safe_one():
    """测试单次 run_safe 调用。"""
    def _run():
        from amani_trinity_bridge import TrinityBridge
        bridge = TrinityBridge()
        result = bridge.run_safe("测试文本：帕金森病患者寻求BCI治疗方案", top_k_agids=5)
        print(f"  run_safe 结果: intercepted={result.get('intercepted')}, agid_count={len(result.get('l3_nexus', {}).get('agids', []))}")
        return result
    return test_step("5. 单次 run_safe 调用", _run, timeout=120)

def main():
    print("="*60)
    print("10k 任务卡住原因诊断脚本")
    print("="*60)
    
    results = {}
    
    # 步骤 1: 导入
    ok, _, err = test_import()
    results["import"] = {"ok": ok, "error": err}
    if not ok:
        print("\n❌ 导入失败，无法继续")
        return
    
    # 步骤 2: 初始化
    ok, bridge, err = test_init()
    results["init"] = {"ok": ok, "error": err}
    if not ok:
        print("\n❌ 初始化失败，问题可能在 ChromaDB 连接或模块导入")
        return
    
    # 步骤 3: ChromaDB
    ok, count, err = test_chromadb()
    results["chromadb"] = {"ok": ok, "count": count, "error": err}
    
    # 步骤 4: L1 单独
    ok, _, err = test_l1_only()
    results["l1_only"] = {"ok": ok, "error": err}
    
    # 步骤 5: 完整 run_safe
    ok, _, err = test_run_safe_one()
    results["run_safe"] = {"ok": ok, "error": err}
    
    # 汇总
    print("\n" + "="*60)
    print("诊断汇总")
    print("="*60)
    for step, r in results.items():
        status = "✅" if r.get("ok") else "❌"
        print(f"{status} {step}: {r.get('error', 'OK')}")
    
    # 建议
    print("\n" + "="*60)
    print("建议")
    print("="*60)
    if not results.get("init", {}).get("ok"):
        print("1. TrinityBridge 初始化失败，检查 ChromaDB 路径和权限")
    elif not results.get("run_safe", {}).get("ok"):
        print("2. run_safe 调用失败，问题可能在 L2/L3 处理阶段")
        print("   - 检查 medical_reasoner 模块是否正常")
        print("   - 检查 amani_cultural_equalizer_l2 模块是否正常")
        print("   - 检查 ChromaDB 查询是否超时")
    elif results.get("run_safe", {}).get("ok"):
        print("3. 单次调用正常，问题可能在批量处理时的资源耗尽或死锁")
        print("   - 考虑添加超时机制")
        print("   - 考虑分批处理并释放资源")

if __name__ == "__main__":
    main()
