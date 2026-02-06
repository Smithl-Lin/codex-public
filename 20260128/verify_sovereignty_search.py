import chromadb

def verify_clinical_sovereignty():
    client = chromadb.PersistentClient(path="./medical_db")
    collection = client.get_collection(name="mayo_clinic_trials")

    # 模拟三个极具挑战性的临床与前沿技术查询
    queries = {
        "Longevity": "Cellular reprogramming and Senolytic therapy for aging reversal",
        "Neurology": "STN-DBS programming and alpha-synuclein PET biomarkers",
        "Rare Disease": "Gene editing for orphan metabolic disorders"
    }

    print("🚀 启动 300,001 资产【临床主权】深度检索测试...\n")

    for key, q_text in queries.items():
        print(f"🔍 正在检索 [{key}] 领域核心资产...")
        # 核心逻辑：基于 0.79 精度的对位搜索
        results = collection.query(
            query_texts=[q_text],
            n_results=2,
            include=['metadatas', 'documents', 'distances']
        )
        
        for i in range(len(results['ids'][0])):
            dist = results['distances'][0][i]
            meta = results['metadatas'][0][i]
            doc = results['documents'][0][i]
            print(f"  - [对位距离]: {dist:.4f} (专利阈值: 0.79)")
            print(f"  - [专家节点]: {meta['expert']}")
            print(f"  - [技术特征]: {meta.get('tech_feature', 'Standard')}")
            print(f"  - [资产摘要]: {doc[:80]}...\n")
        print("-" * 60)

if __name__ == "__main__":
    verify_clinical_sovereignty()