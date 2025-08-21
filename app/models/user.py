from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

from .base import BaseResponse, UserProfileBase, BaseDBModel

class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class UserProfile(UserProfileBase):
    """用户基本信息模型"""
    gender: Gender  # 覆盖基类的str类型为Gender枚举

class UserCreate(BaseModel):
    """创建用户请求模型"""
    device_id: str = Field(..., description="设备唯一标识")
    profile: UserProfile

class UserUpdate(BaseModel):
    """更新用户请求模型"""
    profile: UserProfile

class UserResponse(BaseModel):
    """用户响应模型"""
    user_id: str
    device_id: str
    gender: Gender
    birth_date: str
    birth_time: str
    birth_location: str
    is_new_user: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

class UserStatusData(BaseModel):
    """用户状态数据模型"""
    is_new_user: bool = Field(..., description="是否为新用户")
    user_profile: Optional[dict] = Field(None, description="用户信息")
    has_blueprint: bool = Field(..., description="是否有算命结果")

class UserStatusResponse(BaseResponse[UserStatusData]):
    """用户状态响应模型"""
    pass

class UserInDB(BaseDBModel):
    """数据库中的用户模型"""
    user_id: str = Field(..., description="用户ID")
    device_id: str = Field(..., description="设备ID")
    gender: Gender = Field(..., description="性别")
    birth_date: str = Field(..., description="出生日期")
    birth_time: str = Field(..., description="出生时间")
    birth_location: str = Field(..., description="出生地点")
    is_new_user: bool = Field(True, description="是否为新用户")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")

    # 数据库字段名（snake_case）
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
