#!/usr/bin/env python3
"""
OpenAI版本的蓝图服务
使用GPT-4o-mini替代Gemini进行五行计算
"""

import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any
from app.services.openai_service import OpenAIService
from app.utils.logger import MyLogger
from app.core.cache import VersionedCacheManager
from app.models.blueprint import BlueprintResult
from app.core.database import Database

class OpenAIBlueprintService:
    """OpenAI版本的蓝图服务类"""
    
    def __init__(self):
        self.ai_service = OpenAIService()
        self.cache_manager = VersionedCacheManager()
        self.logger = MyLogger("openai_blueprint_service")
    
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
        return f"openai_blueprint_quick_{hash(str(sorted(key_data.items())))}"
    
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
            self.logger.warning(f"无法解析OpenAI响应，使用默认结构: {ai_content[:100]}")
            
        except Exception as e:
            self.logger.error(f"解析OpenAI响应失败: {e}, 内容: {ai_content[:100]}")
        
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
            # 调用 OpenAI 服务快速生成五行结果
            result = await self.ai_service.generate_blueprint_quick(user_profile)
            
            if not result.get("success"):
                raise Exception(f"OpenAI 快速生成失败: {result.get('message')}")
            
            # 解析 AI 响应，获取五行数据
            quick_data = self._parse_blueprint_quick_response(result.get("message", ""))
            
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
            
            self.logger.info(f"OpenAI快速五行生成完成，任务ID: {blueprint_result.task_id}")
            return blueprint_result
            
        except Exception as e:
            self.logger.error(f"OpenAI快速生成五行结果失败: {e}")
            raise Exception(f"OpenAI快速生成五行结果失败: {str(e)}")
    
    async def cleanup(self):
        """清理资源"""
        await self.ai_service.cleanup()


# 单例模式
_openai_blueprint_service_instance = None

async def get_openai_blueprint_service() -> OpenAIBlueprintService:
    """获取OpenAI蓝图服务实例"""
    global _openai_blueprint_service_instance
    if _openai_blueprint_service_instance is None:
        _openai_blueprint_service_instance = OpenAIBlueprintService()
    return _openai_blueprint_service_instance

async def cleanup_openai_blueprint_service():
    """清理OpenAI蓝图服务资源"""
    global _openai_blueprint_service_instance
    if _openai_blueprint_service_instance is not None:
        await _openai_blueprint_service_instance.cleanup()
        _openai_blueprint_service_instance = None
