from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .base import BaseResponse, ListResponse, BaseDBModel, Hexagram as BaseHexagram

class Hexagram(BaseHexagram):
    """Daily Fortune卦象模型 (扩展基础卦象)"""
    pinyin: str = Field(..., description="拼音")
    energy: str = Field(..., description="能量描述")
    luck: int = Field(..., ge=0, le=100, description="幸运指数 (0-100)")

class TimeAdvice(BaseModel):
    """时段建议模型"""
    period: str = Field(..., description="时间段")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    activity: str = Field(..., description="建议活动")
    description: str = Field(..., description="详细描述")
    energy: str = Field(..., description="能量状态")
    priority: str = Field(..., description="优先级")

class LuckyElements(BaseModel):
    """幸运元素模型"""
    color: str = Field(..., description="幸运颜色")
    direction: str = Field(..., description="幸运方向")
    number: int = Field(..., description="幸运数字")
    element: str = Field(..., description="幸运元素")
    gemstone: str = Field(..., description="幸运宝石")

class DailyFortune(BaseDBModel):
    """每日运势模型"""
    user_id: str = Field(..., description="关联用户ID")
    date: datetime = Field(..., description="运势日期")
    hexagram: Hexagram = Field(..., description="当日卦象")
    time_advice: List[TimeAdvice] = Field(..., description="时段建议")
    lucky_elements: LuckyElements = Field(..., description="幸运元素")
    personal_advice: str = Field(..., description="个性化建议")
    ai_generated: str = Field(..., description="Gemini AI 生成的运势内容")

class DailyFortuneRequest(BaseModel):
    """生成运势请求模型"""
    user_id: str = Field(..., description="用户ID")
    user_profile: dict = Field(..., description="用户信息")
    date: Optional[str] = Field(None, description="运势日期，格式：YYYY-MM-DD，默认为今天")

class DailyFortuneResponse(BaseResponse[DailyFortune]):
    """每日运势响应模型"""
    pass

class DailyFortuneHistoryResponse(ListResponse[DailyFortune]):
    """运势历史响应模型"""
    pass
