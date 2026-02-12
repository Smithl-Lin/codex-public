import asyncio
import json
import time
import logging
from trinity_api_connector import AMAHWeightedEngine
from billing_engine import AMAHBillingEngine
import chromadb

logger = logging.getLogger(__name__)

class AMAHUnifiedSynergy:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./amah_vector_db")
        self.engine = AMAHWeightedEngine()
        self.billing = AMAHBillingEngine()
        
        # 挂载核心分片
        self.assets = self.client.get_collection("neurology_assets")
        self.experts = self.client.get_collection("expert_map_global")
        print("✅ AMAH V10.0 全链路商业闭环引擎已激活")

    async def execute_strategic_matching(self, user_query):
        start_time = time.time()
        safe_query = user_query
        try:
            from privacy_guard import redact_text
            safe_query, redaction_stats = redact_text(str(user_query))
            if any(redaction_stats.values()):
                logger.info("Outbound payload redacted for unified_synergy: %s", redaction_stats)
        except Exception:
            safe_query = user_query
        user_query = safe_query
        print(f"\n📢 处理高精诉求: {user_query}")
        
        # 1. 资产与专家双重检索 (HNSW 0.79 精度保障)
        asset_res = self.assets.query(query_texts=[safe_query], n_results=1)
        matched_asset = asset_res['documents'][0][0]
        
        expert_query = f"{safe_query} using {matched_asset}"
        expert_res = self.experts.query(query_texts=[expert_query], n_results=1)
        
        matched_expert_doc = expert_res['documents'][0][0]
        expert_meta = expert_res['metadatas'][0][0]
        
        # 2. 三路博弈审计 (战略延续性验证)
        audit_context = f"Goal: {safe_query} | Asset: {matched_asset} | Expert: {matched_expert_doc}"
        score, var, mode = await self.engine.execute_audit_workflow(audit_context)
        
        # 3. 商业计费自动生成
        # 从专家元数据提取增值服务标签
        services = json.loads(expert_meta.get('services', '[]'))
        quote = self.billing.generate_quote(score, mode, services)
        
        # 4. 最终展示
        duration = time.time() - start_time
        self.billing.print_invoice_demo(quote)
        
        print(f"🏁 全链路处理完成 | 耗时: {duration:.2f}s")
        return quote

if __name__ == "__main__":
    pipeline = AMAHUnifiedSynergy()
    # 模拟一个涉及 DBS 植入的复杂诉求
    query = "Urgent high-precision DBS lead placement for Parkinson patient, Florida, Medicare coverage required."
    asyncio.run(pipeline.execute_strategic_matching(query))
