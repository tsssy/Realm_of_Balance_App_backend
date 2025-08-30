#!/usr/bin/env python3
"""
Kimi版本的Daily Fortune API路由
使用Kimi AI替代Gemini进行运势生成
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import time
from datetime import datetime

from app.models.daily_fortune import (
    DailyFortuneRequest, DailyFortuneResponse, 
    DailyFortuneHistoryResponse
)
from app.services.kimi_daily_fortune_service import get_kimi_daily_fortune_service, KimiDailyFortuneService
from app.services.user_service import UserService
from app.utils.logger import MyLogger

router = APIRouter(prefix="/kimi-daily-fortune", tags=["Kimi Daily Fortune"])
logger = MyLogger("kimi_daily_fortune_api")

async def get_user_service():
    """获取用户服务实例"""
    return UserService()

@router.post("/generate", response_model=DailyFortuneResponse)
async def generate_kimi_daily_fortune(
    request: DailyFortuneRequest,
    kimi_daily_fortune_service: KimiDailyFortuneService = Depends(get_kimi_daily_fortune_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    生成今日运势 (Kimi版本)
    """
    start_time = time.time()
    request_datetime = datetime.now()
    target_date = request.date or datetime.now().strftime("%Y-%m-%d")
    
    logger.info(f"=== Kimi 运势生成请求开始 ===")
    logger.info(f"请求时间: {request_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"用户ID: {request.user_id}")
    logger.info(f"目标日期: {target_date}")
    
    try:
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 生成运势
        daily_fortune = await kimi_daily_fortune_service.generate_daily_fortune(
            request.user_id,
            request.user_profile,
            target_date
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"=== Kimi 运势生成完成 ===")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info(f"运势记录已创建")
        
        return DailyFortuneResponse(
            success=True,
            data=daily_fortune,
            message="Kimi运势生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kimi运势生成异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Kimi运势生成异常: {e}")

@router.get("/{user_id}/today", response_model=DailyFortuneResponse)
async def get_kimi_today_fortune(
    user_id: str,
    kimi_daily_fortune_service: KimiDailyFortuneService = Depends(get_kimi_daily_fortune_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取今日运势 (Kimi版本)
    """
    start_time = time.time()
    request_datetime = datetime.now()
    
    logger.info(f"=== Kimi 今日运势请求开始 ===")
    logger.info(f"请求时间: {request_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"用户ID: {user_id}")
    
    try:
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
        daily_fortune = await kimi_daily_fortune_service.get_today_fortune(
            user_id, 
            user_profile
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"=== Kimi 今日运势完成 ===")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info(f"运势记录已创建")
        
        return DailyFortuneResponse(
            success=True,
            data=daily_fortune,
            message="Kimi今日运势获取成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kimi今日运势异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Kimi今日运势异常: {e}")

@router.get("/{user_id}/history", response_model=DailyFortuneHistoryResponse)
async def get_kimi_fortune_history(
    user_id: str,
    start_date: Optional[str] = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    kimi_daily_fortune_service: KimiDailyFortuneService = Depends(get_kimi_daily_fortune_service)
):
    """
    获取Kimi运势历史
    """
    try:
        logger.info(f"获取用户 {user_id} 的Kimi运势历史，范围: {start_date} 到 {end_date}")
        
        fortune_records = await kimi_daily_fortune_service.get_fortune_history(
            user_id, start_date, end_date
        )
        
        return DailyFortuneHistoryResponse(
            success=True,
            data=fortune_records,
            total=len(fortune_records),
            message="获取成功"
        )
        
    except Exception as e:
        logger.error(f"获取Kimi运势历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/date/{date}", response_model=DailyFortuneResponse)
async def get_kimi_fortune_by_date(
    user_id: str,
    date: str,
    kimi_daily_fortune_service: KimiDailyFortuneService = Depends(get_kimi_daily_fortune_service)
):
    """
    获取指定日期的运势 (Kimi版本)
    """
    try:
        logger.info(f"获取用户 {user_id} 的 {date} Kimi运势")
        
        daily_fortune = await kimi_daily_fortune_service.get_fortune_by_date(user_id, date)
        
        if not daily_fortune:
            raise HTTPException(status_code=404, detail="该日期的运势不存在")
        
        return DailyFortuneResponse(
            success=True,
            data=daily_fortune,
            message="获取成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Kimi指定日期运势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/date/{date}")
async def delete_kimi_fortune_by_date(
    user_id: str,
    date: str,
    kimi_daily_fortune_service: KimiDailyFortuneService = Depends(get_kimi_daily_fortune_service)
):
    """
    删除指定日期的运势 (Kimi版本)
    """
    try:
        logger.info(f"删除用户 {user_id} 的 {date} Kimi运势")
        
        # 先获取运势记录
        daily_fortune = await kimi_daily_fortune_service.get_fortune_by_date(user_id, date)
        
        if not daily_fortune:
            raise HTTPException(status_code=404, detail="该日期的运势不存在")
        
        # 删除运势记录
        success = await kimi_daily_fortune_service.delete_fortune(
            str(daily_fortune._id), 
            user_id
        )
        
        if success:
            return {"success": True, "message": "Kimi运势记录删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除Kimi指定日期运势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_kimi_daily_fortune_status():
    """获取Kimi Daily Fortune服务状态"""
    return {
        "success": True,
        "service": "Kimi moonshot-v1-8k",
        "status": "active",
        "description": "Kimi版本的每日运势生成服务",
        "endpoints": {
            "generate": "/api/v2/kimi-daily-fortune/generate",
            "today": "/api/v2/kimi-daily-fortune/{user_id}/today",
            "history": "/api/v2/kimi-daily-fortune/{user_id}/history",
            "by_date": "/api/v2/kimi-daily-fortune/{user_id}/date/{date}"
        }
    }
