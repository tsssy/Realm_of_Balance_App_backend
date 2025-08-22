#!/usr/bin/env python3
"""
Heart Compass & Daily Fortune 性能测试脚本
- 创建用户
- 调用 Heart Compass 指导（/heart-compass/seek）并记录耗时
- 调用 Daily Fortune 生成（/daily-fortune/generate）并记录耗时
- 清理用户
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

TEST_USER = {
    "device_id": f"perf-hc-df-{int(time.time())}",
    "profile": {
        "gender": "male",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "birth_location": "北京"
    }
}

async def run_once():
    async with aiohttp.ClientSession() as session:
        try:
            # 1) 创建用户
            print("📝 创建测试用户...")
            resp = await session.post(f"{API_BASE_URL}/api/v1/user/create", json=TEST_USER)
            if resp.status != 200:
                print(f"❌ 创建用户失败: {resp.status}")
                print(await resp.text())
                return
            u = await resp.json()
            user_id = u.get("user_id") or (u.get("data") or {}).get("user_id")
            if not user_id:
                print("❌ 无法获取用户ID")
                return
            print(f"✅ 用户创建成功: {user_id}")
            
            # 2) Heart Compass 指导
            print("\n🧭 Heart Compass 指导测试...")
            hc_payload = {
                "user_id": user_id,
                "question": "我是否应该换工作？",
                "user_profile": TEST_USER["profile"]
            }
            t0 = time.time();
            hc_resp = await session.post(f"{API_BASE_URL}/api/v1/heart-compass/seek-guidance", json=hc_payload)
            t1 = time.time();
            print(f"⏱️ Heart Compass 耗时: {t1 - t0:.2f}秒, 状态: {hc_resp.status}")
            if hc_resp.status == 200:
                hc_json = await hc_resp.json()
                print(f"📊 Heart Compass 响应: {json.dumps(hc_json, ensure_ascii=False)[:300]}...")
            else:
                print(f"❌ Heart Compass 失败: {await hc_resp.text()}")
            
            # 3) Daily Fortune 生成
            print("\n📅 Daily Fortune 生成测试...")
            df_payload = {
                "user_id": user_id,
                "user_profile": TEST_USER["profile"]
            }
            t0 = time.time();
            df_resp = await session.post(f"{API_BASE_URL}/api/v1/daily-fortune/generate", json=df_payload)
            t1 = time.time();
            print(f"⏱️ Daily Fortune 耗时: {t1 - t0:.2f}秒, 状态: {df_resp.status}")
            if df_resp.status == 200:
                df_json = await df_resp.json()
                print(f"📊 Daily Fortune 响应: {json.dumps(df_json, ensure_ascii=False)[:300]}...")
            else:
                print(f"❌ Daily Fortune 失败: {await df_resp.text()}")
            
            # 4) 清理
            print("\n🧹 清理测试数据...")
            # 注释掉清理，保留数据用于检查
            # await session.delete(f"{API_BASE_URL}/api/v1/user/{user_id}")
            print("✅ 数据保留，用于检查")
        except Exception as e:
            print("❌ 测试过程中发生异常:", e)
            import traceback; traceback.print_exc()

async def main():
    print("🧪 Heart Compass & Daily Fortune 性能测试")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    await run_once()
    print(f"结束时间: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
