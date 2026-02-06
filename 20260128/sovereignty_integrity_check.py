import chromadb
import pandas as pd
from collections import Counter

def run_integrity_audit():
    client = chromadb.PersistentClient(path="./medical_db")
    collection = client.get_collection(name="mayo_clinic_trials")
    
    print("🔍 启动 AMAH 平台 [资产-专家] 全球逻辑对位深度审计...")
    
    # 获取样本进行统计分析 (抽取 30,000 项，占比 10%)
    sample_size = 30000
    results = collection.get(limit=sample_size, include=['metadatas'])
    metas = results['metadatas']
    df = pd.DataFrame(metas)

    print("\n" + "="*60)
    print("📊 AMAH 资产质量与配对完整性报告")
    print("="*60)

    # 1. 专家中心资产密度分析 (Top 10 Centers)
    print("\n🏢 [专家节点载荷分析 - Top 10 Centers]:")
    print(df['expert'].value_counts().head(10))

    # 2. 临床对位逻辑检查 (科室 vs 地理分布)
    print("\n🌍 [地理主权分布]:")
    print(df['region'].value_counts())

    # 3. 核心疾病/技术配对质量 (Longevity & Tech)
    print("\n🔬 [高溢价资产配对抽检]:")
    tech_counts = df['tech_feature'].value_counts().head(5)
    print(f"  - 先进技术覆盖种类: {len(df['tech_feature'].unique())}")
    print(tech_counts)

    # 4. 完整性红线检查
    missing_expert = df['expert'].isnull().sum()
    missing_tech = df['tech_feature'].isnull().sum()
    precision_consistency = (df['precision_target'] == 0.79).all()

    print("\n🛡️ [系统完整性红线]:")
    print(f"  - 专家缺失项: {'NONE ✅' if missing_expert == 0 else f'{missing_expert} ❌'}")
    print(f"  - 技术特征缺失: {'NONE ✅' if missing_tech == 0 else f'{missing_tech} ❌'}")
    print(f"  - 0.79 专利精度对齐: {'100% PASS ✅' if precision_consistency else 'FAIL ❌'}")

    # 5. 逻辑错位预警 (示例：检查长寿资产是否挂载到了非相关中心)
    longevity_in_wrong_place = df[(df['dept'] == 'Geriatrics & Longevity') & 
                                  (~df['expert'].str.contains('Aging|Longevity|Altos|Hevolution|Buck', case=False, na=False))]
    
    print(f"\n⚠️ [临床逻辑错位预警]:")
    print(f"  - 长寿资产潜在错位风险项: {len(longevity_in_wrong_place)} (抽样样本中)")
    if len(longevity_in_wrong_place) > 0:
        print("    *建议执行自动校准逻辑以确保专利 5 的拦截精度。")

if __name__ == "__main__":
    run_integrity_audit()