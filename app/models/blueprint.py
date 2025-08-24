from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import BaseResponse, BaseDBModel, UserProfileBase

class BaziPillar(BaseModel):
    """八字柱模型"""
    heavenly_stem: str = Field(..., description="天干")
    earthly_branch: str = Field(..., description="地支")

class Bazi(BaseModel):
    """八字模型"""
    year_pillar: BaziPillar = Field(..., description="年柱")
    month_pillar: BaziPillar = Field(..., description="月柱")
    day_pillar: BaziPillar = Field(..., description="日柱")
    hour_pillar: BaziPillar = Field(..., description="时柱")

class ElementalStrength(BaseModel):
    """五行强度模型"""
    strength: float = Field(..., ge=0, le=100, description="强度值 0-100")
    characteristics: List[str] = Field(..., description="特征描述")

class ElementalProfile(BaseModel):
    """五行分析模型"""
    metal: ElementalStrength = Field(..., description="金")
    wood: ElementalStrength = Field(..., description="木")
    water: ElementalStrength = Field(..., description="水")
    fire: ElementalStrength = Field(..., description="火")
    earth: ElementalStrength = Field(..., description="土")

class Compatibility(BaseModel):
    """兼容性分析模型"""
    best_elements: List[str] = Field(..., description="最佳元素")
    challenging_elements: List[str] = Field(..., description="挑战元素")

class CoreAnalysis(BaseModel):
    """核心分析模型"""
    dominant_element: str = Field(..., description="主导元素")
    weakest_element: str = Field(..., description="最弱元素")
    personality_traits: List[str] = Field(..., description="性格特征")
    life_guidance: str = Field(..., description="人生指导")
    compatibility: Compatibility = Field(..., description="兼容性分析")

class ChartDataPoint(BaseModel):
    """图表数据点模型"""
    axis: str = Field(..., description="坐标轴名称")
    value: float = Field(..., ge=0, le=100, description="数值 0-100")

class CoreEnergyField(BaseModel):
    """核心能量场模型"""
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    chart_data: List[ChartDataPoint] = Field(..., description="雷达图数据")

class CoreEssence(BaseModel):
    """核心本质模型"""
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")

class NaturalStrengths(BaseModel):
    """天生优势模型"""
    title: str = Field(..., description="标题")
    strengths: List[str] = Field(..., description="优势列表")

class BalancePath(BaseModel):
    """平衡之道模型"""
    title: str = Field(..., description="标题")
    suggestions: List[str] = Field(..., description="建议列表")

class GrowthAreas(BaseModel):
    """成长挑战模型"""
    title: str = Field(..., description="标题")
    analysis: str = Field(..., description="分析内容")
    balance_path: BalancePath = Field(..., description="平衡之道")

class LifeJourneyDataPoint(BaseModel):
    """生命曲线数据点模型"""
    year: int = Field(..., description="年份")
    energy_level: float = Field(..., ge=0, le=100, description="能量值 0-100")
    is_turning_point: bool = Field(..., description="是否为转折点")
    icon_id: str = Field(..., description="图标标识")
    event_description: str = Field(..., description="年度描述")

class LifeJourneyCurve(BaseModel):
    """生命曲线模型"""
    title: str = Field(..., description="标题")
    description: str = Field(..., description="描述")
    chart_data: List[LifeJourneyDataPoint] = Field(..., description="曲线图数据")

class InnerBlueprint(BaseModel):
    """内在蓝图模型"""
    core_energy_field: CoreEnergyField = Field(..., description="核心能量场")
    core_essence: CoreEssence = Field(..., description="核心本质")
    natural_strengths: NaturalStrengths = Field(..., description="天生优势")
    growth_areas: GrowthAreas = Field(..., description="成长挑战")
    life_journey_curve: LifeJourneyCurve = Field(..., description="生命曲线")

class BlueprintResult(BaseDBModel):
    """算命结果模型"""
    user_id: str = Field(..., description="用户ID")
    
    # 新增字段：生成状态和任务ID
    generation_status: str = Field("complete", description="生成状态: partial|complete")
    task_id: Optional[str] = Field(None, description="后台任务ID")
    
    # 快速计算结果（可选）
    quick_data: Optional[Dict[str, Any]] = Field(None, description="快速计算的五行数据")
    
    # 原有字段（现在都是可选的，支持部分生成）
    bazi: Optional[Bazi] = Field(None, description="八字排盘")
    elemental_profile: Optional[ElementalProfile] = Field(None, description="五行分析")
    core_analysis: Optional[CoreAnalysis] = Field(None, description="核心分析")
    inner_blueprint: Optional[InnerBlueprint] = Field(None, description="内在蓝图")
    ai_analysis: Optional[str] = Field(None, description="AI 分析内容")

class BlueprintGenerateRequest(BaseModel):
    """生成算命结果请求模型"""
    user_id: str = Field(..., description="用户ID")
    user_profile: Dict[str, Any] = Field(..., description="用户信息")

class BlueprintResponse(BaseResponse[BlueprintResult]):
    """算命结果响应模型"""
    pass
