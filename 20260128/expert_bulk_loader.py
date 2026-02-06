import chromadb
import json
import time
import numpy as np
from chromadb.utils import embedding_functions

class AMAHBulkExpertEngine:
    def __init__(self):
        # 1. 初始化持久化客户端
        self.client = chromadb.PersistentClient(path="./amah_vector_db")
        
        # 2. 核心精度参数配置
        # 调高 M 和 construction_ef 以确保 10万级数据下的 0.79 匹配精度
        self.collection = self.client.get_or_create_collection(
            name="expert_map_global",
            metadata={
                "hnsw:space": "cosine", 
                "hnsw:construction_ef": 400, # 深度索引构建
                "hnsw:M": 32                 # 增加连接数，提升召回率
            }
        )
        print("🏛️ AMAH 全球专家索引空间已硬化。")

    def batch_import(self, data_list, batch_size=100):
        """
        分批导入逻辑，防止内存溢出，确保后续持续更新。
        """
        total = len(data_list)
        print(f"📦 准备处理 {total} 个专家节点...")
        
        for i in range(0, total, batch_size):
            batch = data_list[i : i + batch_size]
            ids = [item['id'] for item in batch]
            # 增强型语义文本：整合全生命周期服务标签
            documents = [
                f"{item['name']} | {item['affiliation']} | {item['specialty']} | "
                f"Tags: {', '.join(item['expertise_tags'])} | "
                f"Services: {', '.join(item['value_add_services'])}" 
                for item in batch
            ]
            metadatas = [{
                "name": item['name'],
                "location": f"{item['location']['city']}, {item['location']['state']}",
                "insurance": json.dumps(item['insurance_partners'])
            } for item in batch]

            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            print(f"✅ 已完成: {min(i + batch_size, total)} / {total}")

    def unified_match_audit(self, query):
        """
        全路径精准匹配验证
        """
        start = time.time()
        results = self.collection.query(
            query_texts=[query],
            n_results=3,
            include=['documents', 'distances', 'metadatas']
        )
        
        print(f"\n📊 检索耗时: {time.time()-start:.4f}s")
        for i in range(len(results['ids'][0])):
            accuracy = 1 - results['distances'][0][i]
            if accuracy >= 0.79:
                print(f"🎯 [精准对位] {results['metadatas'][0][i]['name']} | 精度: {accuracy:.4f}")
                print(f"🔗 资源指向: {results['documents'][0][i][:120]}...")
            else:
                print(f"⚠️ [低精拦截] 匹配度 {accuracy:.4f} 未达 0.79 阈值。")

if __name__ == "__main__":
    engine = AMAHBulkExpertEngine()
    
    # 模拟真实 100+ 专家导入 (实际可对接您的 CSV/数据库)
    # 这里我们复用之前的数据，但在实际路演时，建议加载您完整的专家清单
    try:
        with open('expert_map_data.json', 'r') as f:
            data = json.load(f)
            engine.batch_import(data)
    except FileNotFoundError:
        print("❌ 未找到数据文件，请先生成 expert_map_data.json")

    # 验证匹配准确性与策略延续性
    test_query = "Find STN-DBS experts in Florida for refractory tremors, must handle international travel."
    engine.unified_match_audit(test_query)
