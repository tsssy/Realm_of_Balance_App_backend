from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar, List
from datetime import datetime

# 泛型类型变量
T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """统一的API响应基础模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class ListResponse(BaseModel, Generic[T]):
    """列表响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总数量")
    page: Optional[int] = Field(None, description="当前页码")
    page_size: Optional[int] = Field(None, description="每页大小")
    message: Optional[str] = Field(None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="请求失败")
    error: dict = Field(..., description="错误信息")
    message: str = Field(..., description="错误消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

class Hexagram(BaseModel):
    """统一的卦象模型"""
    code: Optional[str] = Field(None, description="卦序 (如 '1')")
    name: str = Field(..., description="卦名")
    pinyin: Optional[str] = Field(None, description="拼音")
    english_name: str = Field(..., description="英文含义")
    title: str = Field(..., description="完整标题")
    energy: Optional[str] = Field(None, description="能量描述")
    luck: Optional[int] = Field(None, ge=0, le=100, description="幸运指数 (0-100)")
    hexagram_text: str = Field(..., description="卦辞")
    image_text: str = Field(..., description="象辞")

class UserProfileBase(BaseModel):
    """统一的用户信息基础模型"""
    gender: str = Field(..., description="性别")
    birth_date: str = Field(..., description="出生日期，格式：YYYY-MM-DD")
    birth_time: str = Field(..., description="出生时间，格式：HH:MM")
    birth_location: str = Field(..., description="出生地点")

class BaseDBModel(BaseModel):
    """数据库模型基类"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB文档ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        from_attributes = True
        populate_by_name = True
        # 允许额外字段，便于数据库兼容
        extra = "allow"
