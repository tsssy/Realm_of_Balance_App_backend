from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from app.models.heart_compass import (
    HeartCompassRequest, HeartCompassResponse, 
    HeartCompassHistoryResponse, AskAgainRequest
)
from app.services.heart_compass_service import HeartCompassService
from app.services.user_service import UserService
from app.utils.logger import MyLogger

logger = MyLogger("heart_compass_api")

router = APIRouter(prefix="/heart-compass", tags=["Heart Compass 指导"])

# 依赖注入
async def get_heart_compass_service():
    return HeartCompassService()

async def get_user_service():
    return UserService()

@router.post("/seek-guidance", response_model=HeartCompassResponse)
async def seek_guidance(
    request: HeartCompassRequest,
    heart_compass_service: HeartCompassService = Depends(get_heart_compass_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取 Heart Compass 指导
    
    - **user_id**: 用户ID
    - **question**: 用户的具体困惑文本
    - **user_profile**: 用户信息，用于个性化分析
    
    返回结构化的指导内容，包括：
    - 卦象信息
    - 对话流（四个环节）
    - 深层智慧
    - 行动指南
    - 决策协议
    """
    try:
        logger.info(f"用户 {request.user_id} 寻求指导: {request.question[:50]}...")
        
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取指导
        guidance_record = await heart_compass_service.seek_guidance(
            request.user_id,
            request.question,
            request.user_profile
        )
        
        return HeartCompassResponse(
            success=True,
            data=guidance_record
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指导失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask-again", response_model=HeartCompassResponse)
async def ask_again(
    request: AskAgainRequest,
    heart_compass_service: HeartCompassService = Depends(get_heart_compass_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    重新提问，基于之前的指导进行深入探讨
    
    - **user_id**: 用户ID
    - **question**: 新的问题或深入探讨
    - **previous_guidance_id**: 之前的指导ID（可选，用于上下文关联）
    
    返回新的指导内容，可能基于之前的分析进行深入
    """
    try:
        logger.info(f"用户 {request.user_id} 重新提问: {request.question[:50]}...")
        
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
        guidance_record = await heart_compass_service.ask_again(
            request.user_id,
            request.question,
            user_profile,
            request.previous_guidance_id
        )
        
        return HeartCompassResponse(
            success=True,
            data=guidance_record
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新提问失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/history", response_model=HeartCompassHistoryResponse)
async def get_guidance_history(
    user_id: str,
    page: int = Query(1, ge=1, description="页码，从1开始"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数，最大100"),
    heart_compass_service: HeartCompassService = Depends(get_heart_compass_service)
):
    """
    获取指导历史
    
    - **user_id**: 用户ID
    - **page**: 页码（可选，默认为1）
    - **limit**: 每页记录数（可选，默认为10，最大100）
    
    返回分页的指导历史记录
    """
    try:
        logger.info(f"获取用户 {user_id} 的指导历史，页码: {page}, 每页: {limit}")
        
        history_response = await heart_compass_service.get_guidance_history(
            user_id, page, limit
        )
        
        return history_response
        
    except Exception as e:
        logger.error(f"获取指导历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guidance/{guidance_id}", response_model=HeartCompassResponse)
async def get_guidance_by_id(
    guidance_id: str,
    heart_compass_service: HeartCompassService = Depends(get_heart_compass_service)
):
    """
    根据ID获取指导记录
    
    - **guidance_id**: 指导记录ID
    
    返回指定的指导记录详情
    """
    try:
        logger.info(f"获取指导记录: {guidance_id}")
        
        guidance_record = await heart_compass_service.get_guidance_by_id(guidance_id)
        
        if not guidance_record:
            raise HTTPException(status_code=404, detail="指导记录不存在")
        
        return HeartCompassResponse(
            success=True,
            data=guidance_record
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指导记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/guidance/{guidance_id}")
async def delete_guidance(
    guidance_id: str,
    user_id: str = Query(..., description="用户ID，用于验证权限"),
    heart_compass_service: HeartCompassService = Depends(get_heart_compass_service)
):
    """
    删除指导记录
    
    - **guidance_id**: 指导记录ID
    - **user_id**: 用户ID（用于验证权限）
    
    注意：只能删除自己的指导记录
    """
    try:
        logger.info(f"删除指导记录: {guidance_id}, 用户: {user_id}")
        
        success = await heart_compass_service.delete_guidance(guidance_id, user_id)
        
        if success:
            return {"success": True, "message": "指导记录删除成功"}
        else:
            raise HTTPException(status_code=404, detail="指导记录不存在或无权删除")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除指导记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
