import chromadb
import json
import random
import time
from chromadb.config import Settings

class AMAHMegaLoader:
    def __init__(self):
        # 初始化持久化存储
        self.client = chromadb.PersistentClient(path="./amah_vector_db")
        # 针对大规模数据调优 HNSW 索引
        self.collection = self.client.get_or_create_collection(
            name="expert_map_global",
            metadata={
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 800,
                "hnsw:M": 64
            }
        )

    def generate_high_fidelity_batch(self, count):
        """生成大规模高精专家镜像数据"""
        hubs = ["Jacksonville", "Houston", "Boston", "Cleveland", "Palo Alto", "New York"]
        specialties = ["STN-DBS", "Focused-Ultrasound", "Neuro-Regeneration", "Gene-Therapy"]
        
        batch_data = []
        for i in range(count):
            hub = random.choice(hubs)
            spec = random.choice(specialties)
            expert = {
                "id": f"mega_exp_{i:06d}",
                "name": f"Dr. Elite_{hub}_{i}",
                "document": f"{hub} {spec} Precision Medicine Medicare Travel-Concierge latest clinical trials {spec}",
                "metadata": {
                    "hub": hub,
                    "specialty": spec,
                    "services": json.dumps(["Hospital-Docking", "Travel-Concierge"])
                }
            }
            batch_data.append(expert)
        return batch_data

    def execute_bulk_import(self, total_count, batch_size=500):
        """执行大规模分批导入"""
        print(f"🚀 开始硬化 {total_count} 个专家节点至向量空间...")
        start_time = time.time()
        
        for i in range(0, total_count, batch_size):
            batch = self.generate_high_fidelity_batch(min(batch_size, total_count - i))
            
            self.collection.upsert(
                ids=[e["id"] for e in batch],
                documents=[e["document"] for e in batch],
                metadatas=[e["metadata"] for e in batch]
            )
            if i % 5000 == 0:
                print(f"✅ 已完成: {i}/{total_count}")
        
        print(f"🏁 导入完成。总耗时: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    loader = AMAHMegaLoader()
    # 先注入 1000 个高精种子节点用于路演展示（可根据需要调整为 100,000）
    loader.execute_bulk_import(1000)
    print(f"\n📌 当前库中总资产数: {loader.collection.count()}")
