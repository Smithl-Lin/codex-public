import chromadb
import json
import random
import time

class AMAHNebulaEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./amah_vector_db")
        self.collection = self.client.get_collection("expert_map_global")
        
    def generate_elite_fingerprint(self, i):
        # 扩展全球及全美顶级医疗枢纽
        hubs = [
            ("Jacksonville", "FL", "Mayo Clinic"),
            ("Houston", "TX", "MD Anderson"),
            ("Baltimore", "MD", "Johns Hopkins"),
            ("San Francisco", "CA", "UCSF"),
            ("Seattle", "WA", "Fred Hutch"),
            ("London", "UK", "Queen Square"),
            ("Heidelberg", "DE", "University Hospital")
        ]
        city, state, aff = random.choice(hubs)
        
        # 挂载前沿医学标签：器械+药物+试验
        domains = [
            ("DBS-Lead-V2", "Neuromodulation", "Medtronic-Percept"),
            ("CAR-T-Cell", "Oncology", "Latest-Immunotherapy"),
            ("CRISPR-Gene-Editing", "Genetics", "Clinical-Trial-Phase-II"),
            ("Focused-Ultrasound", "Non-Invasive", "Insightec-Gen4")
        ]
        tag_set = random.choice(domains)
        
        return {
            "id": f"nebula_node_{i:06d}",
            "document": f"{aff} {city} {state} | {tag_set[0]} {tag_set[1]} | {tag_set[2]} | Medicare International-Ins | Travel-Concierge Hospital-Docking",
            "metadata": {
                "name": f"Dr. {random.choice(['Expert', 'Lead', 'Chief', 'Advisor'])}_{i}",
                "location": f"{city}, {state}",
                "services": json.dumps(["Travel-Concierge", "Hospital-Docking", "Insurance-Liaison"])
            }
        }

    def run_injection(self, count=20000, batch_size=1000):
        print(f"🌌 启动“星云级”注塑：目标增量 {count} 个专家节点...")
        start_time = time.time()
        
        current_count = self.collection.count()
        for i in range(current_count, current_count + count, batch_size):
            batch = [self.generate_elite_fingerprint(j) for j in range(i, i + batch_size)]
            
            self.collection.upsert(
                ids=[x["id"] for x in batch],
                documents=[x["document"] for x in batch],
                metadatas=[x["metadata"] for x in batch]
            )
            print(f"✨ 能量灌注中: {i + batch_size - current_count}/{count}")
            
        print(f"🏁 阶段性扩容完成。总耗时: {time.time() - start_time:.2f}s")
        print(f"📊 AMAH 全球专家库当前总规模: {self.collection.count()}")

if __name__ == "__main__":
    engine = AMAHNebulaEngine()
    engine.run_injection(20000)
