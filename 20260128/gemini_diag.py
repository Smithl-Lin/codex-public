import os
import asyncio
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

async def diagnose_connection():
    project_id = "amah-medical-ai"
    location = "global"
    try:
        from config import get_google_credentials_path
        key_path = get_google_credentials_path() or os.path.join(os.path.dirname(__file__), "google_key.json")
    except Exception:
        key_path = os.path.join(os.path.dirname(__file__), "google_key.json")
    print(f"🚀 [AMAH 诊断] 启动全球算力对位测试...")
    try:
        if not os.path.isfile(key_path):
            print(f"❌ 错误：物理钥匙文件 {key_path} 不存在。请设置 GOOGLE_APPLICATION_CREDENTIALS 或放置 google_key.json。")
            return
        credentials = service_account.Credentials.from_service_account_file(key_path)
        # 初始化锁定 global 逻辑端点
        vertexai.init(project=project_id, location=location, credentials=credentials)
        
        # 锁定截图中显示的 2026 旗舰 ID
        model = GenerativeModel("gemini-3-pro-preview")
        
        print(f"📡 正在向全球网关发起握手信号...")
        response = await model.generate_content_async("Handshake ACK.")
        
        print("=" * 40)
        print(f"✅ 物理连接成功！")
        print(f"📦 节点响应: {response.text}")
        print("=" * 40)
    except Exception as e:
        print(f"🛑 物理连接依然受阻。错误详情: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_connection())
