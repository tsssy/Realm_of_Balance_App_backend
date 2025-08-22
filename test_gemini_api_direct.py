#!/usr/bin/env python3
"""
直接调用Gemini API测试
"""

import asyncio
from app.services.ai_service import GeminiInteractionAPI

async def test_gemini_api_direct():
    """直接测试Gemini API"""
    try:
        print("🧪 直接测试Gemini API")
        print("=" * 50)
        
        # 创建Gemini API实例
        gemini_api = GeminiInteractionAPI()
        
        # 简单的测试提示词
        simple_prompt = """请严格按照以下JSON格式输出：

```json
{
  "test": "这是一个测试",
  "status": "success"
}
```

只输出JSON，不要其他内容。"""
        
        print("发送简单测试提示词...")
        response = await gemini_api.send_message_to_ai(simple_prompt)
        
        print(f"响应状态: {response.get('success')}")
        print(f"响应消息: {response.get('message', 'N/A')}")
        
        if response.get('success'):
            message = response.get('message', '')
            print(f"消息长度: {len(message)}")
            print(f"消息内容: {message}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_api_direct())
