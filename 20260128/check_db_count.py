import chromadb

# 必须指向与 blitz_expansion.py 完全相同的路径
client = chromadb.PersistentClient(path="./medical_db")
collection = client.get_collection(name="mayo_clinic_trials")

total_count = collection.count()
print(f"✅ 底层数据库检测到总资产数: {total_count}")

# 检查是否存在新标签
results = collection.peek(limit=1)
print(f"抽检首条资产元数据: {results['metadatas']}")