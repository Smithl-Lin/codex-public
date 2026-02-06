import os
import json
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import ResourceExhausted, InternalServerError, ServiceUnavailable
from tqdm import tqdm

# ================= 配置区 =================
try:
    from config import get_gemini_api_key
    API_KEY = get_gemini_api_key()
except Exception:
    API_KEY = None
INPUT_DIR = "AMANI_Training_Data"
OUTPUT_FILE = "amani_finetuning_dataset.jsonl"

if API_KEY:
    genai.configure(api_key=API_KEY)

# 🔄 战略切换：使用 Lite 预览版，享有独立配额池
MODEL_NAME = "models/gemini-2.0-flash-lite-preview-02-05"

# 🛡️ 医疗安全豁免 (保持不拦截)
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

SYSTEM_PROMPT = """
You are A.M.A.N.I., an expert clinical resource coordinator.
Analyze the provided medical case abstract. Extract key information into the A.M.A.N.I. 4-Level Ontology.

OUTPUT SCHEMA (Strict JSON):
{
  "L1_Anchor": { "Diagnosis": "...", "Contraindications": "...", "Weight": 1.0 },
  "L2_Clinical": { "Symptoms": "...", "History": "...", "Trial_Criteria": "...", "Weight": 0.8 },
  "L3_Profile": { "Demographics": "...", "Financial_Proxy": "...", "Weight": 0.6 },
  "L4_Context": { "Preferences": "...", "Weight": 0.3 }
}
RULES: Output ONLY valid JSON. No markdown.
"""

def clean_json_string(json_str):
    json_str = json_str.strip()
    if json_str.startswith("```json"): json_str = json_str[7:]
    if json_str.startswith("```"): json_str = json_str[3:]
    if json_str.endswith("```"): json_str = json_str[:-3]
    return json_str.strip()

def process_case_with_retry(model, case_data):
    """带自动重试机制的处理函数"""
    abstract = case_data.get('abstract', '')
    if len(abstract) < 50: return None

    full_prompt = f"{SYSTEM_PROMPT}\n\nCASE ABSTRACT:\n{abstract}"
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 发送请求
            response = model.generate_content(
                full_prompt, 
                safety_settings=SAFETY_SETTINGS
            )
            
            cleaned_response = clean_json_string(response.text)
            structured_logic = json.loads(cleaned_response)
            
            return {
                "instruction": "Analyze this medical case and extract the A.M.A.N.I. 4-Level Ontology.",
                "input": abstract,
                "output": json.dumps(structured_logic, ensure_ascii=False)
            }

        except ResourceExhausted:
            # 🛑 遇到 429 超速，自动停车等待
            # 这里的等待时间较短，因为我们已经换了 Lite 模型
            wait_time = 30 + (retry_count * 10)
            tqdm.write(f"⏳ Quota Hit (429). Sleeping for {wait_time}s to cooldown...")
            time.sleep(wait_time)
            retry_count += 1
            
        except (InternalServerError, ServiceUnavailable):
            time.sleep(5)
            retry_count += 1
            
        except Exception as e:
            # 其他错误直接跳过
            return None
            
    return None

def main():
    print(f"=== A.M.A.N.I. Data Synthesizer V3.1 (Lite Edition) ===")
    print(f"🤖 Model: {MODEL_NAME}")
    print(f"🐢 Speed Limit: 10s delay (Maximum Safety Mode)")
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        print(f"❌ Error initializing model: {e}")
        return

    if not os.path.exists(INPUT_DIR): return
    
    # 1. 读取原始数据
    all_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('_training_set.json')]
    all_cases = []
    for f in all_files:
        try:
            with open(os.path.join(INPUT_DIR, f), 'r', encoding='utf-8') as file:
                all_cases.extend(json.load(file))
        except: continue
    
    # 2. 断点续传逻辑
    existing_outputs = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    existing_outputs.append(json.loads(line))
                except: continue
    
    processed_count = len(existing_outputs)
    print(f"📂 Total Raw Cases: {len(all_cases)}")
    print(f"♻️  Resuming from: {processed_count} (Already done)")
    
    cases_to_process = all_cases[processed_count:]
    
    if not cases_to_process:
        print("✅ All cases already processed!")
        return

    print(f"🚀 Starting synthesis for remaining {len(cases_to_process)} cases...")

    successful_this_run = 0
    
    # 追加模式 'a'
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as outfile:
        for case in tqdm(cases_to_process): 
            result = process_case_with_retry(model, case)
            
            if result:
                outfile.write(json.dumps(result, ensure_ascii=False) + '\n')
                outfile.flush() 
                successful_this_run += 1
            
            # 🛑 强制 10 秒延迟 - 这是核心修改
            time.sleep(10) 

    print("\n=============================================")
    print(f"✅ Synthesis Complete.")
    print(f"📊 New Added: {successful_this_run}")
    print(f"💾 Total Data: {processed_count + successful_this_run}")
    print("=============================================")

if __name__ == "__main__":
    main()