# 文件名: build_db.py
import chromadb
from langchain_openai import OpenAIEmbeddings
import os

# 检查 Key 是否存在
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("请先设置 OPENAI_API_KEY 环境变量！")

# 1. 初始化 Embedding 模型 (将文本转为数学向量)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. 初始化本地向量数据库 (会自动创建 medical_db 文件夹)
client = chromadb.PersistentClient(path="./medical_db")
collection = client.get_or_create_collection(name="mayo_clinic_trials")

# 3. 读取刚才抓取的数据
with open("trial_data.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# 4. 存入数据库
print("正在向量化并存入数据库...")
collection.add(
    documents=[full_text],
    metadatas=[{"source": "Mayo Clinic", "type": "Proton Therapy"}],
    ids=["NCT04567771"]
)
print("✅ 成功！数据已成为可调度的智能资产。")