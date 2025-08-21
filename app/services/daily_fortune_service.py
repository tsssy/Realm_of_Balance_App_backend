import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.core.database import Database
from app.core.cache import versioned_cache, VersionedCacheManager
from app.models.daily_fortune import (
    DailyFortune, DailyFortuneRequest, 
    DailyFortuneResponse, DailyFortuneHistoryResponse
)
from app.services.ai_service import AIService
from app.utils.logger import MyLogger

logger = MyLogger("daily_fortune_service")

class DailyFortuneService:
    """每日运势服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.cache_manager = VersionedCacheManager()
    
    @versioned_cache(entity_type="daily_fortune", expire=86400)  # 24小时缓存
    async def generate_daily_fortune(self, user_id: str, user_profile: dict, date: str = None):
        """生成每日运势 - 自动版本化缓存"""
        try:
            # 调用 AI 服务生成运势
            result = await self.ai_service.generate_daily_fortune(user_profile, date)
            
            if not result.get("success"):
                raise Exception(f"AI 生成失败: {result.get('message')}")
            
            # 解析 AI 响应，构建结构化数据
            fortune_data = self._parse_daily_fortune_ai_response(result.get("ai_content", ""))
            
            # 构建完整的运势记录
            fortune_record = DailyFortune(
                user_id=user_id,
                date=datetime.strptime(date, "%Y-%m-%d") if date else datetime.now(),
                **fortune_data,
                ai_generated=result.get("ai_content", ""),
                created_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("daily_fortune_records", fortune_record.dict())
            
            logger.info(f"用户 {user_id} 每日运势生成成功，日期: {date or 'today'}")
            return fortune_record
            
        except Exception as e:
            logger.error(f"生成每日运势失败: {e}")
            raise
    
    async def get_fortune_by_date(self, user_id: str, date: str):
        """获取指定日期的运势"""
        try:
            # 先尝试从缓存获取
            cache_key = f"daily_fortune:{user_id}:{date}"
            cached_result = await self.cache_manager.get_entity_cache(cache_key)
            if cached_result:
                return cached_result
            
            # 从数据库查询
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            # 构建日期范围查询，匹配当天的所有时间
            start_of_day = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            record_data = await Database.find_one(
                "daily_fortune_records", 
                {
                    "user_id": user_id, 
                    "date": {
                        "$gte": start_of_day,
                        "$lte": end_of_day
                    }
                }
            )
            
            if record_data:
                fortune_record = DailyFortune(**record_data)
                # 缓存结果（使用版本化缓存）
                await self.cache_manager.set_with_version(
                    cache_key, fortune_record, user_id, "daily_fortune", 3600
                )
                return fortune_record
            
            return None
            
        except Exception as e:
            logger.error(f"获取指定日期运势失败: {e}")
            raise
    
    async def get_today_fortune(self, user_id: str, user_profile: Optional[dict] = None):
        """获取今日运势"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 先尝试获取今日运势
            daily_fortune = await self.get_fortune_by_date(user_id, today)
            
            # 如果今日运势不存在且有用户配置文件，则生成运势
            if not daily_fortune and user_profile:
                daily_fortune = await self.generate_daily_fortune(user_id, user_profile, today)
            
            return daily_fortune
            
        except Exception as e:
            logger.error(f"获取今日运势失败: {e}")
            raise
    
    async def get_fortune_history(self, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 30):
        """获取运势历史"""
        try:
            # 构建查询条件
            query = {"user_id": user_id}
            
            # 如果指定了日期范围，添加日期过滤
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    try:
                        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                        date_filter["$gte"] = start_date_obj
                    except ValueError:
                        logger.warning(f"无效的开始日期格式: {start_date}")
                
                if end_date:
                    try:
                        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                        date_filter["$lte"] = end_date_obj
                    except ValueError:
                        logger.warning(f"无效的结束日期格式: {end_date}")
                
                if date_filter:
                    query["date"] = date_filter
            
            # 查询数据库
            records = await Database.find(
                "daily_fortune_records",
                query,
                sort=[("date", -1)],
                limit=limit
            )
            
            fortune_records = []
            for record in records:
                fortune_records.append(DailyFortune(**record))
            
            return fortune_records
            
        except Exception as e:
            logger.error(f"获取运势历史失败: {e}")
            raise
    
    async def delete_fortune(self, user_id: str, date: str):
        """删除运势记录"""
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            result = await Database.delete_one(
                "daily_fortune_records", 
                {"user_id": user_id, "date": date_obj}
            )
            
            if result > 0:
                # 失效相关缓存
                cache_key = f"daily_fortune:{user_id}:{date}"
                await self.cache_manager.invalidate_entity_cache(cache_key, "运势记录删除")
                logger.info(f"运势记录已删除，用户: {user_id}, 日期: {date}")
            
            return result > 0
            
        except Exception as e:
            logger.error(f"删除运势记录失败: {e}")
            return False
    
    def _parse_daily_fortune_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """解析 AI 响应，构建结构化数据"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回基础结构
        return {
            "hexagram": {
                "name": "晋卦",
                "pinyin": "Jìn",
                "english_name": "The Progress, Radiance",
                "title": "晋卦 (Jìn) - The Progress, Radiance",
                "energy": "Dynamic & Expansive",
                "luck": 85,
                "hexagram_text": "晋：康侯用锡马蕃庶，昼日三接。",
                "image_text": "明出地上，晋；君子以自昭明德。"
            },
            "time_advice": [
                {
                    "period": "Morning (6:00 AM - 12:00 PM)",
                    "start_time": "6:00 AM",
                    "end_time": "12:00 PM",
                    "activity": "Embrace New Beginnings",
                    "description": "The morning brings fresh energy. Focus on planning and initiating new tasks. Your mind is sharpest now.",
                    "energy": "High & Focused",
                    "priority": "High"
                },
                {
                    "period": "Afternoon (12:00 PM - 6:00 PM)",
                    "start_time": "12:00 PM",
                    "end_time": "6:00 PM",
                    "activity": "Collaborate & Connect",
                    "description": "Social interactions are favored. Engage in discussions, networking, and teamwork. Seek diverse perspectives.",
                    "energy": "Social & Harmonious",
                    "priority": "Medium"
                },
                {
                    "period": "Evening (6:00 PM - 12:00 AM)",
                    "start_time": "6:00 PM",
                    "end_time": "12:00 AM",
                    "activity": "Reflect & Recharge",
                    "description": "Wind down and process the day's events. Engage in calming activities like meditation or reading. Prioritize rest.",
                    "energy": "Calm & Restorative",
                    "priority": "Medium"
                }
            ],
            "lucky_elements": {
                "color": "Emerald Green",
                "direction": "Southeast",
                "number": 8,
                "element": "Wood",
                "gemstone": "Jade"
            },
            "personal_advice": "Today, the energy of 'Progress' (晋卦) illuminates your path. Embrace opportunities for growth and expansion. Your natural strengths in creativity and empathy will be particularly potent. Remember to balance your fiery passion with grounding practices to maintain stability. Trust your intuition, but also seek practical advice. A small act of kindness can bring unexpected rewards. Stay open to new ideas and connections."
        }
