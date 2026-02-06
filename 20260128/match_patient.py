# 文件名: match_patient.py
import chromadb
from langchain_openai import OpenAIEmbeddings

client = chromadb.PersistentClient(path="./medical_db")
collection = client.get_collection(name="mayo_clinic_trials")

# 模拟一个高净值客户的中文需求
patient_query = """
患者信息：女性，45岁，病理确诊为宫颈癌（Cervical Cancer）。
治疗史：已完成子宫切除术（Hysterectomy）。
核心诉求：想了解术后辅助放射治疗方案，希望能减少对周围器官的副作用。
"""

print(f"正在为患者匹配全球资源：\n{patient_query}")

# 在向量空间中搜索最近的邻居
results = collection.query(
    query_texts=[patient_query],
    n_results=1
)

# 输出结果
if results['documents']:
    matched_doc = results['documents'][0][0]
    matched_id = results['ids'][0][0]
    print("\n" + "="*30)
    print(f"🎯 匹配成功！推荐试验 ID: {matched_id}")
    print("="*30)
    print("AI 匹配依据（原始英文标准片段）：")
    print(matched_doc[:300] + "...")
else:
    print("未找到匹配的试验。")