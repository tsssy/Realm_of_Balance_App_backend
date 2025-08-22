#!/usr/bin/env python3
"""
调试Heart Compass服务
"""

import asyncio
import aiohttp
import json

API_BASE_URL = "http://localhost:8000"

async def test_heart_compass_debug():
    """调试Heart Compass服务"""
    async with aiohttp.ClientSession() as session:
        try:
            # 创建测试用户
            print("📝 创建测试用户...")
            test_user = {
                "device_id": f"debug-hc-{int(asyncio.get_event_loop().time())}",
                "profile": {
                    "gender": "male",
                    "birth_date": "1990-01-01",
                    "birth_time": "12:00",
                    "birth_location": "北京"
                }
            }
            
            resp = await session.post(f"{API_BASE_URL}/api/v1/user/create", json=test_user)
            if resp.status != 200:
                print(f"❌ 创建用户失败: {resp.status}")
                return
                
            u = await resp.json()
            user_id = u.get("user_id") or (u.get("data") or {}).get("user_id")
            print(f"✅ 用户创建成功: {user_id}")
            
            # 测试Heart Compass
            print("\n🧭 测试Heart Compass...")
            hc_payload = {
                "user_id": user_id,
                "question": "我是否应该换工作？",
                "user_profile": test_user["profile"]
            }
            
            print("发送请求...")
            hc_resp = await session.post(f"{API_BASE_URL}/api/v1/heart-compass/seek-guidance", json=hc_payload)
            print(f"状态: {hc_resp.status}")
            
            if hc_resp.status == 200:
                hc_json = await hc_resp.json()
                print("✅ Heart Compass 成功")
                print("响应数据结构:")
                print(f"  success: {hc_json.get('success')}")
                print(f"  data: {type(hc_json.get('data'))}")
                if 'data' in hc_json:
                    data = hc_json['data']
                    print(f"  data.hexagram.name: {data.get('hexagram', {}).get('name', 'N/A')}")
                    print(f"  data.ai_generated: {data.get('ai_generated', 'N/A')[:100]}...")
                
            else:
                print(f"❌ Heart Compass 失败: {await hc_resp.text()}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_heart_compass_debug())
