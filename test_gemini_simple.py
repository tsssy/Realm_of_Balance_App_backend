#!/usr/bin/env python3
"""
简单测试 Gemini API 连接
"""

import asyncio
import aiohttp
import json

async def test_gemini_simple():
    """简单测试 Gemini API"""
    try:
        # 使用用户提供的新 API 密钥
        api_key = "AIzaSyABUujxgPVKWsPmpOmPP4Fa2K56XbBdslw"
        
        print("🧪 开始测试 Gemini API 连接")
        print("=" * 50)
        
        # 尝试不同的模型
        models = [
            "gemini-pro",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]
        
        for model in models:
            print(f"\n🔍 测试模型: {model}")
            
            # 构建请求
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
            # 简单的测试消息
            data = {
                "contents": [{
                    "parts": [{
                        "text": "hello"
                    }]
                }]
            }
            
            print(f"📤 发送请求到: {url}")
            
            # 设置更短的超时
            timeout = aiohttp.ClientTimeout(total=10)
            
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, json=data) as response:
                        print(f"📥 响应状态码: {response.status}")
                        
                        if response.status == 200:
                            result = await response.json()
                            print("✅ API 调用成功!")
                            print(f"📄 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                            return  # 成功就退出
                        else:
                            error_text = await response.text()
                            print(f"❌ API 调用失败: {error_text}")
                            
            except asyncio.TimeoutError:
                print(f"⏰ {model} 请求超时")
            except Exception as e:
                print(f"❌ {model} 测试失败: {e}")
        
        print("\n❌ 所有模型都测试失败")
                    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_simple())
