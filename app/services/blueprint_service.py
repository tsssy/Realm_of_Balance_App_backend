import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import Database
from app.core.cache import versioned_cache, VersionedCacheManager
from app.models.blueprint import BlueprintResult, BlueprintGenerateRequest, BlueprintResponse
from app.services.ai_service import AIService
from app.config.prompt_config import PromptType
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
                generation_status="complete",  # 标记为完整完成
                task_id=None,  # 完整生成没有任务ID
                quick_data=None,  # 完整生成不需要快速数据
                bazi=blueprint_data.get("bazi"),
                elemental_profile=blueprint_data.get("elemental_profile"),
                core_analysis=blueprint_data.get("core_analysis"),
                inner_blueprint=blueprint_data.get("inner_blueprint"),
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
    
    async def generate_blueprint_quick(self, user_id: str, user_profile: dict):
        """快速生成五行计算结果"""
        try:
            # 调用 AI 服务快速生成五行结果
            result = await self.ai_service.generate_blueprint_quick(user_profile)
            
            if not result.get("success"):
                raise Exception(f"AI 快速生成失败: {result.get('message')}")
            
            # 解析 AI 响应，获取五行数据
            quick_data = self._parse_blueprint_quick_response(result.get("ai_content", ""))
            
            # 构建部分算命结果（只有五行数据）
            blueprint_result = BlueprintResult(
                user_id=user_id,
                generation_status="partial",  # 标记为部分完成
                task_id=f"task_{uuid.uuid4().hex[:8]}",  # 生成任务ID
                quick_data=quick_data,  # 存储五行数据
                bazi=None,  # 部分生成没有八字数据
                elemental_profile=None,  # 部分生成没有五行分析
                core_analysis=None,  # 部分生成没有核心分析
                inner_blueprint=None,  # 部分生成没有内在蓝图
                ai_analysis=None,  # 部分生成没有AI分析
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("blueprint_results", blueprint_result.dict())
            
            # 失效相关缓存
            await self.cache_manager.invalidate_entity_cache(
                user_id, "blueprint", "五行结果快速生成"
            )
            
            logger.info(f"用户 {user_id} 五行结果快速生成成功")
            return blueprint_result
            
        except Exception as e:
            logger.error(f"快速生成五行结果失败: {e}")
            raise
    
    async def generate_blueprint_complete(self, user_id: str, user_profile: dict):
        """基于五行结果生成完整蓝图"""
        try:
            # 获取现有的五行结果
            existing_blueprint = await self.get_blueprint(user_id)
            if not existing_blueprint or existing_blueprint.generation_status != "partial":
                raise Exception("没有找到部分完成的五行结果")
            
            # 调用 AI 服务生成完整内容
            result = await self.ai_service.generate_blueprint_complete(
                user_profile, 
                existing_blueprint.quick_data
            )
            
            if not result.get("success"):
                raise Exception(f"AI 完整生成失败: {result.get('message')}")
            
            # 解析 AI 响应，获取完整内容
            complete_data = self._parse_blueprint_complete_response(result.get("ai_content", ""), existing_blueprint.quick_data)
            
            # 更新现有记录，添加完整内容
            update_data = {
                "generation_status": "complete",  # 标记为完成
                "task_id": None,  # 清空任务ID
                "inner_blueprint": complete_data,  # 添加完整内容
                "updated_at": datetime.now()
            }
            
            await Database.update_one(
                "blueprint_results",
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            # 失效相关缓存
            await self.cache_manager.invalidate_entity_cache(
                user_id, "blueprint", "完整蓝图生成"
            )
            
            logger.info(f"用户 {user_id} 完整蓝图生成成功")
            return await self.get_blueprint(user_id)
            
        except Exception as e:
            logger.error(f"生成完整蓝图失败: {e}")
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
    
    async def get_blueprint_status(self, user_id: str) -> Dict[str, Any]:
        """获取用户的蓝图生成状态"""
        try:
            blueprint_result = await self.get_blueprint(user_id)
            
            if not blueprint_result:
                return {
                    "user_id": user_id,
                    "status": "not_found",
                    "message": "没有找到蓝图数据"
                }
            
            # 构建状态信息
            status_info = {
                "user_id": user_id,
                "generation_status": blueprint_result.generation_status,
                "task_id": blueprint_result.task_id,
                "has_quick_data": blueprint_result.quick_data is not None,
                "has_complete_data": blueprint_result.inner_blueprint is not None,
                "created_at": blueprint_result.created_at,
                "updated_at": blueprint_result.updated_at
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"获取蓝图状态失败: {e}")
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
    
    def _parse_blueprint_quick_response(self, ai_content: str) -> Dict[str, Any]:
        """解析快速五行计算结果响应"""
        # 尝试解析AI返回的JSON内容
        try:
            import json
            # 如果AI直接返回JSON，尝试解析
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content.strip())
            
            # 如果AI返回的是包含```json的格式，提取JSON部分
            if '```json' in ai_content:
                start = ai_content.find('```json') + 7
                end = ai_content.find('```', start)
                json_content = ai_content[start:end].strip()
                return json.loads(json_content)
            
            # 如果找不到JSON，使用默认结构
            logger.warning(f"无法解析AI响应，使用默认结构: {ai_content[:100]}")
            
        except Exception as e:
            logger.error(f"解析AI响应失败: {e}, 内容: {ai_content[:100]}")
        
        # 降级到硬编码数据
        return {
            "core_energy_field": {
                "title": "核心能量场 | Elemental Composition", 
                "description": "这是构成你内在世界的五种基本能量。",
                "chart_data": [
                    {"axis": "金 | Metal", "value": 25},
                    {"axis": "木 | Wood", "value": 15},
                    {"axis": "水 | Water", "value": 30},
                    {"axis": "火 | Fire", "value": 20},
                    {"axis": "土 | Earth", "value": 10}
                ]
            }
        }
    
    def _parse_blueprint_complete_response(self, ai_content: str, quick_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """解析完整蓝图响应"""
        # 尝试解析AI返回的JSON内容
        try:
            import json
            # 如果AI直接返回JSON，尝试解析
            if ai_content.strip().startswith('{'):
                parsed_data = json.loads(ai_content.strip())
                # 确保包含必要的字段
                if 'core_essence' in parsed_data and 'natural_strengths' in parsed_data:
                    # 从quick_data获取core_energy_field
                    if quick_data and 'core_energy_field' in quick_data:
                        parsed_data['core_energy_field'] = quick_data['core_energy_field']
                    return parsed_data
            
            # 如果AI返回的是包含```json的格式，提取JSON部分
            if '```json' in ai_content:
                start = ai_content.find('```json') + 7
                end = ai_content.find('```', start)
                json_content = ai_content[start:end].strip()
                parsed_data = json.loads(json_content)
                # 确保包含必要的字段
                if 'core_essence' in parsed_data and 'natural_strengths' in parsed_data:
                    # 从quick_data获取core_energy_field
                    if quick_data and 'core_energy_field' in quick_data:
                        parsed_data['core_energy_field'] = quick_data['core_energy_field']
                    return parsed_data
            
            # 如果找不到有效的JSON，使用默认结构
            logger.warning(f"无法解析AI响应，使用默认结构: {ai_content[:100]}")
            
        except Exception as e:
            logger.error(f"解析AI响应失败: {e}, 内容: {ai_content[:100]}")
        
        # 降级到硬编码数据（保持兼容性）
        core_energy_field = quick_data.get("core_energy_field") if quick_data else {
            "title": "核心能量场 | Elemental Composition",
            "description": "这是构成你内在世界的五种基本能量。",
            "chart_data": [
                {"axis": "金 | Metal", "value": 25},
                {"axis": "木 | Wood", "value": 15},
                {"axis": "水 | Water", "value": 30},
                {"axis": "火 | Fire", "value": 20},
                {"axis": "土 | Earth", "value": 10}
            ]
        }
        
        return {
            "core_energy_field": core_energy_field,
            "core_essence": {
                "title": "核心本质 | Core Essence",
                "description": "你的核心能量如水，深邃、包容且极具适应性。"
            },
            "natural_strengths": {
                "title": "天生优势 | Natural Strengths",
                "strengths": ["深刻的同理心", "灵活的适应力", "卓越的沟通力"]
            },
            "growth_areas": {
                "title": "成长挑战 | Growth Areas",
                "analysis": "你的能量构成中，'土'元素稍显不足。",
                "balance_path": {
                    "title": "平衡之道 | Path to Balance",
                    "suggestions": [
                        "每日5分钟接地冥想练习",
                        "定期与朋友家人沟通",
                        "制定明确的计划和目标"
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
