# 文件名: batch_build_db.py
import json
import chromadb
import os

def build_medical_db():
    print("🚀 启动全球医疗资产库同步程序 (V10K 稳定去重版)...")
    
    # 1. 初始化数据库
    client = chromadb.PersistentClient(path="./medical_db")
    collection = client.get_or_create_collection(name="mayo_clinic_trials")

    # 2. 加载全量数据
    if not os.path.exists("merged_data.json"):
        print("❌ 错误: 未找到 merged_data.json 文件。")
        return

    with open("merged_data.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # --- 核心修复：执行全局 ID 去重 ---
    # 使用字典推导式，以 id 为 key，确保每一个 NCT 编号只保留最后一份最新记录
    unique_map = {item['id']: item for item in raw_data}
    data = list(unique_map.values())
    
    print(f"🧹 原始数据: {len(raw_data)} 条 | 去重后唯一资产: {len(data)} 条")
    print(f"📦 正在准备将 {len(data)} 条唯一资产数据注入 Mayo Clinic AI 中台...")

    # 3. 分批次注入 (每批 2000 条)
    batch_size = 2000
    for i in range(0, len(data), batch_size):
        batch = data[i : i + batch_size]
        
        ids = [item['id'] for item in batch]
        documents = [item['criteria'] for item in batch]
        metadatas = [{
            "source": item['source'],
            "category": item['category'],
            "title": item['title'],
            "status": item['status']
        } for item in batch]

        print(f"⏳ 正在注入第 {i} 到 {min(i + batch_size, len(data))} 条记录...")
        
        try:
            collection.upsert(
                ids=ids,
                metadatas=metadatas,
                documents=documents
            )
        except Exception as e:
            print(f"⚠️ 批次注入异常: {e}")
            # 如果某一批次内仍有特殊字符导致的错误，跳过该批次继续
            continue

    print(f"✅ 成功！当前数据库总规模: {collection.count()} 项。")

if __name__ == "__main__":
    build_medical_db()