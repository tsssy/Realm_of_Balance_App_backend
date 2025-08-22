#!/usr/bin/env python3
"""
测试修改后的蓝图生成接口性能
去掉生命曲线部分后的响应时间测试
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime

# 测试配置
API_BASE_URL = "http://localhost:8000"
import uuid

# 生成唯一的设备ID
unique_device_id = f"test-device-{uuid.uuid4().hex[:8]}"
TEST_USER_DATA = {
    "device_id": unique_device_id,
    "profile": {
        "gender": "male",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "birth_location": "北京"
    }
}

async def test_blueprint_performance():
    """测试蓝图生成性能"""
    print("🚀 开始测试修改后的蓝图生成接口性能")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 创建测试用户
            print("📝 步骤1: 创建测试用户...")
            start_time = time.time()
            
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
            
            # 检查响应结构
            if "user_id" in user_data:
                user_id = user_data["user_id"]
            elif "data" in user_data and "user_id" in user_data["data"]:
                user_id = user_data["data"]["user_id"]
            else:
                print("❌ 无法获取用户ID，响应结构异常")
                return
            create_time = time.time() - start_time
            
            print(f"✅ 用户创建成功: {user_id}")
            print(f"⏱️  用户创建耗时: {create_time:.2f}秒")
            print()
            
            # 2. 测试蓝图生成性能
            print("🔮 步骤2: 测试蓝图生成性能...")
            print("📊 当前提示词已简化，去掉生命曲线部分，预期响应时间会减少")
            print()
            
            # 准备蓝图生成请求
            blueprint_request = {
                "user_id": user_id,
                "user_profile": TEST_USER_DATA
            }
            
            # 开始计时
            start_time = time.time()
            print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
            
            # 发送蓝图生成请求
            blueprint_response = await session.post(
                f"{API_BASE_URL}/api/v1/blueprint/generate",
                json=blueprint_request
            )
            
            # 结束计时
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")
            print(f"⏱️  总耗时: {total_time:.2f}秒")
            
            # 检查响应状态
            if blueprint_response.status == 200:
                print("✅ 蓝图生成成功!")
                
                # 获取响应数据
                response_data = await blueprint_response.json()
                
                # 分析响应内容
                if "data" in response_data:
                    blueprint_data = response_data["data"]
                    
                    # 检查是否包含生命曲线数据
                    has_life_curve = "life_journey_curve" in blueprint_data
                    has_core_energy = "core_energy_field" in blueprint_data
                    
                    print(f"📊 响应内容分析:")
                    print(f"   - 包含核心能量场: {'✅' if has_core_energy else '❌'}")
                    print(f"   - 包含生命曲线: {'✅' if has_life_curve else '❌'}")
                    
                    if has_core_energy:
                        core_energy = blueprint_data["core_energy_field"]
                        if "chart_data" in core_energy:
                            chart_data = core_energy["chart_data"]
                            print(f"   - 五行数据点数: {len(chart_data)}")
                    
                    # 计算响应大小
                    response_size = len(json.dumps(response_data, ensure_ascii=False))
                    print(f"   - 响应数据大小: {response_size} 字符")
                    
            else:
                print(f"❌ 蓝图生成失败: {blueprint_response.status}")
                error_text = await blueprint_response.text()
                print(f"错误详情: {error_text}")
            
            print()
            
            # 3. 性能分析
            print("📈 性能分析:")
            if total_time < 10:
                print(f"🎉 优秀! 响应时间: {total_time:.2f}秒 (预期: <10秒)")
            elif total_time < 20:
                print(f"👍 良好! 响应时间: {total_time:.2f}秒 (预期: <20秒)")
            elif total_time < 30:
                print(f"⚠️  一般! 响应时间: {total_time:.2f}秒 (预期: <30秒)")
            else:
                print(f"❌ 较慢! 响应时间: {total_time:.2f}秒 (预期: <30秒)")
            
            print()
            print("💡 优化建议:")
            if total_time > 20:
                print("   - 考虑进一步简化AI提示词")
                print("   - 检查AI服务响应时间")
                print("   - 优化数据库查询")
            else:
                print("   - 性能已达到可接受范围")
                print("   - 可以考虑添加更多功能")
            
            # 4. 清理测试数据
            print("🧹 步骤3: 清理测试数据...")
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
    print("🔮 蓝图生成性能测试工具")
    print("=" * 60)
    print("📋 测试说明:")
    print("   - 测试蓝图生成接口性能")
    print("   - 当前提示词已简化，去掉生命曲线部分")
    print("   - 测试简化后的性能表现")
    print("=" * 60)
    
    await test_blueprint_performance()
    
    print("=" * 60)
    print("🏁 测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
