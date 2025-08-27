from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .base import BaseResponse, ListResponse, BaseDBModel, Hexagram as BaseHexagram

class FocusYao(BaseModel):
    """焦点爻辞模型"""
    yao_number: int = Field(..., ge=1, le=6, description="爻位 (1-6)")
    yao_text: str = Field(..., description="爻辞内容")

class Hexagram(BaseHexagram):
    """Heart Compass卦象信息模型 (扩展基础卦象)"""
    code: str = Field(..., description="卦序 (如 '1')")
    focus_yao: FocusYao = Field(..., description="焦点爻辞")

class Insight(BaseModel):
    """洞察模型（原 dialogue_flow）"""
    revelation: str = Field(..., description="启示 - 短诗或箴言")
    analysis: str = Field(..., description="分析 - 基于象辞的处境分析")
    guidance: str = Field(..., description="指引 - 行动方向或心态建议")
    encouragement: str = Field(..., description="鼓励 - 温暖治愈的话语")

class DeepWisdom(BaseModel):
    """深层智慧模型"""
    title: str = Field(..., description="标题")
    explanation: str = Field(..., description="详细解释")
    philosophical_meaning: str = Field(..., description="哲学含义")
    personal_interpretation: str = Field(..., description="个人解读")

class ActionGuide(BaseModel):
    """行动指南模型"""
    title: str = Field(..., description="标题")
    main_actions: List[str] = Field(..., description="主要行动")
    supporting_actions: List[str] = Field(..., description="支持行动")
    inspirational_message: str = Field(..., description="激励话语")

class Summary(BaseModel):
    """总结模型（原 decision_protocol）"""
    title: str = Field(..., description="固定标题，应为 'Summary'")
    situation_code: str = Field(..., description="情境代码 (如 '乾卦 (#1)')")
    core_strategy: str = Field(..., description="核心策略 (四字短语)")
    action_guide: List[str] = Field(..., description="行动指南 (2-3条具体建议)")

class HeartCompassRecord(BaseDBModel):
    """Heart Compass 指导记录模型"""
    user_id: str = Field(..., description="关联用户ID")
    question: str = Field(..., description="用户问题/困惑文本")
    hexagram: Hexagram = Field(..., description="对应的卦象信息")
    insight: Insight = Field(..., description="洞察 (四个环节)")
    deep_wisdom: DeepWisdom = Field(..., description="深层智慧")
    action_guide: ActionGuide = Field(..., description="行动指南")
    summary: Summary = Field(..., description="总结")
    ai_generated: str = Field(..., description="Gemini AI 生成的完整指导")

class HeartCompassRequest(BaseModel):
    """获取指导请求模型"""
    user_id: str = Field(..., description="用户ID")
    question: str = Field(..., description="用户的具体困惑文本")
    user_profile: dict = Field(..., description="用户信息，用于个性化分析")

class HeartCompassResponse(BaseResponse[HeartCompassRecord]):
    """Heart Compass 响应模型"""
    pass

class HeartCompassHistoryResponse(ListResponse[HeartCompassRecord]):
    """指导历史响应模型"""
    pass

class AskAgainRequest(BaseModel):
    """重新提问请求模型"""
    user_id: str = Field(..., description="用户ID")
    question: str = Field(..., description="新的问题或深入探讨")
    previous_guidance_id: Optional[str] = Field(None, description="之前的指导ID，用于上下文关联")
