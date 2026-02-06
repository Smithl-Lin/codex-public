# 文件名: test_basket_match.py
import chromadb
# 注意：不导入 OpenAIEmbeddings，使用默认模型以匹配 batch_build_db.py 的配置
import os

# 1. 连接数据库
client = chromadb.PersistentClient(path="./medical_db")
collection = client.get_collection(name="mayo_clinic_trials")

# 2. 定义高净值客户病历 (复杂场景)
# 这是一个典型的“篮子试验”候选人：
# - 肺癌 (Lung Cancer)
# - KRAS G12C 突变 (关键匹配点)
# - 既往化疗失败 (符合二线/三线治疗标准)
patient_profile = """
患者信息：男性，58岁，确诊为非小细胞肺癌 (NSCLC)。
基因检测报告：KRAS G12C 突变阳性。
治疗史：一线含铂化疗进展，免疫治疗无效。
核心诉求：寻求针对 KRAS 突变的最新靶向药物临床试验。
"""

print(f"🧬 正在为【KRAS 突变】患者检索全球资源...")
print(f"患者画像：{patient_profile.strip()}")
print("-" * 30)

# 3. 检索 (Retrieval)
# 我们请求返回最匹配的 2 个结果，看看 AI 能否把靶向药排在第一位
results = collection.query(
    query_texts=[patient_profile],
    n_results=2 
)

# 4. 展示结果
if results['documents']:
    print(f"🔍 检索完成，找到 {len(results['documents'][0])} 个潜在匹配项：\n")
    
    for i in range(len(results['documents'][0])):
        trial_id = results['ids'][0][i]
        doc_preview = results['documents'][0][i][:200].replace('\n', ' ')
        distance = results['distances'][0][i] # 距离越小越匹配
        
        print(f"【排名 {i+1}】 Trial ID: {trial_id}")
        print(f"   匹配距离: {distance:.4f}")
        print(f"   内容摘要: {doc_preview}...")
        print("-" * 30)

    # 自动判断是否命中 KRYSTAL-1 (NCT04589845)
    top_id = results['ids'][0][0]
    if top_id == "NCT04589845":
        print("\n✅ 成功！AI 准确识别出了 Adagrasib (KRYSTAL-1) 靶向药试验。")
    else:
        print(f"\n⚠️ 警告：AI 首选了 {top_id}，而非预期的 KRAS 试验。")
else:
    print("❌ 未找到匹配项。")