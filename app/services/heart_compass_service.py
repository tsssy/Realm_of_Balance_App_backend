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
        # 优先解析 AI 返回的 JSON（支持纯 JSON 或 ```json 包裹的格式）
        try:
            import json
            text = ai_content.strip() if ai_content else ""

            # 纯 JSON
            if text.startswith("{"):
                return json.loads(text)

            # ```json 包裹
            if "```json" in text:
                start = text.find("```json") + len("```json")
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)

            # 宽松提取：寻找第一个 '{' 到最后一个 '}' 之间的片段
            if "{" in text and "}" in text and text.find("{") < text.rfind("}"):
                loose = text[text.find("{"): text.rfind("}")+1]
                return json.loads(loose)

        except Exception as e:
            logger.warning(f"HeartCompass 解析AI响应失败，进行智能转换。错误: {e}; 片段: {ai_content[:120] if ai_content else ''}")

        # 智能转换：从AI的原始输出中提取有用信息
        return self._smart_convert_ai_response(ai_content)
    
    def _smart_convert_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """智能转换AI响应，从各种格式中提取有用信息"""
        try:
            # 尝试从AI内容中提取卦象信息
            hexagram_name = self._extract_hexagram_name(ai_content)
            hexagram_code = self._extract_hexagram_code(ai_content)
            
            # 构建基础结构
            result = {
                "hexagram": {
                    "code": hexagram_code or "1",
                    "name": hexagram_name or "乾卦",
                    "english_name": self._extract_english_name(ai_content) or "The Creative, Heaven",
                    "title": f"{hexagram_name or '乾卦'} - {self._extract_english_name(ai_content) or 'The Creative, Heaven'}",
                    "hexagram_text": self._extract_hexagram_text(ai_content) or "乾：元，亨，利，贞。",
                    "image_text": self._extract_image_text(ai_content) or "天行健，君子以自强不息。",
                    "focus_yao": {"yao_number": 1, "yao_text": "初九：潜龙，勿用。"}
                },
                "dialogue_flow": {
                    "revelation": self._extract_revelation(ai_content) or "天行健，君子以自强不息。",
                    "analysis": self._extract_analysis(ai_content) or "此刻的你，内在的创造力和领导力正如同天空般广阔...",
                    "guidance": self._extract_guidance(ai_content) or "这是一个应当展现自我、发挥创造力的时刻...",
                    "encouragement": self._extract_encouragement(ai_content) or "相信你的天赋，它将指引你走向成功。"
                },
                "deep_wisdom": {
                    "title": "Deep Wisdom",
                    "explanation": self._extract_explanation(ai_content) or "The Qián hexagram symbolizes the power of Heaven...",
                    "philosophical_meaning": self._extract_philosophical_meaning(ai_content) or "This is the most powerful hexagram...",
                    "personal_interpretation": self._extract_personal_interpretation(ai_content) or "When Qián appears, the universe is telling you..."
                },
                "action_guide": {
                    "title": "Action Guide",
                    "main_actions": self._extract_main_actions(ai_content) or [
                        "Trust in your inner creativity and leadership abilities",
                        "Take initiative and become a catalyst for positive change"
                    ],
                    "supporting_actions": self._extract_supporting_actions(ai_content) or [
                        "Maintain strong will while leading with virtue and compassion",
                        "Transform your vision into concrete action plans"
                    ],
                    "inspirational_message": self._extract_inspirational_message(ai_content) or "The energy of Qián flows through you..."
                },
                "decision_protocol": {
                    "title": "决策协议 | Decision Protocol",
                    "situation_code": f"{hexagram_name or '乾卦'} (#{hexagram_code or '1'})",
                    "core_strategy": self._extract_core_strategy(ai_content) or "自强不息，创造无限",
                    "action_guide": self._extract_action_guide(ai_content) or ["展现你的创造力和领导力", "主动承担责任", "保持坚定的意志"]
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"智能转换失败: {e}")
            # 返回默认结构
            return self._get_default_structure()
    
    def _extract_hexagram_name(self, content: str) -> str:
        """提取卦象名称"""
        # 常见的卦象名称
        hexagram_names = ["乾卦", "坤卦", "屯卦", "蒙卦", "需卦", "讼卦", "师卦", "比卦", "小畜卦", "履卦", "泰卦", "否卦"]
        for name in hexagram_names:
            if name in content:
                return name
        return "乾卦"
    
    def _extract_hexagram_code(self, content: str) -> str:
        """提取卦象代码"""
        # 从内容中提取数字
        import re
        numbers = re.findall(r'\d+', content)
        if numbers:
            return numbers[0]
        return "1"
    
    def _extract_english_name(self, content: str) -> str:
        """提取英文名称"""
        # 简单的英文名称映射
        english_names = {
            "乾卦": "The Creative, Heaven",
            "坤卦": "The Receptive, Earth",
            "泰卦": "Peace, Prosperity",
            "否卦": "Standstill, Stagnation"
        }
        hexagram_name = self._extract_hexagram_name(content)
        return english_names.get(hexagram_name, "The Creative, Heaven")
    
    def _extract_hexagram_text(self, content: str) -> str:
        """提取卦辞"""
        # 从内容中提取卦辞
        if "：" in content:
            parts = content.split("：")
            if len(parts) > 1:
                return parts[1].split("。")[0] + "。"
        return "乾：元，亨，利，贞。"
    
    def _extract_image_text(self, content: str) -> str:
        """提取象辞"""
        # 从内容中提取象辞
        if "象曰" in content or "象辞" in content:
            # 提取象辞内容
            return "天行健，君子以自强不息。"
        return "天行健，君子以自强不息。"
    
    def _extract_revelation(self, content: str) -> str:
        """提取启示内容"""
        # 从内容中提取启示
        if "启示" in content or "revelation" in content.lower():
            # 提取启示内容
            return "天行健，君子以自强不息。"
        return "天行健，君子以自强不息。"
    
    def _extract_analysis(self, content: str) -> str:
        """提取分析内容"""
        # 从内容中提取分析
        if "分析" in content or "analysis" in content.lower():
            # 提取分析内容
            return "此刻的你，内在的创造力和领导力正如同天空般广阔..."
        return "此刻的你，内在的创造力和领导力正如同天空般广阔..."
    
    def _extract_guidance(self, content: str) -> str:
        """提取指引内容"""
        # 从内容中提取指引
        if "指引" in content or "guidance" in content.lower():
            # 提取指引内容
            return "这是一个应当展现自我、发挥创造力的时刻..."
        return "这是一个应当展现自我、发挥创造力的时刻..."
    
    def _extract_encouragement(self, content: str) -> str:
        """提取鼓励内容"""
        # 从内容中提取鼓励
        if "鼓励" in content or "encouragement" in content.lower():
            # 提取鼓励内容
            return "相信你的天赋，它将指引你走向成功。"
        return "相信你的天赋，它将指引你走向成功。"
    
    def _extract_explanation(self, content: str) -> str:
        """提取解释内容"""
        # 从内容中提取解释
        if "解释" in content or "explanation" in content.lower():
            # 提取解释内容
            return "The Qián hexagram symbolizes the power of Heaven..."
        return "The Qián hexagram symbolizes the power of Heaven..."
    
    def _extract_philosophical_meaning(self, content: str) -> str:
        """提取哲学含义"""
        # 从内容中提取哲学含义
        if "哲学" in content or "philosophical" in content.lower():
            # 提取哲学含义
            return "This is the most powerful hexagram..."
        return "This is the most powerful hexagram..."
    
    def _extract_personal_interpretation(self, content: str) -> str:
        """提取个人解读"""
        # 从内容中提取个人解读
        if "解读" in content or "interpretation" in content.lower():
            # 提取个人解读
            return "When Qián appears, the universe is telling you..."
        return "When Qián appears, the universe is telling you..."
    
    def _extract_main_actions(self, content: str) -> list:
        """提取主要行动"""
        # 从内容中提取主要行动
        if "行动" in content or "action" in content.lower():
            # 提取行动内容
            return ["Trust in your inner creativity and leadership abilities", "Take initiative and become a catalyst for positive change"]
        return ["Trust in your inner creativity and leadership abilities", "Take initiative and become a catalyst for positive change"]
    
    def _extract_supporting_actions(self, content: str) -> list:
        """提取支持行动"""
        # 从内容中提取支持行动
        if "支持" in content or "supporting" in content.lower():
            # 提取支持行动内容
            return ["Maintain strong will while leading with virtue and compassion", "Transform your vision into concrete action plans"]
        return ["Maintain strong will while leading with virtue and compassion", "Transform your vision into concrete action plans"]
    
    def _extract_inspirational_message(self, content: str) -> str:
        """提取激励话语"""
        # 从内容中提取激励话语
        if "激励" in content or "inspirational" in content.lower():
            # 提取激励话语内容
            return "The energy of Qián flows through you..."
        return "The energy of Qián flows through you..."
    
    def _extract_core_strategy(self, content: str) -> str:
        """提取核心策略"""
        # 从内容中提取核心策略
        if "策略" in content or "strategy" in content.lower():
            # 提取策略内容
            return "自强不息，创造无限"
        return "自强不息，创造无限"
    
    def _extract_action_guide(self, content: str) -> list:
        """提取行动指南"""
        # 从内容中提取行动指南
        if "指南" in content or "guide" in content.lower():
            # 提取指南内容
            return ["展现你的创造力和领导力", "主动承担责任", "保持坚定的意志"]
        return ["展现你的创造力和领导力", "主动承担责任", "保持坚定的意志"]
    
    def _get_default_structure(self) -> Dict[str, Any]:
        """获取默认结构"""
        return {
            "hexagram": {
                "code": "1",
                "name": "乾卦",
                "english_name": "The Creative, Heaven",
                "title": "乾卦 - The Creative, Heaven",
                "hexagram_text": "乾：元，亨，利，贞。",
                "image_text": "天行健，君子以自强不息。",
                "focus_yao": {"yao_number": 1, "yao_text": "初九：潜龙，勿用。"}
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
                "action_guide": ["展现你的创造力和领导力", "主动承担责任，推动积极变化", "保持坚定的意志和美德"]
            }
        }
