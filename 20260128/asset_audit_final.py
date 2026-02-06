import chromadb
import pandas as pd

def audit_and_clean():
    client = chromadb.PersistentClient(path="./medical_db")
    collection = client.get_collection(name="mayo_clinic_trials")
    
    # 1. 提取全量元数据进行审计
    data = collection.get()
    ids = data['ids']
    metas = data['metadatas']
    
    df = pd.DataFrame(metas)
    df['id'] = ids
    
    # 2. 剔除重复的资产 (基于 ID 或标题)
    initial_count = len(df)
    df_clean = df.drop_duplicates(subset=['id'])
    
    # 3. 分布统计：科室与专家对位
    dept_dist = df_clean['dept'].value_counts()
    expert_dist = df_clean['expert'].value_counts()
    
    print(f"✅ 审计完成：初始 {initial_count} -> 提纯后 {len(df_clean)}")
    print(f"📊 科室分布TOP 3: \n{dept_dist.head(3)}")
    print(f"👨‍⚕️ 顶级专家节点映射数: {len(expert_dist)} 个中心")

if __name__ == "__main__":
    audit_and_clean()