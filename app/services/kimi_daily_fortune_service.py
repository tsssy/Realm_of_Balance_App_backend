#!/usr/bin/env python3
"""
Kimi版本的Daily Fortune服务
使用Kimi AI替代Gemini进行运势生成
"""

import json
import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, List

from app.services.kimi_service import KimiService
from app.utils.logger import MyLogger
from app.core.database import Database
from app.models.daily_fortune import DailyFortune

logger = MyLogger("kimi_daily_fortune_service")

class KimiDailyFortuneService:
    """Kimi版本的Daily Fortune服务类"""
    
    def __init__(self):
        self.ai_service = KimiService()
        self.logger = logger
    
    async def generate_daily_fortune(self, user_id: str, user_profile: Dict[str, Any], date: str = None):
        """生成每日运势 - Kimi版本（与原始服务完全一致）"""
        try:
            # 调用 Kimi AI 服务生成运势（与原始服务完全一致的方法调用）
            result = await self.ai_service.generate_daily_fortune(user_profile, date)
            
            if not result.get("success"):
                raise Exception(f"AI 生成失败: {result.get('message')}")
            
            # 解析 AI 响应，构建结构化数据（与原始服务一致）
            fortune_data = self._parse_daily_fortune_ai_response(result.get("ai_content", ""))
            
            # 构建完整的运势记录（与原始服务完全一致）
            fortune_record = DailyFortune(
                user_id=user_id,
                date=datetime.strptime(date, "%Y-%m-%d") if date else datetime.now(),
                **fortune_data,
                ai_generated=result.get("ai_content", ""),
                created_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("daily_fortune_records", fortune_record.dict())
            
            self.logger.info(f"用户 {user_id} 每日运势生成成功，日期: {date or 'today'}")
            return fortune_record
            
        except Exception as e:
            self.logger.error(f"生成每日运势失败: {e}")
            raise
    
    async def get_today_fortune(self, user_id: str, user_profile: Dict[str, Any]):
        """获取今日运势 - 如果不存在则自动生成"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 先检查数据库是否已经存在今日运势
        existing_fortune = await self.get_fortune_by_date(user_id, today)
        if existing_fortune:
            self.logger.info(f"用户 {user_id} 今日运势已存在，直接返回")
            return existing_fortune
        
        # 如果不存在，则生成新的运势
        self.logger.info(f"用户 {user_id} 今日运势不存在，开始生成")
        return await self.generate_daily_fortune(user_id, user_profile, today)
    
    async def get_fortune_by_date(self, user_id: str, target_date: str):
        """获取指定日期的运势"""
        try:
            # 构建日期范围查询，匹配当天的所有时间
            date_obj = datetime.strptime(target_date, "%Y-%m-%d")
            start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            record = await Database.find_one(
                "daily_fortune_records",
                {
                    "user_id": user_id, 
                    "date": {
                        "$gte": start_of_day,
                        "$lte": end_of_day
                    }
                }
            )
            
            if record:
                return DailyFortune(**record)
            return None
            
        except Exception as e:
            self.logger.error(f"获取Kimi运势记录失败: {e}")
            raise Exception(f"获取Kimi运势记录失败: {str(e)}")
    
    async def get_fortune_history(self, user_id: str, start_date: str = None, end_date: str = None):
        """获取运势历史"""
        try:
            # 构建查询条件
            query = {"user_id": user_id}
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                query["fortune_date"] = date_filter
            
            # 获取记录
            records = await Database.find(
                "daily_fortune_records",
                query,
                sort=[("fortune_date", -1)]
            )
            
            return [DailyFortune(**record) for record in records]
            
        except Exception as e:
            self.logger.error(f"获取Kimi运势历史失败: {e}")
            raise Exception(f"获取Kimi运势历史失败: {str(e)}")
    
    async def delete_fortune(self, fortune_id: str, user_id: str):
        """删除运势记录"""
        try:
            result = await Database.delete_one(
                "daily_fortune_records",
                {"fortune_id": fortune_id, "user_id": user_id}
            )
            return result.deleted_count > 0
            
        except Exception as e:
            self.logger.error(f"删除Kimi运势记录失败: {e}")
            raise Exception(f"删除Kimi运势记录失败: {str(e)}")
    
    def _parse_daily_fortune_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """解析Daily Fortune响应"""
        try:
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content.strip())
            
            if '```json' in ai_content:
                start = ai_content.find('```json') + 7
                end = ai_content.find('```', start)
                json_content = ai_content[start:end].strip()
                return json.loads(json_content)
            
            self.logger.warning(f"无法解析Kimi Daily Fortune响应，使用默认结构: {ai_content[:100]}")
            
        except Exception as e:
            self.logger.error(f"解析Kimi Daily Fortune响应失败: {e}, 内容: {ai_content[:100]}")
        
        return {
            "hexagram": {
                "name": "今日卦象",
                "description": "基于您的八字和今日天干地支的卦象",
                "interpretation": "卦象解读"
            },
            "time_periods": {
                "morning": {
                    "time": "06:00-12:00",
                    "energy": "上升",
                    "suitable_activities": ["工作", "学习"],
                    "advice": "适宜开展重要事务"
                },
                "afternoon": {
                    "time": "12:00-18:00", 
                    "energy": "稳定",
                    "suitable_activities": ["会议", "社交"],
                    "advice": "适宜处理人际关系"
                },
                "evening": {
                    "time": "18:00-24:00",
                    "energy": "收敛", 
                    "suitable_activities": ["休息", "反思"],
                    "advice": "适宜内省和休养"
                }
            },
            "lucky_elements": {
                "colors": ["蓝色", "绿色"],
                "numbers": [3, 8],
                "directions": ["东方", "北方"],
                "materials": ["木", "水"]
            },
            "personal_advice": {
                "focus_areas": ["事业发展", "人际关系"],
                "avoid": ["冲动决策", "争执"],
                "enhance": ["沟通能力", "耐心"],
                "general_guidance": "今日适宜稳扎稳打，避免急躁"
            },
            "overall_score": 78
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.ai_service.cleanup()


# 单例模式
_kimi_daily_fortune_service_instance = None

async def get_kimi_daily_fortune_service() -> KimiDailyFortuneService:
    """获取Kimi Daily Fortune服务实例"""
    global _kimi_daily_fortune_service_instance
    if _kimi_daily_fortune_service_instance is None:
        _kimi_daily_fortune_service_instance = KimiDailyFortuneService()
    return _kimi_daily_fortune_service_instance
