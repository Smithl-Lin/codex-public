# V4.0_STRATEGIC_LOCKED_BY_SMITH_LIN
# -*- coding: utf-8 -*-
"""
前置条件验证脚本：检查所有必需的配置、数据和依赖
"""
import os
import sys
import json


def check_env_vars():
    """检查环境变量配置"""
    print("\n" + "="*70)
    print("🔑 1. 环境变量检查")
    print("="*70)

    from dotenv import load_dotenv
    load_dotenv()

    keys = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        'MEDGEMMA_ENDPOINT': os.getenv('MEDGEMMA_ENDPOINT'),
    }

    has_any_llm = False
    for k, v in keys.items():
        if k in ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']:
            if v:
                has_any_llm = True
        status = '✅' if v else '❌'
        masked = (v[:10] + '...' if len(v) > 10 else v) if v else '未配置'
        print(f"{status} {k:35} : {masked}")

    if not has_any_llm:
        print("\n⚠️  警告: 至少需要配置一个 LLM API key (Gemini/OpenAI/Anthropic)")
        return False

    return True


def check_data_files():
    """检查必需的数据文件"""
    print("\n" + "="*70)
    print("📁 2. 数据文件检查")
    print("="*70)

    required_files = {
        'amah_config.json': '系统配置',
        'merged_data.json': '临床试验主库',
        'expert_map_data.json': '专家/PI 表',
        'hospital_center_assets.json': '医院/中心表',
    }

    all_exist = True
    for f, desc in required_files.items():
        if os.path.isfile(f):
            size = os.path.getsize(f)
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    count = len(data) if isinstance(data, list) else 1
                print(f"✅ {f:30} | {desc:20} | {count:6} 条 | {size/1024:.1f} KB")
            except Exception as e:
                print(f"⚠️  {f:30} | {desc:20} | 解析失败: {e}")
                all_exist = False
        else:
            print(f"❌ {f:30} | {desc:20} | 文件缺失")
            all_exist = False

    return all_exist


def check_chromadb():
    """检查 ChromaDB 初始化状态"""
    print("\n" + "="*70)
    print("🗄️  3. ChromaDB 检查")
    print("="*70)

    if not os.path.isdir('amah_vector_db'):
        print("❌ amah_vector_db/ 目录不存在")
        print("   解决方案: 运行 python batch_build_db.py")
        return False

    try:
        import chromadb
        client = chromadb.PersistentClient(path='./amah_vector_db')
        collections = client.list_collections()

        if not collections:
            print("⚠️  ChromaDB 目录存在但无集合")
            print("   解决方案: 运行 python batch_build_db.py")
            return False

        for c in collections:
            count = c.count()
            print(f"✅ 集合: {c.name:25} | {count:8} 条记录")

        # 检查必需集合
        coll_names = [c.name for c in collections]
        if 'expert_map_global' not in coll_names:
            print("⚠️  缺少 expert_map_global 集合")
            print("   解决方案: 运行 python expert_bulk_loader.py")
            return False

        return True
    except Exception as e:
        print(f"❌ ChromaDB 错误: {e}")
        return False


