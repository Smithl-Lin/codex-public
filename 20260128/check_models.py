import google.generativeai as genai
import os

try:
    from config import get_gemini_api_key
    API_KEY = get_gemini_api_key()
except Exception:
    API_KEY = None
if API_KEY:
    genai.configure(api_key=API_KEY)

def list_available_models():
    print("=== Checking Available Gemini Models ===")
    try:
        count = 0
        for m in genai.list_models():
            # 只列出支持内容生成的模型 (generateContent)
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Found: {m.name}")
                count += 1
        
        if count == 0:
            print("❌ No models found supporting 'generateContent'.")
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_available_models()