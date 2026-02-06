import google.generativeai as genai
import os
import json

# ================= 诊断配置 (from config / .env) =================
try:
    from config import get_gemini_api_key
    API_KEY = get_gemini_api_key()
except Exception:
    API_KEY = None
INPUT_DIR = "AMANI_Training_Data"

if API_KEY:
    genai.configure(api_key=API_KEY)

# ================= 诊断逻辑 =================
def run_diagnostic():
    print("=== A.M.A.N.I. Diagnostic Mode ===")
    print(f"🔑 Testing with Key: {API_KEY[:5]}...{API_KEY[-4:]}" if API_KEY else "🔑 No GEMINI_API_KEY set in .env")
    
    # 1. 检查数据文件
    if not os.path.exists(INPUT_DIR):
        print(f"❌ CRITICAL: Directory '{INPUT_DIR}' does not exist.")
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('_training_set.json')]
    if not files:
        print(f"❌ CRITICAL: No data files found in {INPUT_DIR}")
        return
    else:
        print(f"✅ Files found: {len(files)} JSON files.")

    # 2. 读取样本数据
    first_file = os.path.join(INPUT_DIR, files[0])
    try:
        with open(first_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                print("❌ CRITICAL: JSON file is empty.")
                return
            sample_case = data[0]
            print(f"✅ Sample case loaded. PMID: {sample_case.get('pmid')}")
            print(f"   Abstract length: {len(sample_case.get('abstract', ''))} chars")
    except Exception as e:
        print(f"❌ CRITICAL: Error reading file: {e}")
        return

    # 3. 测试 API 连接 (Hello World)
    print("\n>>> Test 1: Basic API Connectivity...")
    try:
        # 尝试标准模型名称
        model = genai.GenerativeModel('gemini-1.5-flash') 
        response = model.generate_content("Say 'Hello A.M.A.N.I.' if you can hear me.")
        print(f"✅ Connection Success! Response: {response.text.strip()}")
    except Exception as e:
        print(f"❌ Connection FAILED.")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {e}")
        return

    # 4. 测试医疗内容生成 (安全过滤器测试)
    print("\n>>> Test 2: Medical Content Processing (Safety Filters)...")
    try:
        # 使用样本摘要的前 300 个字符进行测试
        test_abstract = sample_case.get('abstract', '')[:300]
        prompt = f"Extract medical entities from this text: {test_abstract}"
        
        response = model.generate_content(prompt)
        
        # 检查是否被阻挡
        if response.prompt_feedback:
            # 如果存在 feedback，检查是否有 block_reason
            block_reason = response.prompt_feedback.block_reason
            if block_reason:
                print(f"⚠️ BLOCKED. Reason: {block_reason}")
                print(f"   Safety Ratings: {response.prompt_feedback.safety_ratings}")
            else:
                # 尝试获取文本
                try:
                    print(f"✅ Medical Processing Success! Output preview: {response.text[:50]}...")
                except ValueError:
                    print("❌ Response blocked by safety filters (No text returned).")
                    print(f"   Safety Ratings: {response.prompt_feedback.safety_ratings}")
        else:
             print(f"✅ Medical Processing Success! Output preview: {response.text[:50]}...")

    except Exception as e:
        print(f"❌ Medical Processing Error: {e}")

if __name__ == "__main__":
    run_diagnostic()