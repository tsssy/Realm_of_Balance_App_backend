import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import Database
from app.core.cache import versioned_cache, VersionedCacheManager
from app.models.blueprint import BlueprintResult, BlueprintGenerateRequest, BlueprintResponse
from app.services.ai_service import AIService
from app.utils.logger import MyLogger

logger = MyLogger("blueprint_service")

class BlueprintService:
    """算命分析服务类"""
    
    def __init__(self):
        self.ai_service = AIService()
        self.cache_manager = VersionedCacheManager()
    
    async def generate_blueprint(self, user_id: str, user_profile: dict):
        """生成算命结果"""
        try:
            # 调用 Gemini AI 生成算命结果
            result = await self.ai_service.generate_blueprint(user_profile)
            
            if not result.get("success"):
                raise Exception(f"AI 生成失败: {result.get('message')}")
            
            # 解析 AI 响应，构建结构化数据
            blueprint_data = self._parse_blueprint_ai_response(result.get("ai_content", ""))
            
            # 构建完整的算命结果
            blueprint_result = BlueprintResult(
                user_id=user_id,
                **blueprint_data,
                ai_analysis=result.get("ai_content", ""),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("blueprint_results", blueprint_result.dict())
            
            logger.info(f"用户 {user_id} 算命结果生成成功")
            return blueprint_result
            
        except Exception as e:
            logger.error(f"生成算命结果失败: {e}")
            raise
    
    async def get_blueprint(self, user_id: str) -> Optional[BlueprintResult]:
        """获取用户的算命结果"""
        try:
            blueprint_data = await Database.find_one("blueprint_results", {"user_id": user_id})
            if blueprint_data:
                return BlueprintResult(**blueprint_data)
            return None
        except Exception as e:
            logger.error(f"获取算命结果失败: {e}")
            raise
    
    async def regenerate_blueprint(self, user_id: str, user_profile: dict):
        """重新生成算命结果 - 自动失效缓存"""
        try:
            # 删除旧的算命结果
            await Database.delete_one("blueprint_results", {"user_id": user_id})
            
            # 失效相关缓存（自动递增版本号）
            await self.cache_manager.invalidate_entity_cache(
                user_id, "blueprint", "算命结果重新生成"
            )
            
            # 重新生成
            return await self.generate_blueprint(user_id, user_profile)
            
        except Exception as e:
            logger.error(f"重新生成算命结果失败: {e}")
            raise
    
    def _parse_blueprint_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """解析 AI 响应，构建结构化数据"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回基础结构
        return {
            "bazi": {
                "year_pillar": {"heavenly_stem": "庚", "earthly_branch": "午"},
                "month_pillar": {"heavenly_stem": "己", "earthly_branch": "未"},
                "day_pillar": {"heavenly_stem": "甲", "earthly_branch": "子"},
                "hour_pillar": {"heavenly_stem": "乙", "earthly_branch": "丑"}
            },
            "elemental_profile": {
                "metal": {"strength": 25, "characteristics": ["精确", "逻辑"]},
                "wood": {"strength": 15, "characteristics": ["生长", "创造"]},
                "water": {"strength": 30, "characteristics": ["智慧", "适应"]},
                "fire": {"strength": 20, "characteristics": ["热情", "领导"]},
                "earth": {"strength": 10, "characteristics": ["稳定", "承载"]}
            },
            "core_analysis": {
                "dominant_element": "water",
                "weakest_element": "earth",
                "personality_traits": ["深刻的同理心", "灵活的适应力", "卓越的沟通力"],
                "life_guidance": "你的人生指导内容",
                "compatibility": {
                    "best_elements": ["metal", "wood"],
                    "challenging_elements": ["earth"]
                }
            },
            "inner_blueprint": {
                "core_energy_field": {
                    "title": "核心能量场 | Elemental Composition",
                    "description": "这是构成你内在世界的五种基本能量。它们之间的平衡与互动，塑造了你独特的个性与天赋。",
                    "chart_data": [
                        {"axis": "金 | Metal", "value": 25},
                        {"axis": "木 | Wood", "value": 15},
                        {"axis": "水 | Water", "value": 30},
                        {"axis": "火 | Fire", "value": 20},
                        {"axis": "土 | Earth", "value": 10}
                    ]
                },
                "core_essence": {
                    "title": "核心本质 | Core Essence",
                    "description": "你的核心能量如水，深邃、包容且极具适应性。你天生拥有强大的直觉和洞察力，能够敏锐地感知环境与人心的流动。"
                },
                "natural_strengths": {
                    "title": "天生优势 | Natural Strengths",
                    "strengths": ["深刻的同理心", "灵活的适应力", "卓越的沟通力"]
                },
                "growth_areas": {
                    "title": "成长挑战 | Growth Areas",
                    "analysis": "你的能量构成中，'土'元素稍显不足。这可能意味着有时缺乏根基，没有归属感或安全感，在决断时犹豫不决，或在快节奏的生活中难以保持内心的稳定。",
                    "balance_path": {
                        "title": "平衡之道 | Path to Balance",
                        "suggestions": [
                            "每日5分钟接地冥想练习，感受身体与大地的连接",
                            "定期与朋友家人沟通，建立稳定的情感支持网络",
                            "制定明确的计划和目标，培养决策的果断性"
                        ]
                    }
                },
                "life_journey_curve": {
                    "title": "生命曲线 | Life Journey Forecast",
                    "description": "未来数年你的能量将经历自然波动。",
                    "chart_data": [
                        {
                            "year": 2025,
                            "energy_level": 55,
                            "is_turning_point": True,
                            "icon_id": "self_growth",
                            "event_description": "一个建立内在稳定和清晰规划的年份。"
                        }
                    ]
                }
            }
        }
    
    async def delete_blueprint(self, user_id: str) -> bool:
        """删除用户的算命结果"""
        try:
            result = await Database.delete_one("blueprint_results", {"user_id": user_id})
            
            # 失效相关缓存
            await self.cache_manager.invalidate_entity_cache(
                user_id, "blueprint", "算命结果删除"
            )
            
            logger.info(f"用户 {user_id} 算命结果已删除")
            return result > 0
            
        except Exception as e:
            logger.error(f"删除算命结果失败: {e}")
            return False
