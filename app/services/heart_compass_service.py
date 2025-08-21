import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.core.database import Database
from app.core.cache import versioned_cache, VersionedCacheManager
from app.models.heart_compass import (
    HeartCompassRecord, HeartCompassRequest, 
    HeartCompassResponse, HeartCompassHistoryResponse, AskAgainRequest
)
from app.services.ai_service import AIService
from app.utils.logger import MyLogger

logger = MyLogger("heart_compass_service")

class HeartCompassService:
    """Heart Compass 指导服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.cache_manager = VersionedCacheManager()
    
    @versioned_cache(entity_type="heart_compass", expire=3600)
    async def seek_guidance(self, user_id: str, question: str, user_profile: dict):
        """获取指导 - 自动版本化缓存"""
        try:
            # 调用 AI 服务获取指导
            result = await self.ai_service.seek_heart_compass_guidance(question, user_profile)
            
            if not result.get("success"):
                raise Exception(f"AI 生成失败: {result.get('message')}")
            
            # 解析 AI 响应，构建结构化数据
            guidance_data = self._parse_heart_compass_ai_response(result.get("ai_content", ""))
            
            # 构建完整的指导记录
            guidance_record = HeartCompassRecord(
                user_id=user_id,
                question=question,
                **guidance_data,
                ai_generated=result.get("ai_content", ""),
                created_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("heart_compass_records", guidance_record.dict())
            
            logger.info(f"用户 {user_id} Heart Compass 指导生成成功")
            return guidance_record
            
        except Exception as e:
            logger.error(f"获取 Heart Compass 指导失败: {e}")
            raise
    
    async def ask_again(
        self, 
        user_id: str, 
        question: str, 
        user_profile: dict, 
        previous_guidance_id: Optional[str] = None
    ):
        """重新提问，基于之前的指导进行深入探讨"""
        try:
            # 构建上下文，包含之前的问题信息
            context = {
                "question": question,
                "user_profile": user_profile,
                "is_follow_up": True
            }
            
            # 如果有之前的指导ID，获取相关信息
            if previous_guidance_id:
                previous_guidance = await self.get_guidance_by_id(previous_guidance_id)
                if previous_guidance and previous_guidance.user_id == user_id:
                    context["previous_guidance"] = {
                        "hexagram": previous_guidance.hexagram,
                        "question": previous_guidance.question,
                        "guidance_summary": previous_guidance.decision_protocol.core_strategy
                    }
            
            # 调用 AI 服务获取深入指导
            result = await self.ai_service.seek_heart_compass_guidance(question, context)
            
            if not result.get("success"):
                raise Exception(f"AI 生成失败: {result.get('message')}")
            
            # 解析 AI 响应，构建结构化数据
            guidance_data = self._parse_heart_compass_ai_response(result.get("ai_content", ""))
            
            # 构建完整的指导记录
            guidance_record = HeartCompassRecord(
                user_id=user_id,
                question=question,
                **guidance_data,
                ai_generated=result.get("ai_content", ""),
                created_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("heart_compass_records", guidance_record.dict())
            
            logger.info(f"用户 {user_id} Heart Compass 重新提问指导生成成功")
            return guidance_record
            
        except Exception as e:
            logger.error(f"重新提问失败: {e}")
            raise
    
    async def get_guidance_history(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 10
    ) -> HeartCompassHistoryResponse:
        """获取指导历史"""
        try:
            # 计算跳过数量
            skip = (page - 1) * limit
            
            # 查询数据库
            records = await Database.find(
                "heart_compass_records",
                {"user_id": user_id},
                sort=[("created_at", -1)],
                limit=limit
            )
            
            # 获取总数
            total = await Database.count_documents("heart_compass_records", {"user_id": user_id})
            
            # 构建响应数据
            guidance_records = []
            for record in records:
                guidance_records.append(HeartCompassRecord(**record))
            
            # 计算分页信息
            pages = (total + limit - 1) // limit
            
            return HeartCompassHistoryResponse(
                success=True,
                data=guidance_records,
                total=total,
                page=page,
                page_size=limit
            )
            
        except Exception as e:
            logger.error(f"获取指导历史失败: {e}")
            return HeartCompassHistoryResponse(
                success=False,
                data=[],
                total=0,
                message=f"获取指导历史失败: {str(e)}"
            )
    
    async def get_guidance_by_id(self, guidance_id: str) -> Optional[HeartCompassRecord]:
        """根据ID获取指导记录"""
        try:
            from bson import ObjectId
            # 转换字符串ID为ObjectId
            object_id = ObjectId(guidance_id)
            record_data = await Database.find_one("heart_compass_records", {"_id": object_id})
            if record_data:
                return HeartCompassRecord(**record_data)
            return None
        except Exception as e:
            logger.error(f"获取指导记录失败: {e}")
            raise
    
    async def delete_guidance(self, guidance_id: str, user_id: str) -> bool:
        """删除指导记录"""
        try:
            result = await Database.delete_one(
                "heart_compass_records", 
                {"_id": guidance_id, "user_id": user_id}
            )
            
            if result > 0:
                # 失效相关缓存
                await self.cache_manager.invalidate_entity_cache(
                    user_id, "heart_compass", "指导记录删除"
                )
                logger.info(f"指导记录 {guidance_id} 已删除")
            
            return result > 0
            
        except Exception as e:
            logger.error(f"删除指导记录失败: {e}")
            return False
    
    def _parse_heart_compass_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """解析 AI 响应，构建结构化数据"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回基础结构
        return {
            "hexagram": {
                "code": "1",
                "name": "乾卦",
                "english_name": "The Creative, Heaven",
                "title": "乾卦 - The Creative, Heaven",
                "hexagram_text": "乾：元，亨，利，贞。",
                "image_text": "天行健，君子以自强不息。",
                "focus_yao": {
                    "yao_number": 1,
                    "yao_text": "初九：潜龙，勿用。"
                }
            },
            "dialogue_flow": {
                "revelation": "天行健，君子以自强不息。",
                "analysis": "此刻的你，内在的创造力和领导力正如同天空般广阔...",
                "guidance": "这是一个应当展现自我、发挥创造力的时刻...",
                "encouragement": "相信你的天赋，它将指引你走向成功。"
            },
            "deep_wisdom": {
                "title": "Deep Wisdom",
                "explanation": "The Qián hexagram symbolizes the power of Heaven — pure yang, strength, and eternal movement...",
                "philosophical_meaning": "This is the most powerful hexagram among the 64, representing creativity, leadership, and infinite possibilities.",
                "personal_interpretation": "When Qián appears, the universe is telling you that now is the time to manifest your inner strength and creative gifts."
            },
            "action_guide": {
                "title": "Action Guide",
                "main_actions": [
                    "Trust in your inner creativity and leadership abilities",
                    "Take initiative and become a catalyst for positive change"
                ],
                "supporting_actions": [
                    "Maintain strong will while leading with virtue and compassion",
                    "Transform your vision into concrete action plans"
                ],
                "inspirational_message": "The energy of Qián flows through you, meaning you have the power to change your current situation."
            },
            "decision_protocol": {
                "title": "决策协议 | Decision Protocol",
                "situation_code": "乾卦 (#1)",
                "core_strategy": "自强不息，创造无限",
                "action_guide": [
                    "展现你的创造力和领导力",
                    "主动承担责任，推动积极变化",
                    "保持坚定的意志和美德"
                ]
            }
        }