def check_physical_registry():
    """检查物理节点注册表"""
    print("\n" + "="*70)
    print("🗺️  4. 物理节点注册表检查")
    print("="*70)

    if not os.path.isfile('physical_node_registry.json'):
        print("❌ physical_node_registry.json 不存在")
        print("   解决方案: 运行 python sync_l2_to_chromadb.py")
        return False

    try:
        with open('physical_node_registry.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            count = len(data) if isinstance(data, list) else 0
            print(f"✅ 物理节点注册表: {count} 个映射")

            if count == 0:
                print("⚠️  注册表为空")
                return False

            # 显示示例
            if isinstance(data, list) and data:
                sample = data[0]
                print(f"   示例 AGID: {sample.get('agid', 'N/A')}")
                print(f"   示例区域: {sample.get('region', 'N/A')}")

            return True
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return False


def check_dependencies():
    """检查 Python 依赖"""
    print("\n" + "="*70)
    print("📦 5. Python 依赖检查")
    print("="*70)

    required = {
        'streamlit': 'Streamlit UI',
        'chromadb': 'Vector Database',
        'pandas': 'Data Processing',
        'numpy': 'Numerical Computing',
        'openai': 'OpenAI API',
        'anthropic': 'Anthropic API',
        'google.cloud.aiplatform': 'Google Vertex AI',
        'dotenv': 'Environment Variables',
    }

    all_installed = True
    for module, desc in required.items():
        try:
            if module == 'google.cloud.aiplatform':
                __import__('google.cloud.aiplatform')
            elif module == 'dotenv':
                __import__('dotenv')
            else:
                __import__(module)
            print(f"✅ {module:30} | {desc}")
        except ImportError:
            print(f"❌ {module:30} | {desc} | 未安装")
            all_installed = False

    if not all_installed:
        print("\n   解决方案: pip install -r requirements.txt")

    return all_installed


def check_deployment_critical():
    """生产化关键项：amah_config 必需段、physical_node_registry、ChromaDB 路径；缺则提示运行 sync_l2_to_chromadb。"""
    print("\n" + "="*70)
    print("🚀 生产化关键项检查")
    print("="*70)

    ok = True
    if not os.path.isfile('amah_config.json'):
        print("❌ amah_config.json 不存在")
        ok = False
    else:
        try:
            with open('amah_config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            required_sections = ['alignment_logic', 'trinity_audit_gate', 'centurion_injection']
            for sec in required_sections:
                if sec not in cfg:
                    print("⚠️  amah_config.json 缺少段: %s" % sec)
                    ok = False
            if ok:
                print("✅ amah_config.json 存在且含 alignment_logic / trinity_audit_gate / centurion_injection")
        except Exception as e:
            print("❌ amah_config.json 解析失败: %s" % e)
            ok = False

    if not os.path.isfile('physical_node_registry.json'):
        print("❌ physical_node_registry.json 不存在")
        print("   解决方案: 运行 python sync_l2_to_chromadb.py")
        ok = False
    else:
        print("✅ physical_node_registry.json 存在")

    chroma_ok = os.path.isdir('amah_vector_db') or os.path.isdir('medical_db')
    if not chroma_ok:
        print("⚠️  ChromaDB 路径不存在 (amah_vector_db 或 medical_db)")
        print("   解决方案: 运行 python batch_build_db.py 或 sync_l2_to_chromadb.py")
        ok = False
    else:
        print("✅ ChromaDB 路径存在 (amah_vector_db 或 medical_db)")

    return ok


def check_core_modules():
    """检查核心 AMANI 模块可导入性"""
    print("\n" + "="*70)
    print("🧩 6. 核心模块检查")
    print("="*70)

    core_modules = [
        'config',
        'amani_core_v4',
        'amani_trinity_bridge',
        'amani_nexus_layer_v3',
        'amani_interface_layer_v4',
        'amani_value_layer_v4',
        'medical_reasoner',
        'billing_engine',
    ]

    all_ok = True
    for mod in core_modules:
        try:
            __import__(mod)
            print(f"✅ {mod}")
        except Exception as e:
            print(f"❌ {mod:30} | 错误: {str(e)[:40]}")
            all_ok = False

    return all_ok


def main():
    """运行所有检查"""
    print("🚀 A.M.A.N.I. V4.0 前置条件验证")
    print("   检查系统是否具备运行条件...")

    checks = [
        ("Python 依赖", check_dependencies),
        ("环境变量", check_env_vars),
        ("数据文件", check_data_files),
        ("ChromaDB", check_chromadb),
        ("物理节点注册表", check_physical_registry),
        ("生产化关键项", check_deployment_critical),
        ("核心模块", check_core_modules),
    ]

    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as e:
            print(f"\n❌ {name} 检查异常: {e}")
            results[name] = False

    # 总结
    print("\n" + "="*70)
    print("📊 验证总结")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有前置条件满足！系统可以启动。")
        print("\n下一步:")
        print("  • 运行测试: python test_trinity_full_pipeline.py")
        print("  • 启动 UI: streamlit run app.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 项检查失败，请先解决以上问题。")
        print("\n快速修复:")
        if not results.get("ChromaDB"):
            print("  1. python batch_build_db.py")
            print("  2. python expert_bulk_loader.py")
        if not results.get("物理节点注册表") or not results.get("生产化关键项"):
            print("  3. python sync_l2_to_chromadb.py  # 生成 physical_node_registry.json")
        if not results.get("Python 依赖"):
            print("  4. pip install -r requirements.txt")
        if not results.get("环境变量"):
            print("  5. 编辑 .env 文件填入 API keys")
        return 1


if __name__ == "__main__":
    sys.exit(main())
