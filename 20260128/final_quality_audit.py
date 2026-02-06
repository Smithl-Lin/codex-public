import chromadb

def run_quality_check():
    client = chromadb.PersistentClient(path="./medical_db")
    collection = client.get_collection(name="mayo_clinic_trials")

    # 模拟两个最高价值的检索场景
    test_scenarios = [
        {"query": "Advanced Parkinson's neurostimulation", "dept": "Neurology"},
        {"query": "Senolytic therapy and age reversal", "dept": "Geriatrics & Longevity"}
    ]

    print("🚀 正在执行 [资产-技术-专家] 逻辑配对深度审核...\n")

    for scenario in test_scenarios:
        print(f"📡 正在压力测试领域: [{scenario['dept']}]")
        results = collection.query(
            query_texts=[scenario['query']],
            n_results=3,
            include=['metadatas', 'documents']
        )
        
        for i in range(len(results['ids'][0])):
            meta = results['metadatas'][0][i]
            print(f"  - [资产 ID]: {results['ids'][0][i]}")
            print(f"  - [技术特征]: {meta.get('tech_feature')}")
            print(f"  - [对位专家]: {meta.get('expert')} ({meta.get('region')})")
            print(f"  - [专利对位]: {meta.get('precision_target')} / $100k Shadow Bill")
            print(f"  - [资产描述]: {results['documents'][0][i][:70]}...")
            print("  " + "."*30)
        print("-" * 60)

if __name__ == "__main__":
    run_quality_check()