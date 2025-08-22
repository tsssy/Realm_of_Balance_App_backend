#!/usr/bin/env python3
"""
分层架构蓝图生成测试脚本
测试快速五行计算和完整蓝图生成功能
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# API配置
API_BASE_URL = "http://localhost:8000"

# 测试用户数据
TEST_USER_DATA = {
    "device_id": f"test-device-layered-{int(time.time())}",
    "profile": {
        "gender": "male",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "birth_location": "北京"
    }
}

async def test_layered_blueprint():
    """测试分层架构蓝图生成"""
    print("🧪 分层架构蓝图生成测试")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 创建测试用户
            print("📝 步骤1: 创建测试用户...")
            create_user_response = await session.post(
                f"{API_BASE_URL}/api/v1/user/create",
                json=TEST_USER_DATA
            )
            
            if create_user_response.status != 200:
                print(f"❌ 创建用户失败: {create_user_response.status}")
                error_text = await create_user_response.text()
                print(f"错误详情: {error_text}")
                return
            
            user_data = await create_user_response.json()
            print(f"用户创建响应: {json.dumps(user_data, ensure_ascii=False, indent=2)}")
            
            if "user_id" in user_data:
                user_id = user_data["user_id"]
            elif "data" in user_data and "user_id" in user_data["data"]:
                user_id = user_data["data"]["user_id"]
            else:
                print("❌ 无法获取用户ID，响应结构异常")
                return
            
            print(f"✅ 用户创建成功: {user_id}")
            print()
            
            # 2. 测试快速五行计算
            print("🔮 步骤2: 测试快速五行计算...")
            print("📊 预期：5-8秒内返回五行结果，状态为 partial")
            print()
            
            quick_request = {
                "user_id": user_id,
                "user_profile": TEST_USER_DATA["profile"]
            }
            
            start_time = time.time()
            print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
            
            quick_response = await session.post(
                f"{API_BASE_URL}/api/v1/blueprint/quick",
                json=quick_request
            )
            
            end_time = time.time()
            quick_time = end_time - start_time
            
            print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")
            print(f"⏱️  快速计算耗时: {quick_time:.2f}秒")
            
            if quick_response.status == 200:
                print("✅ 快速五行计算成功!")
                quick_data = await quick_response.json()
                print(f"📊 响应数据: {json.dumps(quick_data, ensure_ascii=False, indent=2)}")
                
                # 检查数据结构
                if "data" in quick_data:
                    blueprint_data = quick_data["data"]
                    print(f"🔍 数据检查:")
                    print(f"   - 生成状态: {blueprint_data.get('generation_status', 'N/A')}")
                    print(f"   - 任务ID: {blueprint_data.get('task_id', 'N/A')}")
                    print(f"   - 五行数据: {'✅' if blueprint_data.get('quick_data') else '❌'}")
                    print(f"   - 完整蓝图: {'✅' if blueprint_data.get('inner_blueprint') else '❌'}")
            else:
                print(f"❌ 快速五行计算失败: {quick_response.status}")
                error_text = await quick_response.text()
                print(f"错误详情: {error_text}")
                return
            
            print()
            
            # 3. 检查状态
            print("📊 步骤3: 检查生成状态...")
            status_response = await session.get(f"{API_BASE_URL}/api/v1/blueprint/{user_id}/status")
            
            if status_response.status == 200:
                status_data = await status_response.json()
                print(f"📊 状态信息: {json.dumps(status_data, ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ 状态查询失败: {status_response.status}")
            
            print()
            
            # 4. 测试完整蓝图生成
            print("🔮 步骤4: 测试完整蓝图生成...")
            print("📊 预期：基于五行结果生成完整内容，状态变为 complete")
            print()
            
            complete_request = {
                "user_id": user_id,
                "user_profile": TEST_USER_DATA["profile"]
            }
            
            start_time = time.time()
            print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
            
            complete_response = await session.post(
                f"{API_BASE_URL}/api/v1/blueprint/complete",
                json=complete_request
            )
            
            end_time = time.time()
            complete_time = end_time - start_time
            
            print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")
            print(f"⏱️  完整生成耗时: {complete_time:.2f}秒")
            
            if complete_response.status == 200:
                print("✅ 完整蓝图生成成功!")
                complete_data = await complete_response.json()
                print(f"📊 响应数据: {json.dumps(complete_data, ensure_ascii=False, indent=2)}")
                
                # 检查数据结构
                if "data" in complete_data:
                    blueprint_data = complete_data["data"]
                    print(f"🔍 数据检查:")
                    print(f"   - 生成状态: {blueprint_data.get('generation_status', 'N/A')}")
                    print(f"   - 任务ID: {blueprint_data.get('task_id', 'N/A')}")
                    print(f"   - 五行数据: {'✅' if blueprint_data.get('quick_data') else '❌'}")
                    print(f"   - 完整蓝图: {'✅' if blueprint_data.get('inner_blueprint') else '❌'}")
            else:
                print(f"❌ 完整蓝图生成失败: {complete_response.status}")
                error_text = await complete_response.text()
                print(f"错误详情: {error_text}")
            
            print()
            
            # 5. 最终状态检查
            print("📊 步骤5: 最终状态检查...")
            final_status_response = await session.get(f"{API_BASE_URL}/api/v1/blueprint/{user_id}/status")
            
            if final_status_response.status == 200:
                final_status_data = await final_status_response.json()
                print(f"📊 最终状态: {json.dumps(final_status_data, ensure_ascii=False, indent=2)}")
            else:
                print(f"❌ 最终状态查询失败: {final_status_response.status}")
            
            print()
            
            # 6. 检查数据库状态（清理前）
            print("🔍 步骤6: 检查数据库状态...")
            try:
                # 再次获取蓝图数据，确认数据库中的状态
                final_blueprint_response = await session.get(f"{API_BASE_URL}/api/v1/blueprint/{user_id}")
                if final_blueprint_response.status == 200:
                    final_blueprint_data = await final_blueprint_response.json()
                    print("📊 数据库中的最终蓝图数据:")
                    print(f"   - 记录ID: {final_blueprint_data.get('data', {}).get('_id', 'N/A')}")
                    print(f"   - 生成状态: {final_blueprint_data.get('data', {}).get('generation_status', 'N/A')}")
                    print(f"   - 五行数据: {'✅' if final_blueprint_data.get('data', {}).get('quick_data') else '❌'}")
                    print(f"   - 完整蓝图: {'✅' if final_blueprint_data.get('data', {}).get('inner_blueprint') else '❌'}")
                    print(f"   - 创建时间: {final_blueprint_data.get('data', {}).get('created_at', 'N/A')}")
                    print(f"   - 更新时间: {final_blueprint_data.get('data', {}).get('updated_at', 'N/A')}")
                else:
                    print(f"❌ 最终蓝图查询失败: {final_blueprint_response.status}")
            except Exception as e:
                print(f"⚠️  数据库状态检查失败: {e}")
            
            print()
            
            # 7. 清理测试数据
            print("🧹 步骤7: 清理测试数据...")
            try:
                await session.delete(f"{API_BASE_URL}/api/v1/user/{user_id}")
                print("✅ 测试数据清理完成")
            except Exception as e:
                print(f"⚠️  数据清理失败: {e}")
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """主函数"""
    print("🧪 分层架构蓝图生成测试工具")
    print("=" * 60)
    print("📋 测试说明:")
    print("   - 测试快速五行计算API")
    print("   - 测试完整蓝图生成API")
    print("   - 验证数据状态管理")
    print("   - 检查缓存一致性")
    print("=" * 60)
    
    await test_layered_blueprint()
    
    print("=" * 60)
    print("🏁 测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
