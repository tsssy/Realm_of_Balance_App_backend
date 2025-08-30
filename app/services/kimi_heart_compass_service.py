#!/usr/bin/env python3
"""
Kimi版本的Heart Compass服务
使用Kimi AI替代Gemini进行指导生成
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.kimi_service import KimiService
from app.utils.logger import MyLogger
from app.core.database import Database
from app.models.heart_compass import HeartCompassRecord

logger = MyLogger("kimi_heart_compass_service")

class KimiHeartCompassService:
    """Kimi版本的Heart Compass服务类"""
    
    def __init__(self):
        self.ai_service = KimiService()
        self.logger = logger
    
    async def seek_guidance(self, user_id: str, question: str, user_profile: Dict[str, Any]):
        """寻求指导 - Kimi版本"""
        self.logger.info(f"用户 {user_id} 寻求Kimi指导: {question[:50]}...")
        
        try:
            # 调用Kimi服务生成指导（与原始服务完全一致的方法调用）
            result = await self.ai_service.seek_heart_compass_guidance(question, user_profile)
            
            if not result.get("success"):
                raise Exception(f"Kimi Heart Compass生成失败: {result.get('message')}")
            
            # 解析AI响应，构建结构化数据（与原始服务一致）
            guidance_data = self._parse_heart_compass_ai_response(result.get("ai_content", ""))
            
            # 字段兼容：旧字段名转换为新字段名（与原始服务完全一致）
            if "dialogue_flow" in guidance_data and "insight" not in guidance_data:
                guidance_data["insight"] = guidance_data.pop("dialogue_flow")
            if "decision_protocol" in guidance_data and "summary" not in guidance_data:
                _dp = guidance_data.pop("decision_protocol")
                if isinstance(_dp, dict):
                    _dp["title"] = "Summary"
                guidance_data["summary"] = _dp
            
            # 构建完整的指导记录（与原始服务完全一致）
            guidance_record = HeartCompassRecord(
                user_id=user_id,
                question=question,
                **guidance_data,
                ai_generated=result.get("ai_content", ""),
                created_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("heart_compass_records", guidance_record.dict())
            
            self.logger.info(f"用户 {user_id} Kimi Heart Compass 指导生成成功")
            return guidance_record
            
        except Exception as e:
            self.logger.error(f"获取 Kimi Heart Compass 指导失败: {e}")
            raise
    
    async def ask_again(self, user_id: str, question: str, user_profile: Dict[str, Any], previous_guidance_id: str = None):
        """重新提问 - Kimi版本（与原始服务完全一致）"""
        self.logger.info(f"用户 {user_id} 向Kimi重新提问: {question[:50]}...")
        
        try:
            # 构建上下文，包含之前的问题信息（与原始服务完全一致）
            context = {
                "question": question,
                "user_profile": user_profile,
                "is_follow_up": True
            }
            
            # 如果有之前的指导ID，获取相关信息（与原始服务完全一致）
            if previous_guidance_id:
                from bson import ObjectId
                # 转换字符串ID为ObjectId
                object_id = ObjectId(previous_guidance_id)
                previous_guidance = await Database.find_one("heart_compass_records", {"_id": object_id})
                if previous_guidance and previous_guidance.get("user_id") == user_id:
                    context["previous_guidance"] = {
                        "hexagram": previous_guidance.get("hexagram"),
                        "question": previous_guidance.get("question"),
                        "guidance_summary": previous_guidance.get("summary", {}).get("core_strategy", "")
                    }
            
            # 调用 Kimi AI 服务获取深入指导（与原始服务完全一致）
            result = await self.ai_service.seek_heart_compass_guidance(question, user_profile)
            
            if not result.get("success"):
                raise Exception(f"Kimi AI 生成失败: {result.get('message')}")
            
            # 解析 AI 响应，构建结构化数据（与原始服务一致）
            guidance_data = self._parse_heart_compass_ai_response(result.get("ai_content", ""))
            
            # 构建完整的指导记录（与原始服务完全一致）
            guidance_record = HeartCompassRecord(
                user_id=user_id,
                question=question,
                **guidance_data,
                ai_generated=result.get("ai_content", ""),
                created_at=datetime.now()
            )
            
            # 保存到数据库
            await Database.insert_one("heart_compass_records", guidance_record.dict())
            
            self.logger.info(f"用户 {user_id} Kimi Heart Compass 重新提问指导生成成功")
            return guidance_record
            
        except Exception as e:
            self.logger.error(f"Kimi重新提问失败: {e}")
            raise
    
    async def get_guidance_history(self, user_id: str, page: int = 1, limit: int = 10):
        """获取指导历史"""
        try:
            skip = (page - 1) * limit
            
            # 获取记录总数
            total = await Database.count_documents("heart_compass_records", {"user_id": user_id})
            
            # 获取分页记录
            records = await Database.find(
                "heart_compass_records",
                {"user_id": user_id},
                skip=skip,
                limit=limit,
                sort=[("created_at", -1)]
            )
            
            return {
                "records": [HeartCompassRecord(**record) for record in records],
                "total": total,
                "page": page,
                "limit": limit,
                "has_more": (skip + len(records)) < total
            }
            
        except Exception as e:
            self.logger.error(f"获取Kimi指导历史失败: {e}")
            raise Exception(f"获取Kimi指导历史失败: {str(e)}")
    
    async def get_guidance_by_id(self, guidance_id: str):
        """根据ID获取指导记录"""
        try:
            record = await Database.find_one("heart_compass_records", {"guidance_id": guidance_id})
            if record:
                return HeartCompassRecord(**record)
            return None
            
        except Exception as e:
            self.logger.error(f"获取Kimi指导记录失败: {e}")
            raise Exception(f"获取Kimi指导记录失败: {str(e)}")
    
    async def delete_guidance(self, guidance_id: str, user_id: str):
        """删除指导记录"""
        try:
            result = await Database.delete_one(
                "heart_compass_records", 
                {"guidance_id": guidance_id, "user_id": user_id}
            )
            return result.deleted_count > 0
            
        except Exception as e:
            self.logger.error(f"删除Kimi指导记录失败: {e}")
            raise Exception(f"删除Kimi指导记录失败: {str(e)}")
    
    def _parse_heart_compass_ai_response(self, ai_content: str) -> Dict[str, Any]:
        """解析Heart Compass响应"""
        try:
            if ai_content.strip().startswith('{'):
                return json.loads(ai_content.strip())
            
            if '```json' in ai_content:
                start = ai_content.find('```json') + 7
                end = ai_content.find('```', start)
                json_content = ai_content[start:end].strip()
                return json.loads(json_content)
            
            self.logger.warning(f"无法解析Kimi Heart Compass响应，使用默认结构: {ai_content[:100]}")
            
        except Exception as e:
            self.logger.error(f"解析Kimi Heart Compass响应失败: {e}, 内容: {ai_content[:100]}")
        
        return {
            "hexagram_info": {
                "name": "指导卦象",
                "description": "基于您的问题和八字的指导卦象"
            },
            "dialogue_flow": {
                "understanding": "我理解您的困惑",
                "analysis": "让我为您分析当前情况",
                "guidance": "根据五行分析，建议您...",
                "action": "具体的行动建议"
            },
            "deep_wisdom": {
                "content": "基于古典智慧的深层指导"
            },
            "action_guide": {
                "immediate_actions": ["立即可以采取的行动"],
                "long_term_strategy": "长期策略建议"
            },
            "decision_protocol": {
                "key_factors": ["决策的关键因素"],
                "decision_framework": "决策框架建议"
            }
        }
    
    async def cleanup(self):
        """清理资源"""
        await self.ai_service.cleanup()


# 单例模式
_kimi_heart_compass_service_instance = None

async def get_kimi_heart_compass_service() -> KimiHeartCompassService:
    """获取Kimi Heart Compass服务实例"""
    global _kimi_heart_compass_service_instance
    if _kimi_heart_compass_service_instance is None:
        _kimi_heart_compass_service_instance = KimiHeartCompassService()
    return _kimi_heart_compass_service_instance
