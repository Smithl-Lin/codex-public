# 文件名: batch_build_db.py
import chromadb
import json
import os
# 注意：这里我们使用 Default Embedding (免费且快)，与您现有的库保持一致
# 如果您以后想换回 OpenAI Embedding，记得这里要改

client = chromadb.PersistentClient(path="./medical_db")
collection = client.get_or_create_collection(name="mayo_clinic_trials")

# 1. 读取 JSON 数据
with open("merged_data.json", "r", encoding="utf-8") as f:
    print("❌ 找不到 all_trials.json，请先运行 batch_fetch.py")
    exit()

with open("all_trials.json", "r", encoding="utf-8") as f:
    trials = json.load(f)

print(f"正在处理 {len(trials)} 条数据...")

ids = []
documents = []
metadatas = []

# 2. 准备数据
for trial in trials:
    # 组合成一段完整的可搜索文本
    full_text = f"Trial ID: {trial['id']}\nTitle: {trial['title']}\nStatus: {trial['status']}\n\nCriteria:\n{trial['criteria']}"
    
    ids.append(trial['id'])
    documents.append(full_text)
    metadatas.append({
        "status": trial['status'],
        "source": "ClinicalTrials.gov"
    })

# 3. 批量存入 (Upsert: 如果存在则更新，不存在则插入)
collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print(f"✅ {len(trials)} 个核心试验已成功注入 AI 中台！")
print("现在的数据库包含了：子宫内膜癌、NCI-MATCH 篮子试验、TAPUR 晚期癌症试验、KRAS 靶向药试验。")