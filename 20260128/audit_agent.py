# 文件名: audit_agent.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def run_graph_audit(patient_info, trial_data):
    """
    Mayo Clinic 专家级双轨审计引擎 (V20K 融资增强版)
    逻辑：1. 临床研究匹配审计 | 2. 高端长寿管理预防建议
    """
    target_api_key = os.getenv("OPENAI_API_KEY")
    if not target_api_key:
        return "🚨 **审计引擎离线**：请检查 API Key。"

    client = OpenAI(api_key=target_api_key)
    
    # 识别是否为 Mayo 内部资产及分类
    is_mayo = "Mayo Clinic" in str(trial_data)
    is_wellness = "Wellness" in str(trial_data) or "Executive" in str(trial_data)
    
    mayo_bonus = """
    【💡 Mayo 内部绿色通道已激活】: 
    检测到该资产为 Mayo Clinic 官方项目。作为内部研究员 Smith Lin，您可协助客户通过内部系统获取更深度的专家解读及快速预约。
    """ if is_mayo else ""

    system_prompt = f"""
    你是一名在 Mayo Clinic 工作的顶级医学与长寿管理专家。
    你正在为全球高净值客户（HNWIs）执行【资产调度审计】。
    
    【你的双重职责】:
    1. 若为临床研究：核对 BCI/iPS 技术层级，严防“降级匹配”及跨学科偏离。
    2. 若为高端体检：评估美国特色资源（Grail 液态活检、AI MRI）相对于客户当地资源的“非对称优势”。
    {mayo_bonus}
    """

    user_prompt = f"""
    【客户/患者画像】: {patient_info}
    【匹配的全球医疗资产】: {trial_data}

    请按以下结构输出审计结论：
    # 🩺 AI 专家战略审计报告 (Mayo Internal Reference)

    ## 1. 资源对位校验
    - **技术/项目属性**: (判断是治疗研究还是高端预防)
    - **核心对位精度**: (分析 0.79 距离下的匹配质量)

    ## 2. 战略风险与价值评估
    - **风险拦截**: (识别年龄、既往史冲突，拦截 ICU 误匹配)
    - **美式资源增益**: (若为体检，分析美方资源如全基因组测序、液态活检的“黄金标准”验证价值)

    ## 3. 最终调度建议
    - **结论**: 【强烈推荐】/【谨慎考虑】/【匹配拒绝】
    - **专家路径建议**: (提供赴美复查或入组的具体行动点)
    
    {mayo_bonus}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 审计异常: {str(e)}"