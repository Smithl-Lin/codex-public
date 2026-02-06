import os
import asyncio
import chromadb
import json
import time
from trinity_api_connector import AMAHWeightedEngine

class AMAHFullPipeline:
    def __init__(self):
        # 1. 挂载高速向量引擎
        self.chroma_client = chromadb.PersistentClient(path="./amah_vector_db")
        self.engine = AMAHWeightedEngine()
        print("✅ AMAH 全链路引擎初始化完成")

    async def run_dispatch(self, user_query):
        start_time = time.time()
        print(f"\n📢 收到原始诉求: {user_query}")

        # 步骤 1: 向量库初步检索 (Top-3 资产匹配)
        # 模拟 Level 4 判定后定位到 neurology_assets 分片
        collection = self.chroma_client.get_collection("neurology_assets")
        
        print("🔍 正在从 10万级资产库中检索最匹配条目...")
        search_results = collection.query(
            query_texts=[user_query],
            n_results=3
        )
        
        matched_assets = search_results['documents'][0]
        print(f"📦 检索到 {len(matched_assets)} 项潜在资产：{matched_assets}")

        # 步骤 2: 将检索到的资产数据喂给三路博弈引擎
        # 构造增强 Prompt：将真实资产数据作为上下文
        context_prompt = f"""
        User Goal: {user_query}
        Available Assets in Bank: {json.dumps(matched_assets)}
        Please audit if these assets can fulfill the request.
        """

        # 步骤 3: 触发三路并行博弈与仲裁
        print("🚀 正在启动三路模型进行资产对位审计...")
        await self.engine.execute_audit_workflow(context_prompt)
        
        duration = time.time() - start_time
        print(f"🏁 全链路处理完成，总耗时: {duration:.2f}s")

if __name__ == "__main__":
    pipeline = AMAHFullPipeline()
    # 模拟真实诉求
    test_query = "Need urgent high-precision DBS leads for a tremor patient in Florida."
    asyncio.run(pipeline.run_dispatch(test_query))
