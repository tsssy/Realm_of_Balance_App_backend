#!/usr/bin/env python3
"""
Kimi版本的Heart Compass API路由
使用Kimi AI替代Gemini进行指导生成
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import time
from datetime import datetime

from app.models.heart_compass import (
    HeartCompassRequest, HeartCompassResponse, 
    HeartCompassHistoryResponse, AskAgainRequest
)
from app.services.kimi_heart_compass_service import get_kimi_heart_compass_service, KimiHeartCompassService
from app.services.user_service import UserService
from app.utils.logger import MyLogger

router = APIRouter(prefix="/kimi-heart-compass", tags=["Kimi Heart Compass"])
logger = MyLogger("kimi_heart_compass_api")

async def get_user_service():
    """获取用户服务实例"""
    return UserService()

@router.post("/seek-guidance", response_model=HeartCompassResponse)
async def seek_kimi_guidance(
    request: HeartCompassRequest,
    kimi_heart_compass_service: KimiHeartCompassService = Depends(get_kimi_heart_compass_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取 Kimi Heart Compass 指导
    """
    start_time = time.time()
    request_datetime = datetime.now()
    logger.info(f"=== Kimi Heart Compass指导请求开始 ===")
    logger.info(f"请求时间: {request_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"用户ID: {request.user_id}")
    logger.info(f"问题: {request.question[:100]}...")
    
    try:
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取指导
        guidance_record = await kimi_heart_compass_service.seek_guidance(
            request.user_id,
            request.question,
            request.user_profile
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"=== Kimi Heart Compass指导完成 ===")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info(f"指导记录已创建")
        
        return HeartCompassResponse(
            success=True,
            data=guidance_record,
            message="Kimi指导生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kimi Heart Compass指导异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Kimi指导异常: {e}")

@router.post("/ask-again", response_model=HeartCompassResponse)
async def ask_kimi_again(
    request: AskAgainRequest,
    kimi_heart_compass_service: KimiHeartCompassService = Depends(get_kimi_heart_compass_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    重新提问，基于之前的指导进行深入探讨 (Kimi版本)
    """
    start_time = time.time()
    request_datetime = datetime.now()
    logger.info(f"=== Kimi Heart Compass重新提问开始 ===")
    logger.info(f"请求时间: {request_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"用户ID: {request.user_id}")
    logger.info(f"新问题: {request.question[:100]}...")
    
    try:
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取用户信息用于AI分析
        user_profile = {
            "gender": user.gender,
            "birth_date": user.birth_date,
            "birth_time": user.birth_time,
            "birth_location": user.birth_location
        }
        
        # 重新获取指导
        guidance_record = await kimi_heart_compass_service.ask_again(
            request.user_id,
            request.question,
            user_profile,
            request.previous_guidance_id
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"=== Kimi Heart Compass重新提问完成 ===")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info(f"指导记录已创建")
        
        return HeartCompassResponse(
            success=True,
            data=guidance_record,
            message="Kimi重新指导生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kimi Heart Compass重新提问异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Kimi重新提问异常: {e}")

@router.get("/{user_id}/history", response_model=HeartCompassHistoryResponse)
async def get_kimi_guidance_history(
    user_id: str,
    page: int = Query(1, ge=1, description="页码，从1开始"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数，最大100"),
    kimi_heart_compass_service: KimiHeartCompassService = Depends(get_kimi_heart_compass_service)
):
    """
    获取Kimi指导历史
    """
    try:
        logger.info(f"获取用户 {user_id} 的Kimi指导历史，页码: {page}, 每页: {limit}")
        
        history_response = await kimi_heart_compass_service.get_guidance_history(
            user_id, page, limit
        )
        
        return HeartCompassHistoryResponse(
            success=True,
            data=history_response["records"],
            total=history_response["total"],
            page=history_response["page"],
            limit=history_response["limit"],
            has_more=history_response["has_more"],
            message=None
        )
        
    except Exception as e:
        logger.error(f"获取Kimi指导历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guidance/{guidance_id}", response_model=HeartCompassResponse)
async def get_kimi_guidance_by_id(
    guidance_id: str,
    kimi_heart_compass_service: KimiHeartCompassService = Depends(get_kimi_heart_compass_service)
):
    """
    根据ID获取Kimi指导记录
    """
    try:
        logger.info(f"获取Kimi指导记录: {guidance_id}")
        
        guidance_record = await kimi_heart_compass_service.get_guidance_by_id(guidance_id)
        
        if not guidance_record:
            raise HTTPException(status_code=404, detail="指导记录不存在")
        
        return HeartCompassResponse(
            success=True,
            data=guidance_record,
            message="获取成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Kimi指导记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/guidance/{guidance_id}")
async def delete_kimi_guidance(
    guidance_id: str,
    user_id: str = Query(..., description="用户ID，用于验证权限"),
    kimi_heart_compass_service: KimiHeartCompassService = Depends(get_kimi_heart_compass_service)
):
    """
    删除Kimi指导记录
    """
    try:
        logger.info(f"删除Kimi指导记录: {guidance_id}, 用户: {user_id}")
        
        success = await kimi_heart_compass_service.delete_guidance(guidance_id, user_id)
        
        if success:
            return {"success": True, "message": "Kimi指导记录删除成功"}
        else:
            raise HTTPException(status_code=404, detail="指导记录不存在或无权删除")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除Kimi指导记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_kimi_heart_compass_status():
    """获取Kimi Heart Compass服务状态"""
    return {
        "success": True,
        "service": "Kimi moonshot-v1-8k",
        "status": "active",
        "description": "Kimi版本的Heart Compass指导服务",
        "endpoints": {
            "seek_guidance": "/api/v2/kimi-heart-compass/seek-guidance",
            "ask_again": "/api/v2/kimi-heart-compass/ask-again",
            "history": "/api/v2/kimi-heart-compass/{user_id}/history",
            "get_by_id": "/api/v2/kimi-heart-compass/guidance/{guidance_id}"
        }
    }
