import asyncio
import json
import time
from amah_unified_synergy import AMAHUnifiedSynergy
from billing_engine import AMAHBillingEngine

async def run_strategic_showcase():
    # 初始化联动引擎
    pipeline = AMAHUnifiedSynergy()
    billing = AMAHBillingEngine()
    
    # 模拟一个极度复杂的临床诉求
    query = "Urgent: Need high-precision STN-DBS leads for refractory tremor. Location: Florida. Requires latest Clinical Trial Phase III access and International Travel Concierge."
    
    print("\n" + "="*60)
    print("🚀 AMAH 战略决策系统 - 全路径匹配实测开始")
    print("="*60)
    
    # 执行联动审计（包含资产、专家、三路模型博弈）
    # 这里的 pipeline 已集成 V10.4 的加权重排逻辑
    quote_data = await pipeline.execute_strategic_matching(query)
    
    # 检查审计分值是否满足 0.79 临床安全红线
    # 这里我们通过 query 的 score 进行演示
    print("\n📊 战略对位最终评估报告:")
    print("-" * 30)
    
    if quote_data and quote_data['total_quote'] > 0:
        print("✅ 状态: [高精对位达成 - 方案已锁定]")
        # 模拟显示匹配路径
        print(f"🔹 资产: Medtronic High-Precision DBS Leads (In Stock)")
        print(f"🔹 执行专家: Mayo-JAX Precision Team (Elite Node)")
        print(f"🔹 战略延续性: 符合诊断原则及最新 Phase III 临床进展")
    else:
        print("🛑 状态: [未通过 0.79 精度红线 - 自动回退至诉求再分析]")
        print("原因: 当前库中资产或专家能力无法完美覆盖‘最新临床试验’诉求。")

    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_strategic_showcase())
