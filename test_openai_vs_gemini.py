#!/usr/bin/env python3
"""
OpenAI GPT-4o-mini vs Gemini 2.5-flash 性能对比测试
测试两个AI服务的响应速度差异
"""

import asyncio
import time
import sys
import os
import statistics
from datetime import datetime
import requests

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__)))

# 测试数据 - 使用全新的ID避免冲突
TEST_USER_DATA = {
    "device_id": "perf_test_device_20250830_v2",
    "profile": {
        "user_id": "perf_test_user_20250830_v2",
        "name": "性能对比测试用户",
        "email": "perf_test_v2@example.com",
        "gender": "other",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "birth_location": "Beijing, China"
    }
}

BASE_URL = "http://localhost:8001"

async def create_test_user():
    """创建测试用户"""
    print("🔧 创建测试用户...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/user/create",
            json=TEST_USER_DATA,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 测试用户创建成功")
            return True
        elif response.status_code == 400 and ("用户已存在" in response.text or "设备ID已存在" in response.text):
            print("✅ 测试用户已存在")
            return True
        else:
            print(f"❌ 创建用户失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建用户异常: {e}")
        return False

async def test_api_endpoint(endpoint_name: str, url: str, data: dict) -> dict:
    """测试单个API接口"""
    print(f"\n🔬 测试 {endpoint_name}")
    print(f"接口: {url}")
    print(f"时间: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        start_time = time.time()
        start_datetime = datetime.now()
        print(f"开始时间: {start_datetime.strftime('%H:%M:%S')}")
        
        response = requests.post(url, json=data, timeout=120)  # 2分钟超时
        
        end_time = time.time()
        end_datetime = datetime.now()
        response_time = end_time - start_time
        
        print(f"结束时间: {end_datetime.strftime('%H:%M:%S')}")
        print(f"响应时间: {response_time:.2f}秒")
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            success = response_data.get('success', False)
            print(f"接口成功: {success}")
            
            if success:
                data_info = response_data.get('data', {})
                ai_response_time = data_info.get('ai_response_time', 0)
                processing_time = data_info.get('processing_time', 0)
                source = data_info.get('source', 'unknown')
                model = data_info.get('model', 'unknown')
                cached = data_info.get('cached', False)
                
                print(f"AI响应时间: {ai_response_time:.2f}秒")
                print(f"总处理时间: {processing_time:.2f}秒")
                print(f"数据源: {source}")
                print(f"模型: {model}")
                print(f"缓存: {cached}")
                
                return {
                    "success": True,
                    "endpoint": endpoint_name,
                    "total_response_time": response_time,
                    "ai_response_time": ai_response_time,
                    "processing_time": processing_time,
                    "source": source,
                    "model": model,
                    "cached": cached,
                    "start_time": start_datetime,
                    "end_time": end_datetime
                }
            else:
                message = response_data.get('message', 'Unknown error')
                print(f"❌ 接口失败: {message}")
                return {
                    "success": False,
                    "endpoint": endpoint_name,
                    "error": message,
                    "response_time": response_time
                }
        else:
            print(f"❌ HTTP错误: {response.text}")
            return {
                "success": False,
                "endpoint": endpoint_name,
                "error": f"HTTP {response.status_code}: {response.text}",
                "response_time": response_time
            }
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return {
            "success": False,
            "endpoint": endpoint_name,
            "error": str(e)
        }

async def cooldown(seconds: int):
    """冷却期"""
    print(f"\n⏳ 冷却期 ({seconds}秒)")
    for i in range(seconds, 0, -1):
        print(f"\r⏰ 剩余 {i:2d} 秒", end="", flush=True)
        await asyncio.sleep(1)
    print("\n✅ 冷却完成")

async def run_performance_comparison():
    """运行性能对比测试"""
    print("🚀 OpenAI GPT-4o-mini vs Gemini 2.5-flash 性能对比测试")
    print("=" * 80)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试用户
    if not await create_test_user():
        print("❌ 无法创建测试用户，退出测试")
        return
    
    # 测试请求数据
    request_data = {
        "user_id": TEST_USER_DATA["profile"]["user_id"],
        "user_profile": {
            "gender": TEST_USER_DATA["profile"]["gender"],
            "birth_date": TEST_USER_DATA["profile"]["birth_date"],
            "birth_time": TEST_USER_DATA["profile"]["birth_time"],
            "birth_location": TEST_USER_DATA["profile"]["birth_location"]
        }
    }
    
    # 测试轮数
    ROUNDS = 3
    COOLDOWN_TIME = 25  # 增加冷却时间确保清除缓存
    
    results = []
    
    try:
        for round_num in range(1, ROUNDS + 1):
            print(f"\n" + "="*60)
            print(f"🎯 第 {round_num}/{ROUNDS} 轮测试")
            print("="*60)
            
            # 测试 OpenAI GPT-4o-mini
            openai_result = await test_api_endpoint(
                "OpenAI GPT-4o-mini",
                f"{BASE_URL}/api/v2/openai-blueprint/quick",
                request_data
            )
            results.append(openai_result)
            
            # 冷却期
            await cooldown(COOLDOWN_TIME)
            
            # 测试 Gemini 2.5-flash
            gemini_result = await test_api_endpoint(
                "Gemini 2.5-flash",
                f"{BASE_URL}/api/v1/blueprint/quick",
                request_data
            )
            results.append(gemini_result)
            
            # 本轮对比
            if openai_result.get('success') and gemini_result.get('success'):
                openai_time = openai_result['total_response_time']
                gemini_time = gemini_result['total_response_time']
                
                print(f"\n📊 第{round_num}轮结果:")
                print(f"OpenAI: {openai_time:.2f}秒")
                print(f"Gemini: {gemini_time:.2f}秒")
                
                if openai_time < gemini_time:
                    improvement = ((gemini_time - openai_time) / gemini_time) * 100
                    print(f"🎉 OpenAI更快 {improvement:.1f}% (节省{gemini_time-openai_time:.2f}秒)")
                elif openai_time > gemini_time:
                    slower = ((openai_time - gemini_time) / gemini_time) * 100
                    print(f"⚠️ OpenAI较慢 {slower:.1f}% (慢{openai_time-gemini_time:.2f}秒)")
                else:
                    print("📊 两者性能基本相同")
            
            # 最后一轮不需要冷却
            if round_num < ROUNDS:
                await cooldown(COOLDOWN_TIME)
        
        # 统计分析
        print(f"\n" + "="*80)
        print("📈 详细统计分析")
        print("="*80)
        
        # 分离成功的结果
        openai_times = []
        gemini_times = []
        
        for result in results:
            if result.get('success') and not result.get('cached', False):  # 排除缓存结果
                if "OpenAI" in result.get('endpoint', ''):
                    openai_times.append(result['total_response_time'])
                elif "Gemini" in result.get('endpoint', ''):
                    gemini_times.append(result['total_response_time'])
        
        if len(openai_times) >= 2 and len(gemini_times) >= 2:
            print(f"✅ 成功完成 {len(openai_times)} 轮 OpenAI 和 {len(gemini_times)} 轮 Gemini 测试\n")
            
            # 计算统计数据
            openai_avg = statistics.mean(openai_times)
            gemini_avg = statistics.mean(gemini_times)
            openai_std = statistics.stdev(openai_times) if len(openai_times) > 1 else 0
            gemini_std = statistics.stdev(gemini_times) if len(gemini_times) > 1 else 0
            
            print(f"📊 性能对比统计:")
            print(f"{'指标':<20} {'OpenAI GPT-4o-mini':<20} {'Gemini 2.5-flash':<20} {'差异':<15}")
            print("-" * 80)
            print(f"{'平均响应时间':<20} {openai_avg:<20.2f} {gemini_avg:<20.2f} {((openai_avg-gemini_avg)/gemini_avg*100):+.1f}%")
            print(f"{'标准差':<20} {openai_std:<20.2f} {gemini_std:<20.2f} {'N/A':<15}")
            print(f"{'最快时间':<20} {min(openai_times):<20.2f} {min(gemini_times):<20.2f} {'N/A':<15}")
            print(f"{'最慢时间':<20} {max(openai_times):<20.2f} {max(gemini_times):<20.2f} {'N/A':<15}")
            
            # 逐轮详情
            print(f"\n📋 逐轮详情:")
            print(f"{'轮次':<8} {'OpenAI(秒)':<12} {'Gemini(秒)':<12} {'OpenAI优势':<15}")
            print("-" * 50)
            
            wins = 0
            total_saved = 0
            
            for i in range(min(len(openai_times), len(gemini_times))):
                improvement = ((gemini_times[i] - openai_times[i]) / gemini_times[i]) * 100
                saved_time = gemini_times[i] - openai_times[i]
                total_saved += saved_time
                
                if openai_times[i] < gemini_times[i]:
                    wins += 1
                    status = f"+{improvement:.1f}%"
                else:
                    status = f"{improvement:.1f}%"
                
                print(f"第{i+1}轮{'':<4} {openai_times[i]:<12.2f} {gemini_times[i]:<12.2f} {status:<15}")
            
            # 综合结论
            print(f"\n🎯 性能对比结论:")
            print(f"🏆 OpenAI胜出轮数: {wins}/{min(len(openai_times), len(gemini_times))}")
            print(f"⚡ 平均时间差异: {total_saved/min(len(openai_times), len(gemini_times)):.2f}秒")
            print(f"📈 平均性能差异: {((openai_avg-gemini_avg)/gemini_avg*100):.1f}%")
            
            # 稳定性分析
            openai_cv = (openai_std / openai_avg) * 100 if openai_avg > 0 else 0
            gemini_cv = (gemini_std / gemini_avg) * 100 if gemini_avg > 0 else 0
            
            print(f"\n📊 稳定性分析:")
            print(f"OpenAI变异系数: {openai_cv:.1f}%")
            print(f"Gemini变异系数: {gemini_cv:.1f}%")
            
            if openai_cv < gemini_cv:
                print("✅ OpenAI性能更稳定")
            else:
                print("✅ Gemini性能更稳定")
            
            # 最终建议
            print(f"\n💡 最终建议:")
            if wins >= len(openai_times)/2 and openai_avg < gemini_avg:
                print("🎉 强烈建议使用OpenAI GPT-4o-mini！")
                print(f"   - 平均每次节省 {gemini_avg-openai_avg:.2f}秒")
                print(f"   - 胜率: {wins/len(openai_times)*100:.0f}%")
            elif wins >= len(openai_times)/2:
                print("✅ 建议使用OpenAI GPT-4o-mini")
            else:
                print("⚠️ 建议继续使用Gemini 2.5-flash")
                print(f"   - Gemini平均更快 {abs((openai_avg-gemini_avg)/gemini_avg*100):.1f}%")
        
        else:
            print("❌ 测试数据不足，无法进行完整统计分析")
            successful_tests = len([r for r in results if r.get('success')])
            print(f"成功测试: {successful_tests}/{ROUNDS*2}")
            
    except Exception as e:
        print(f"❌ 测试过程异常: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🏁 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return results

if __name__ == "__main__":
    print("启动 OpenAI vs Gemini 性能对比测试...")
    try:
        asyncio.run(run_performance_comparison())
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行错误: {e}")
        import traceback
        traceback.print_exc()
