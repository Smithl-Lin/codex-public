import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
import json
import traceback # 引入堆栈追踪工具

# ================= 配置区 =================
try:
    from config import get_gemini_api_key
    API_KEY = get_gemini_api_key()
except Exception:
    API_KEY = None
INPUT_DIR = "AMANI_Training_Data"

if API_KEY:
    genai.configure(api_key=API_KEY)
# 我们先测试您环境里有的这个最新模型
MODEL_NAME = "models/gemini-2.5-flash"

# ================= 安全设置 (复现刚才的环境) =================
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def forensic_analysis():
    print(f"=== A.M.A.N.I. Forensic Analysis (Target: {MODEL_NAME}) ===")
    
    # 1. 提取尸体 (获取第一个病例数据)
    if not os.path.exists(INPUT_DIR):
        print("❌ Data directory missing.")
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('_training_set.json')]
    if not files:
        print("❌ No data files found.")
        return

    first_file = os.path.join(INPUT_DIR, files[0])
    with open(first_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        case = data[0] # 取第一个
    
    print(f"🔎 Analyzed Case ID: {case.get('pmid', 'Unknown')}")
    print(f"📝 Abstract Length: {len(case.get('abstract', ''))} chars")
    
    # 2. 模拟手术 (调用 API)
    print("\n>>> Attempting Generation with verbose error logging...")
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # 这是一个简化的 Prompt，只为了测试能不能通
        prompt = f"Extract medical entities from this text: {case.get('abstract')[:500]}"
        
        print("    Sending request to Google...")
        response = model.generate_content(
            prompt,
            safety_settings=SAFETY_SETTINGS
        )
        
        # 3. 检查生命体征
        print("\n✅ SUCCESS! The API is working. Here is the raw response:")
        print("-" * 20)
        print(response.text)
        print("-" * 20)
        
    except Exception:
        print("\n❌ FATAL ERROR DETECTED!")
        print("This is the exact reason why your 1200 cases failed:")
        print("=" * 40)
        # 打印完整的错误堆栈，这才是真相
        traceback.print_exc()
        print("=" * 40)
        
        # 4. 尝试备用方案 (如果 2.5 挂了，试试 2.0)
        print("\n>>> Trying fallback model: models/gemini-2.0-flash-lite-preview-02-05 ...")
        try:
            fallback_model = genai.GenerativeModel("models/gemini-2.0-flash-lite-preview-02-05")
            res = fallback_model.generate_content("Hello")
            print(f"✅ Fallback Model Works! Response: {res.text}")
        except:
            print("❌ Fallback Model also failed.")

if __name__ == "__main__":
    forensic_analysis()