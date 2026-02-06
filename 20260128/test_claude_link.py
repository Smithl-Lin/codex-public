import os
import asyncio
from anthropic import AsyncAnthropic

async def test_link():
    # 强制重新读取环境变量
    api_key = os.getenv("ANTHROPIC_API_KEY")
    print(f"📡 正在检测密钥前缀: {api_key[:10] if api_key else 'None'}...")
    
    client = AsyncAnthropic(api_key=api_key)
    try:
        # 使用 2026 年 1 月的最新旗舰模型标识符
        message = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=10,
            messages=[{"role": "user", "content": "Ping"}]
        )
        print(f"✅ Claude 4.5 响应成功: {message.content[0].text}")
    except Exception as e:
        print(f"❌ 物理连接依然失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_link())
