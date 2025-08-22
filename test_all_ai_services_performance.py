#!/usr/bin/env python3
"""
测试所有AI服务的性能对比
包括：蓝图生成、每日运势、Heart Compass指导
"""

import asyncio
import aiohttp
import time
import json
import uuid
from datetime import datetime

# 测试配置
API_BASE_URL = "http://localhost:8000"

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

class AIServicePerformanceTester:
    """AI服务性能测试器"""
    
    def __init__(self):
        self.user_id = None
        self.test_results = []
    
    async def setup_test_user(self, session):
        """创建测试用户"""
        print("📝 步骤1: 创建测试用户...")
        start_time = time.time()
        
        create_user_response = await session.post(
            f"{API_BASE_URL}/api/v1/user/create",
            json=TEST_USER_DATA
        )
        
        if create_user_response.status != 200:
            error_text = await create_user_response.text()
            raise Exception(f"创建用户失败: {create_user_response.status}, {error_text}")
        
        user_data = await create_user_response.json()
        self.user_id = user_data["user_id"]
        create_time = time.time() - start_time
        
        print(f"✅ 用户创建成功: {self.user_id}")
        print(f"⏱️  用户创建耗时: {create_time:.2f}秒")
        print()
        
        return self.user_id
    
    async def test_blueprint_service(self, session):
        """测试蓝图生成服务"""
        print("🔮 测试1: 蓝图生成服务")
        print("-" * 40)
        
        blueprint_request = {
            "user_id": self.user_id,
            "user_profile": TEST_USER_DATA["profile"]
        }
        
        start_time = time.time()
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            response = await session.post(
                f"{API_BASE_URL}/api/v1/blueprint/generate",
                json=blueprint_request
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")
            print(f"⏱️  总耗时: {total_time:.2f}秒")
            
            if response.status == 200:
                response_data = await response.json()
                response_size = len(json.dumps(response_data, ensure_ascii=False))
                
                result = {
                    "service": "蓝图生成",
                    "status": "成功",
                    "time": total_time,
                    "size": response_size,
                    "endpoint": "/blueprint/generate"
                }
                
                print(f"✅ 生成成功")
                print(f"📊 响应大小: {response_size} 字符")
                
            else:
                error_text = await response.text()
                result = {
                    "service": "蓝图生成",
                    "status": "失败",
                    "time": total_time,
                    "error": error_text,
                    "endpoint": "/blueprint/generate"
                }
                print(f"❌ 生成失败: {response.status}")
                print(f"错误详情: {error_text}")
            
            self.test_results.append(result)
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.test_results.append({
                "service": "蓝图生成",
                "status": "异常",
                "time": time.time() - start_time,
                "error": str(e),
                "endpoint": "/blueprint/generate"
            })
        
        print()
    
    async def test_daily_fortune_service(self, session):
        """测试每日运势服务"""
        print("🌟 测试2: 每日运势服务")
        print("-" * 40)
        
        fortune_request = {
            "user_id": self.user_id,
            "user_profile": TEST_USER_DATA["profile"],
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        start_time = time.time()
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            response = await session.post(
                f"{API_BASE_URL}/api/v1/daily-fortune/generate",
                json=fortune_request
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")
            print(f"⏱️  总耗时: {total_time:.2f}秒")
            
            if response.status == 200:
                response_data = await response.json()
                response_size = len(json.dumps(response_data, ensure_ascii=False))
                
                result = {
                    "service": "每日运势",
                    "status": "成功",
                    "time": total_time,
                    "size": response_size,
                    "endpoint": "/daily-fortune/generate"
                }
                
                print(f"✅ 生成成功")
                print(f"📊 响应大小: {response_size} 字符")
                
            else:
                error_text = await response.text()
                result = {
                    "service": "每日运势",
                    "status": "失败",
                    "time": total_time,
                    "error": error_text,
                    "endpoint": "/daily-fortune/generate"
                }
                print(f"❌ 生成失败: {response.status}")
                print(f"错误详情: {error_text}")
            
            self.test_results.append(result)
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.test_results.append({
                "service": "每日运势",
                "status": "异常",
                "time": time.time() - start_time,
                "error": str(e),
                "endpoint": "/daily-fortune/generate"
            })
        
        print()
    
    async def test_heart_compass_service(self, session):
        """测试Heart Compass指导服务"""
        print("💫 测试3: Heart Compass指导服务")
        print("-" * 40)
        
        compass_request = {
            "user_id": self.user_id,
            "question": "我正在考虑是否要换工作，感觉当前工作缺乏挑战性，但又担心新工作的不确定性。请给我一些指导。",
            "user_profile": TEST_USER_DATA["profile"]
        }
        
        start_time = time.time()
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            response = await session.post(
                f"{API_BASE_URL}/api/v1/heart-compass/seek-guidance",
                json=compass_request
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"⏰ 结束时间: {datetime.now().strftime('%H:%M:%S')}")
            print(f"⏱️  总耗时: {total_time:.2f}秒")
            
            if response.status == 200:
                response_data = await response.json()
                response_size = len(json.dumps(response_data, ensure_ascii=False))
                
                result = {
                    "service": "Heart Compass",
                    "status": "成功",
                    "time": total_time,
                    "size": response_size,
                    "endpoint": "/heart-compass/seek-guidance"
                }
                
                print(f"✅ 生成成功")
                print(f"📊 响应大小: {response_size} 字符")
                
            else:
                error_text = await response.text()
                result = {
                    "service": "Heart Compass",
                    "status": "失败",
                    "time": total_time,
                    "error": error_text,
                    "endpoint": "/heart-compass/seek-guidance"
                }
                print(f"❌ 生成失败: {response.status}")
                print(f"错误详情: {error_text}")
            
            self.test_results.append(result)
            
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.test_results.append({
                "service": "Heart Compass",
                "status": "异常",
                "time": time.time() - start_time,
                "error": str(e),
                "endpoint": "/heart-compass/seek-guidance"
            })
        
        print()
    
    async def cleanup_test_user(self, session):
        """清理测试用户"""
        print("🧹 步骤4: 清理测试数据...")
        try:
            await session.delete(f"{API_BASE_URL}/api/v1/user/{self.user_id}")
            print("✅ 测试数据清理完成")
        except Exception as e:
            print(f"⚠️  数据清理失败: {e}")
        print()
    
    def generate_performance_report(self):
        """生成性能分析报告"""
        print("📈 AI服务性能分析报告")
        print("=" * 60)
        
        # 成功的测试结果
        successful_results = [r for r in self.test_results if r["status"] == "成功"]
        
        if successful_results:
            print("📊 成功测试结果:")
            print()
            
            # 按响应时间排序
            successful_results.sort(key=lambda x: x["time"])
            
            print(f"{'服务名称':<15} {'响应时间':<10} {'数据大小':<12} {'性能评级'}")
            print("-" * 55)
            
            for result in successful_results:
                time_str = f"{result['time']:.2f}秒"
                size_str = f"{result['size']:,}字符"
                
                # 性能评级
                if result['time'] < 10:
                    rating = "🎉 优秀"
                elif result['time'] < 20:
                    rating = "👍 良好"
                elif result['time'] < 30:
                    rating = "⚠️ 一般"
                else:
                    rating = "❌ 较慢"
                
                print(f"{result['service']:<15} {time_str:<10} {size_str:<12} {rating}")
            
            print()
            
            # 统计分析
            times = [r["time"] for r in successful_results]
            sizes = [r["size"] for r in successful_results]
            
            print("📈 统计分析:")
            print(f"   - 最快服务: {min(times):.2f}秒 ({successful_results[0]['service']})")
            print(f"   - 最慢服务: {max(times):.2f}秒 ({max(successful_results, key=lambda x: x['time'])['service']})")
            print(f"   - 平均响应时间: {sum(times)/len(times):.2f}秒")
            print(f"   - 平均数据大小: {sum(sizes)/len(sizes):,.0f}字符")
            
            # 性能差异分析
            if len(times) > 1:
                max_time = max(times)
                min_time = min(times)
                diff_percent = ((max_time - min_time) / min_time) * 100
                print(f"   - 最大性能差异: {diff_percent:.1f}%")
        
        # 失败的测试结果
        failed_results = [r for r in self.test_results if r["status"] != "成功"]
        if failed_results:
            print()
            print("❌ 失败测试结果:")
            for result in failed_results:
                print(f"   - {result['service']}: {result.get('error', '未知错误')}")
        
        print()
        print("💡 优化建议:")
        if successful_results:
            slowest = max(successful_results, key=lambda x: x["time"])
            if slowest["time"] > 20:
                print(f"   - {slowest['service']} 响应较慢，建议优化AI提示词或实现异步处理")
            
            fastest = min(successful_results, key=lambda x: x["time"])
            print(f"   - {fastest['service']} 性能最好，可作为优化参考标准")
            
            if len(successful_results) > 1:
                print("   - 考虑为不同服务实现不同的缓存策略")
                print("   - 可以根据服务复杂度调整AI模型参数")
        else:
            print("   - 所有服务都失败了，请检查系统配置和网络连接")

async def main():
    """主测试函数"""
    print("🔮 AI服务性能综合测试工具")
    print("=" * 60)
    print("📋 测试说明:")
    print("   - 测试所有AI服务的性能表现")
    print("   - 包括蓝图生成、每日运势、Heart Compass指导")
    print("   - 对比各服务的响应时间和数据大小")
    print("=" * 60)
    print()
    
    tester = AIServicePerformanceTester()
    
    async with aiohttp.ClientSession() as session:
        try:
            # 创建测试用户
            await tester.setup_test_user(session)
            
            # 测试所有AI服务
            await tester.test_blueprint_service(session)
            await tester.test_daily_fortune_service(session)
            await tester.test_heart_compass_service(session)
            
            # 清理测试数据
            await tester.cleanup_test_user(session)
            
        except Exception as e:
            print(f"❌ 测试过程中发生严重错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 生成性能报告
    tester.generate_performance_report()
    
    print("=" * 60)
    print("🏁 测试完成!")

if __name__ == "__main__":
    asyncio.run(main())
