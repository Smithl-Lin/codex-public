import chromadb
import time

# 1. 挂载已硬化的专家库
client = chromadb.PersistentClient(path="./amah_vector_db")
collection = client.get_collection("expert_map_global")

# 2. V10.3 硬化查询：剔除自然语言噪声，只输入高密特征
test_query = "STN-DBS Parkinson Florida Jacksonville Medicare Travel-Concierge"

print(f"🔍 正在执行 V10.3 核心语义硬化检索...")
print(f"🎯 目标阈值: 0.79 | 查询词: {test_query}")

start = time.time()
results = collection.query(
    query_texts=[test_query],
    n_results=3,
    include=['documents', 'distances', 'metadatas']
)
elapsed = time.time() - start

print("-" * 50)
for i in range(len(results['ids'][0])):
    # 计算余弦相似度
    accuracy = 1 - results['distances'][0][i]
    name = results['metadatas'][0][i]['name']
    
    if accuracy >= 0.79:
        print(f"✅ [高精对位成功] 专家: {name} | 准确性: {accuracy:.4f}")
    else:
        print(f"⚠️ [拦截] 专家: {name} | 准确性: {accuracy:.4f} (未达标)")

print(f"\n📊 检索耗时: {elapsed:.4f}s")
print("-" * 50)
