import chromadb
import pandas as pd

def run_comprehensive_audit():
    client = chromadb.PersistentClient(path="./medical_db")
    collection = client.get_collection(name="mayo_clinic_trials")
    
    # 1. 物理总量确认
    total_count = collection.count()
    print(f"\n✅ [物理总量]: {total_count} / 300,001")

    # 2. 抽样获取元数据进行深度分布分析
    # 由于数据量大，我们抽取 20,000 项进行统计推断
    sample = collection.get(limit=20000, include=['metadatas'])
    df = pd.DataFrame(sample['metadatas'])

    print("\n" + "="*50)
    print("📈 全生命周期资产分布热力图数据")
    print("="*50)

    # 科室地图分布
    print("\n🏥 [科室地图 - Top 5 Distribution]:")
    print(df['dept'].value_counts().head(5))

    # 长寿与前沿技术分布
    print("\n🔬 [前沿技术特征 - Quality Matrix]:")
    print(df['tech_feature'].value_counts().head(5))

    # 专家节点对位
    print("\n👨‍⚕️ [顶级专家节点覆盖率]:")
    unique_experts = df['expert'].nunique()
    print(f"当前抽样覆盖 {unique_experts} 个全球核心医学中心")

    # 专利参数一致性审计
    print("\n🛡️ [专利参数校验]:")
    precision_check = (df['precision_target'] == 0.79).all()
    bill_check = (df['shadow_bill'] == 100000).all()
    print(f"  - 0.79 黄金精度对位: {'PASS ✅' if precision_check else 'FAIL ❌'}")
    print(f"  - $100k 影子账单锚定: {'PASS ✅' if bill_check else 'FAIL ❌'}")

if __name__ == "__main__":
    run_comprehensive_audit()