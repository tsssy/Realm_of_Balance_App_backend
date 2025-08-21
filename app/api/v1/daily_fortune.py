from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from app.models.daily_fortune import (
    DailyFortuneRequest, DailyFortuneResponse, 
    DailyFortuneHistoryResponse
)
from app.services.daily_fortune_service import DailyFortuneService
from app.services.user_service import UserService
from app.utils.logger import MyLogger

logger = MyLogger("daily_fortune_api")

router = APIRouter(prefix="/daily-fortune", tags=["每日运势"])

# 依赖注入
async def get_daily_fortune_service():
    return DailyFortuneService()

async def get_user_service():
    return UserService()

@router.post("/generate", response_model=DailyFortuneResponse)
async def generate_daily_fortune(
    request: DailyFortuneRequest,
    daily_fortune_service: DailyFortuneService = Depends(get_daily_fortune_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    生成今日运势
    
    - **user_id**: 用户ID
    - **user_profile**: 用户信息，用于个性化分析
    - **date**: 运势日期（可选，默认为今天）
    
    返回个性化运势分析，包括：
    - 今日卦象
    - 时段建议
    - 幸运元素
    - 个性化建议
    """
    try:
        logger.info(f"生成用户 {request.user_id} 的运势，日期: {request.date or '今天'}")
        
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 生成运势
        daily_fortune = await daily_fortune_service.generate_daily_fortune(
            request.user_id,
            request.user_profile,
            request.date
        )
        
        return DailyFortuneResponse(
            success=True,
            data=daily_fortune
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成运势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/today", response_model=DailyFortuneResponse)
async def get_today_fortune(
    user_id: str,
    daily_fortune_service: DailyFortuneService = Depends(get_daily_fortune_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取今日运势
    
    - **user_id**: 用户ID
    
    如果今日运势不存在，将自动生成
    """
    try:
        logger.info(f"获取用户 {user_id} 的今日运势")
        
        # 验证用户是否存在
        user = await user_service.get_user_profile(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 构建用户信息
        user_profile = {
            "gender": user.gender,
            "birth_date": user.birth_date,
            "birth_time": user.birth_time,
            "birth_location": user.birth_location
        }
        
        # 获取今日运势
        daily_fortune = await daily_fortune_service.get_today_fortune(
            user_id, 
            user_profile
        )
        
        return DailyFortuneResponse(
            success=True,
            data=daily_fortune
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取今日运势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/history", response_model=DailyFortuneHistoryResponse)
async def get_fortune_history(
    user_id: str,
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    daily_fortune_service: DailyFortuneService = Depends(get_daily_fortune_service)
):
    """
    获取运势历史
    
    - **user_id**: 用户ID
    - **start_date**: 开始日期（可选）
    - **end_date**: 结束日期（可选）
    
    如果不指定日期范围，返回所有运势记录
    """
    try:
        logger.info(f"获取用户 {user_id} 的运势历史，范围: {start_date} 到 {end_date}")
        
        fortune_records = await daily_fortune_service.get_fortune_history(
            user_id, start_date, end_date
        )
        
        return DailyFortuneHistoryResponse(
            success=True,
            data=fortune_records,
            total=len(fortune_records),
            message=None
        )
        
    except Exception as e:
        logger.error(f"获取运势历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/date/{date}", response_model=DailyFortuneResponse)
async def get_fortune_by_date(
    user_id: str,
    date: str,
    daily_fortune_service: DailyFortuneService = Depends(get_daily_fortune_service)
):
    """
    获取指定日期的运势
    
    - **user_id**: 用户ID
    - **date**: 日期，格式：YYYY-MM-DD
    
    返回指定日期的运势记录
    """
    try:
        logger.info(f"获取用户 {user_id} 的 {date} 运势")
        
        daily_fortune = await daily_fortune_service.get_fortune_by_date(user_id, date)
        
        if not daily_fortune:
            raise HTTPException(status_code=404, detail="该日期的运势不存在")
        
        return DailyFortuneResponse(
            success=True,
            data=daily_fortune
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指定日期运势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/date/{date}")
async def delete_fortune_by_date(
    user_id: str,
    date: str,
    daily_fortune_service: DailyFortuneService = Depends(get_daily_fortune_service)
):
    """
    删除指定日期的运势
    
    - **user_id**: 用户ID
    - **date**: 日期，格式：YYYY-MM-DD
    
    注意：此操作将永久删除该日期的运势记录
    """
    try:
        logger.info(f"删除用户 {user_id} 的 {date} 运势")
        
        # 先获取运势记录
        daily_fortune = await daily_fortune_service.get_fortune_by_date(user_id, date)
        
        if not daily_fortune:
            raise HTTPException(status_code=404, detail="该日期的运势不存在")
        
        # 删除运势记录
        success = await daily_fortune_service.delete_fortune(
            daily_fortune._id, 
            user_id
        )
        
        if success:
            return {"success": True, "message": "运势记录删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除指定日期运势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
