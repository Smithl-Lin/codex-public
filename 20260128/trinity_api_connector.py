import os
import asyncio
import numpy as np
import re
import json
import time
import logging
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class AMAHWeightedEngine:
    def __init__(self):
        # 权重设置：强调准确性，Gemini 和 Claude 负责核心医学逻辑
        self.BASE_WEIGHTS = {"gpt": 0.2, "gemini": 0.4, "claude": 0.4}
        self.project_id = "amah-medical-ai"
        self.location = "global"
        try:
            from config import get_google_credentials_path
            key_path = get_google_credentials_path() or os.path.join(os.path.dirname(__file__), "google_key.json")
        except Exception:
            key_path = os.path.join(os.path.dirname(__file__), "google_key.json")
        if os.path.isfile(key_path):
            credentials = service_account.Credentials.from_service_account_file(key_path)
            vertexai.init(project=self.project_id, location=self.location, credentials=credentials)
        else:
            vertexai.init(project=self.project_id, location=self.location)
        
        self.gemini_model = GenerativeModel("gemini-3-pro-preview")
        self.claude_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def clip_value(self, val):
        try: return max(0.0, min(1.0, float(val)))
        except Exception:
            return 0.5

    async def get_model_logic(self, model_type, context):
        """V8.0: 引入临床全路径审计与‘一票否决’逻辑"""
        try:
            from privacy_guard import redact_text
            safe_context, redaction_stats = redact_text(str(context))
            if any(redaction_stats.values()):
                logger.info("Outbound payload redacted for %s: %s", model_type, redaction_stats)
        except Exception:
            safe_context = context
        prompt = f"""
        [AMAH STRATEGIC AUDIT - PRIORITY: ACCURACY]
        Task: {safe_context}
        
        You are a senior medical expert. Audit the asset redistribution following this STRICT sequence:
        1. DIAGNOSIS MATCH: Does the asset align with the primary diagnosis?
        2. TREATMENT PRINCIPLES: Is it consistent with international clinical guidelines?
        3. FRONTIER CHECK: Evaluate against the latest clinical trials, FDA-approved drugs, and new medical devices.
        4. EXPERT SYNERGY: Can this be executed by top-tier specialists from the Expert Map?
        5. FINAL ALIGNMENT: Does the matched outcome fulfill the user's core request?
        
        [VETO RULE]: If ANY step fails or is mismatched, the 'score' MUST be < 0.3.
        Return ONLY JSON: {{'score': float, 'certainty': float, 'pathway': 'validated'|'rejected', 'reasoning': str}}
        """
        try:
            if model_type == "gemini":
                res = await self.gemini_model.generate_content_async(prompt)
                return self.parse_json(res.text)
            elif model_type == "claude":
                res = await self.claude_client.messages.create(
                    model="claude-sonnet-4-5", max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                return self.parse_json(res.content[0].text)
            elif model_type == "gpt":
                res = await self.openai_client.chat.completions.create(
                    model="gpt-4o", messages=[{"role": "user", "content": prompt}]
                )
                return self.parse_json(res.choices[0].message.content)
        except Exception as e:
            logger.warning("Model logic call failed for %s: %s", model_type, e)
            return {"score": None, "certainty": 0, "pathway": "error", "reasoning": "Connection lost"}

    def parse_json(self, text):
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            data = json.loads(match.group().replace("'", '"'))
            data['score'] = self.clip_value(data.get('score', 0.5))
            return data
        except Exception as e:
            logger.warning("Model output parse failed: %s", e)
            return {"score": None, "certainty": 0, "pathway": "parse_fail", "reasoning": "Output Error"}

    async def calculate_weighted_consensus(self, results_dict):
        valid_models = {k: v for k, v in results_dict.items() if v['score'] is not None}
        count = len(valid_models)
        
        if count < 2: return None, 1.0, "INSUFFICIENT_NODES", {}

        # 核心修正：一票否决权检查
        # 如果任何高权重节点判定为 'rejected'，强制整体拦截
        for m, res in valid_models.items():
            if res['score'] < 0.3:
                return 0.1, 0.0, "STRATEGIC_VETO", valid_models

        norm_w = {m: self.BASE_WEIGHTS[m]/sum(self.BASE_WEIGHTS[k] for k in valid_models) for m in valid_models}
        score = sum(valid_models[m]['score'] * norm_w[m] * valid_models[m]['certainty'] for m in valid_models) / \
                sum(norm_w[m] * valid_models[m]['certainty'] for m in valid_models)
        var = float(np.var([v['score'] for v in valid_models.values()]))
        
        return score, var, "TRINITY_STABLE", valid_models

    async def execute_audit_workflow(self, request):
        print(f"🚀 [AMAH 精准审计] 优先级：匹配准确性...")
        tasks = {m: asyncio.wait_for(self.get_model_logic(m, request), timeout=12.0) for m in ["gpt", "gemini", "claude"]}
        try:
            results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
            results_dict = {m: r if not isinstance(r, Exception) else {"score": None} for m, r in zip(tasks.keys(), results_list)}
            
            score, var, mode, nodes = await self.calculate_weighted_consensus(results_dict)
            
            print("="*60)
            if mode == "STRATEGIC_VETO":
                print("🚫 [战略拦截] 方案与临床原则或患者诉求不匹配，已重置方案。")
            elif score and score > 0.8:
                print(f"✅ [高精对位] 聚合得分: {score:.4f} | 方案已锁定。")
            else:
                print("⚠️ [匹配度不足] 建议回退至患者诉求层级重新分析。")
            print("="*60)
            return score, var, mode
        except Exception as e:
            print(f"🛑 系统异常: {e}")
            return None, 1.0, "CRITICAL_ERROR"

if __name__ == "__main__":
    engine = AMAHWeightedEngine()
    asyncio.run(engine.execute_audit_workflow("High-precision DBS Leads audit for STN surgery."))
