#!/usr/bin/env python3
"""
Kimi版本的蓝图服务
使用Kimi替代Gemini进行五行计算
"""

import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any
from app.services.kimi_service import KimiService
from app.utils.logger import MyLogger
from app.core.cache import VersionedCacheManager
from app.models.blueprint import BlueprintResult
from app.core.database import Database

class KimiBlueprintService:
    """Kimi版本的蓝图服务类"""
    
    def __init__(self):
        self.ai_service = KimiService()
        self.cache_manager = VersionedCacheManager()
        self.logger = MyLogger("kimi_blueprint_service")
    
    def _generate_cache_key(self, user_id: str, user_profile: dict) -> str:
        """生成缓存键"""
        # 基于用户ID和关键信息生成缓存键
        key_data = {
            'user_id': user_id,
            'birth_date': user_profile.get('birth_date'),
            'birth_time': user_profile.get('birth_time'),
            'birth_location': user_profile.get('birth_location'),
            'gender': user_profile.get('gender')
        }
        return f"kimi_blueprint_quick_{hash(str(sorted(key_data.items())))}"
    
    def _parse_blueprint_quick_response(self, ai_content: str) -> Dict[str, Any]:
        """解析快速五行计算结果响应 - 与原有服务保持一致"""
        # 尝试解析AI返回的JSON内容
        try:
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
            self.logger.warning(f"无法解析Kimi响应，使用默认结构: {ai_content[:100]}")
            
        except Exception as e:
            self.logger.error(f"解析Kimi响应失败: {e}, 内容: {ai_content[:100]}")
        
        # 返回默认的五行结构
        return {
            "core_energy_field": {
                "title": "Elemental Composition",
                "description": "These are the five fundamental energies that form your inner world.",
                "chart_data": [
                    {"axis": "Metal", "value": 20},
                    {"axis": "Wood", "value": 20},
                    {"axis": "Water", "value": 20},
                    {"axis": "Fire", "value": 20},
                    {"axis": "Earth", "value": 20}
                ]
            }
        }
    
    async def generate_blueprint_quick(self, user_id: str, user_profile: dict):
        """快速生成五行计算结果 - 完全按照原有BlueprintService的模式"""
        try:
            # 调用 Kimi 服务快速生成五行结果
            result = await self.ai_service.generate_blueprint_quick(user_profile)
            
            if not result.get("success"):
                raise Exception(f"Kimi 快速生成失败: {result.get('message')}")
            
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
            
            self.logger.info(f"Kimi快速五行生成完成，任务ID: {blueprint_result.task_id}")
            return blueprint_result
            
        except Exception as e:
            self.logger.error(f"Kimi快速生成五行结果失败: {e}")
            raise Exception(f"Kimi快速生成五行结果失败: {str(e)}")

    async def generate_blueprint_complete(self, user_id: str, user_profile: dict):
        """基于五行结果生成完整蓝图 - Kimi版本（与原始服务完全一致）"""
        try:
            # 获取现有的五行结果（与原始服务完全一致）
            existing_blueprint = await Database.find_one("blueprint_results", {"user_id": user_id})
            if not existing_blueprint or existing_blueprint.get("generation_status") != "partial":
                raise Exception("没有找到部分完成的五行结果")
            
            # 调用 Kimi AI 服务生成完整内容（与原始服务完全一致）
            result = await self.ai_service.generate_blueprint_complete(
                user_profile, 
                existing_blueprint.get("quick_data")
            )
            
            if not result.get("success"):
                raise Exception(f"Kimi AI 完整生成失败: {result.get('message')}")
            
            # 解析 AI 响应，获取完整内容
            complete_data = self._parse_blueprint_complete_response(result.get("ai_content", ""))
            
            # 构建完整的inner_blueprint结构，包含五行数据和完整分析
            inner_blueprint = {
                "core_energy_field": existing_blueprint.get("quick_data", {}).get("core_energy_field", {}),
                **complete_data  # 添加完整蓝图数据
            }
            
            # 更新现有记录，添加完整内容（与原始服务完全一致）
            update_data = {
                "generation_status": "complete",  # 标记为完成
                "task_id": None,  # 清空任务ID
                "inner_blueprint": inner_blueprint,  # 添加完整内容（包含五行+完整分析）
                "updated_at": datetime.now()
            }
            
            await Database.update_one(
                "blueprint_results",
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            # 获取更新后的完整记录
            updated_blueprint = await Database.find_one("blueprint_results", {"user_id": user_id})
            
            self.logger.info(f"用户 {user_id} Kimi完整蓝图生成成功")
            return BlueprintResult(**updated_blueprint)
                
        except Exception as e:
            self.logger.error(f"Kimi完整蓝图生成失败: {e}")
            raise

    def _parse_blueprint_complete_response(self, ai_content: str) -> Dict[str, Any]:
        """解析完整蓝图响应"""
        try:
            parsed_data = None
            
            if ai_content.strip().startswith('{'):
                parsed_data = json.loads(ai_content.strip())
            elif '```json' in ai_content:
                start = ai_content.find('```json') + 7
                end = ai_content.find('```', start)
                json_content = ai_content[start:end].strip()
                parsed_data = json.loads(json_content)
            
            # 如果解析成功，确保数据结构正确
            if parsed_data:
                # 直接返回解析的数据，它应该符合完整蓝图的格式
                return parsed_data
            
            self.logger.warning(f"无法解析Kimi完整蓝图响应，使用默认结构: {ai_content[:100]}")
            
        except Exception as e:
            self.logger.error(f"解析Kimi完整蓝图响应失败: {e}, 内容: {ai_content[:100]}")
        
        # 返回默认的完整结构
        return {
            "core_essence": {
                "title": "Core Essence",
                "description": "Your core personality traits based on Five Elements analysis."
            },
            "natural_strengths": {
                "title": "Natural Strengths",
                "strengths": ["Balanced energy", "Adaptability", "Inner wisdom"]
            },
            "growth_areas": {
                "title": "Growth Areas",
                "analysis": "Areas for personal development and growth.",
                "balance_path": {
                    "title": "Path to Balance",
                    "suggestions": ["Enhance self-awareness", "Practice mindfulness", "Develop emotional intelligence"]
                }
            },
            "life_journey_curve": {
                "title": "Life Journey Forecast",
                "description": "Your energy will experience natural fluctuations in the coming years.",
                "chart_data": [
                    {
                        "year": 2025,
                        "energy_level": 75,
                        "is_turning_point": True,
                        "icon_id": "star",
                        "event_description": "Year of growth and opportunity"
                    },
                    {
                        "year": 2026,
                        "energy_level": 80,
                        "is_turning_point": False,
                        "icon_id": "arrow-up",
                        "event_description": "Continued progress and development"
                    },
                    {
                        "year": 2027,
                        "energy_level": 85,
                        "is_turning_point": True,
                        "icon_id": "crown",
                        "event_description": "Peak achievement and recognition"
                    }
                ]
            }
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.ai_service.cleanup()


# 单例模式
_kimi_blueprint_service_instance = None

async def get_kimi_blueprint_service() -> KimiBlueprintService:
    """获取Kimi蓝图服务实例"""
    global _kimi_blueprint_service_instance
    if _kimi_blueprint_service_instance is None:
        _kimi_blueprint_service_instance = KimiBlueprintService()
    return _kimi_blueprint_service_instance

async def cleanup_kimi_blueprint_service():
    """清理Kimi蓝图服务资源"""
    global _kimi_blueprint_service_instance
    if _kimi_blueprint_service_instance is not None:
        await _kimi_blueprint_service_instance.cleanup()
        _kimi_blueprint_service_instance = None
