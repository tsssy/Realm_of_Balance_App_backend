from fastapi import APIRouter, HTTPException, Header, Depends, Query
from typing import Optional

from app.models.user import UserCreate, UserUpdate, UserResponse, UserStatusResponse
from app.services.user_service import UserService
from app.utils.logger import MyLogger

logger = MyLogger("user_api")

router = APIRouter(prefix="/user", tags=["用户管理"])

# 依赖注入
async def get_user_service():
    return UserService()

@router.get("/status", response_model=UserStatusResponse)
async def check_user_status(
    device_id: Optional[str] = Query(None, description="设备唯一标识"),
    device_id_header: Optional[str] = Header(None, alias="Device-ID"),
    user_service: UserService = Depends(get_user_service)
):
    """
    检查用户状态
    
    - **device_id**: 设备唯一标识（查询参数或 Device-ID 头部）
    
    返回：
    - **is_new_user**: 是否为新用户
    - **user_profile**: 用户信息（老用户）
    - **has_blueprint**: 是否有算命结果
    """
    try:
        # 优先使用查询参数，如果没有则使用头部
        final_device_id = device_id or device_id_header
        
        if not final_device_id:
            raise HTTPException(
                status_code=400, 
                detail="必须提供 device_id 参数或 Device-ID 头部"
            )
        
        logger.info(f"检查用户状态: {final_device_id}")
        result = await user_service.check_user_status(final_device_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查用户状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    创建新用户
    
    - **device_id**: 设备唯一标识
    - **profile**: 用户基本信息
        - **gender**: 性别 (male/female/other)
        - **birth_date**: 出生日期 (YYYY-MM-DD)
        - **birth_time**: 出生时间 (HH:MM)
        - **birth_location**: 出生地点
    """
    try:
        logger.info(f"创建新用户: {user_create.device_id}")
        user = await user_service.create_user(user_create)
        
        return UserResponse(
            user_id=user.user_id,
            device_id=user.device_id,
            gender=user.gender,
            birth_date=user.birth_date,
            birth_time=user.birth_time,
            birth_location=user.birth_location,
            is_new_user=user.is_new_user,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )
    except ValueError as e:
        logger.warning(f"创建用户失败（参数错误）: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    更新用户信息
    
    - **user_id**: 用户ID
    - **profile**: 更新的用户信息
    """
    try:
        logger.info(f"更新用户信息: {user_id}")
        user = await user_service.update_user_profile(user_id, user_update)
        
        return UserResponse(
            user_id=user.user_id,
            device_id=user.device_id,
            gender=user.gender,
            birth_date=user.birth_date,
            birth_time=user.birth_time,
            birth_location=user.birth_location,
            is_new_user=user.is_new_user,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )
    except ValueError as e:
        logger.warning(f"更新用户失败（参数错误）: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新用户失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    获取用户信息
    
    - **user_id**: 用户ID
    """
    try:
        logger.info(f"获取用户信息: {user_id}")
        user = await user_service.get_user_profile(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return UserResponse(
            user_id=user.user_id,
            device_id=user.device_id,
            gender=user.gender,
            birth_date=user.birth_date,
            birth_time=user.birth_time,
            birth_location=user.birth_location,
            is_new_user=user.is_new_user,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    删除用户
    
    - **user_id**: 用户ID
    
    注意：此操作将删除用户的所有数据，包括算命结果、运势记录等
    """
    try:
        logger.info(f"删除用户: {user_id}")
        success = await user_service.delete_user(user_id)
        
        if success:
            return {"success": True, "message": "用户删除成功"}
        else:
            raise HTTPException(status_code=500, detail="用户删除失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/status")
async def get_user_status_summary(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    获取用户状态摘要
    
    - **user_id**: 用户ID
    
    返回用户的基本状态信息，包括是否有算命结果等
    """
    try:
        logger.info(f"获取用户状态摘要: {user_id}")
        status = await user_service.get_user_status_summary(user_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {"success": True, "data": status}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户状态摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
