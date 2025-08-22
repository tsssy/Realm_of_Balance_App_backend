#!/usr/bin/env python3
"""
测试AI服务的响应解析逻辑
"""

import asyncio
import json
from app.services.ai_service import GeminiInteractionAPI

async def test_ai_response_parsing():
    """测试AI响应解析逻辑"""
    print("🧪 测试AI服务响应解析")
    print("=" * 50)
    
    # 创建AI服务实例
    ai_service = GeminiInteractionAPI()
    
    # 测试简单的提示词
    test_prompt = "请输出：金=25, 木=15, 水=30, 火=20, 土=10"
    
    print(f"📝 测试提示词: {test_prompt}")
    print()
    
    try:
        # 调用AI服务
        print("🔄 调用AI服务...")
        result = await ai_service.send_message_to_ai(test_prompt)
        
        print(f"✅ 调用成功!")
        print(f"📊 结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get("success"):
            print(f"🎯 AI响应: {result.get('message', 'N/A')}")
        else:
            print(f"❌ 调用失败: {result.get('message', 'N/A')}")
            
    except Exception as e:
        print(f"💥 发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_response_parsing())
