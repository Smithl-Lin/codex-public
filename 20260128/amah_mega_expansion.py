import chromadb
import json
import random
import time

class AMAHScaleEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./amah_vector_db")
        self.collection = self.client.get_collection("expert_map_global")
        
    def generate_clinical_fingerprint(self, i):
        """生成具备战略延续性的临床指纹数据"""
        hubs = [
            ("Jacksonville", "FL", "Mayo Clinic"),
            ("Houston", "TX", "Houston Methodist"),
            ("Rochester", "MN", "Mayo Clinic"),
            ("Cleveland", "OH", "Cleveland Clinic"),
            ("Boston", "MA", "MGH"),
            ("Palo Alto", "CA", "Stanford")
        ]
        city, state, aff = random.choice(hubs)
        
        # 模拟最新医疗器械与药物的关联
        techs = ["STN-DBS", "GPi-DBS", "Focused-Ultrasound", "Gene-Therapy", "Monoclonal-Antibodies"]
        trials = ["Phase-III-Enrolled", "FDA-Breakthrough-Device", "Latest-Clinical-Protocol"]
        
        selected_tech = random.choice(techs)
        
        return {
            "id": f"mega_node_{i:06d}",
            "document": f"{aff} {city} {state} | {selected_tech} Expert | {random.choice(trials)} | Medicare BlueCross | Travel-Concierge Hospital-Docking",
            "metadata": {
                "name": f"Dr. {random.choice(['Smith', 'Lin', 'Garcia', 'Chen', 'Taylor'])}_{i}",
                "location": f"{city}, {state}",
                "services": json.dumps(["Travel-Concierge", "Hospital-Docking", "Insurance-Liaison"])
            }
        }

    def run_expansion(self, count=5000, batch_size=500):
        print(f"🚀 启动注塑程序：目标增加 {count} 个专家节点...")
        start_time = time.time()
        
        for i in range(0, count, batch_size):
            batch = [self.generate_clinical_fingerprint(j) for j in range(i, i + batch_size)]
            
            self.collection.upsert(
                ids=[x["id"] for x in batch],
                documents=[x["document"] for x in batch],
                metadatas=[x["metadata"] for x in batch]
            )
            print(f"✅ 已注入: {i + batch_size}/{count}")
            
        print(f"🏁 扩容完成。总耗时: {time.time() - start_time:.2f}s")
        print(f"📊 当前库中专家资产总数: {self.collection.count()}")

if __name__ == "__main__":
    engine = AMAHScaleEngine()
    engine.run_expansion(5000)
