#!/usr/bin/env python3
"""
检查数据库中的AI生成内容
"""

import asyncio
from app.core.database import Database

async def check_db_content():
    """检查数据库中的AI生成内容"""
    user_id = "bbcc3216-15f8-436d-b014-3dfca7dcf27f"
    
    print("🔍 检查数据库中的AI生成内容")
    print("=" * 50)
    
    # 检查 Heart Compass 记录
    print("\n🧭 Heart Compass 记录:")
    hc_records = await Database.find('heart_compass_records', {'user_id': user_id})
    for i, record in enumerate(hc_records):
        print(f"\n记录 {i+1}:")
        print(f"  问题: {record.get('question', 'N/A')}")
        print(f"  卦象: {record.get('hexagram', {}).get('name', 'N/A')}")
        ai_generated = record.get('ai_generated', 'N/A')
        if ai_generated and ai_generated != 'N/A':
            print(f"  AI生成内容: {ai_generated[:300]}...")
        else:
            print(f"  AI生成内容: {ai_generated}")
    
    # 检查 Daily Fortune 记录
    print("\n📅 Daily Fortune 记录:")
    df_records = await Database.find('daily_fortune_records', {'user_id': user_id})
    for i, record in enumerate(df_records):
        print(f"\n记录 {i+1}:")
        print(f"  日期: {record.get('date', 'N/A')}")
        print(f"  卦象: {record.get('hexagram', {}).get('name', 'N/A')}")
        ai_generated = record.get('ai_generated', 'N/A')
        if ai_generated and ai_generated != 'N/A':
            print(f"  AI生成内容: {ai_generated[:300]}...")
        else:
            print(f"  AI生成内容: {ai_generated}")

if __name__ == "__main__":
    asyncio.run(check_db_content())
