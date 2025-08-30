#!/usr/bin/env python3
"""
Kimi版本的蓝图API路由
使用Kimi模型替代Gemini进行五行计算
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import time
from datetime import datetime

from app.models.blueprint import BlueprintGenerateRequest, BlueprintResponse
from app.services.kimi_blueprint_service import get_kimi_blueprint_service, KimiBlueprintService
from app.services.user_service import UserService
from app.utils.logger import MyLogger

# 创建路由器
router = APIRouter(prefix="/kimi-blueprint", tags=["Kimi Blueprint"])
logger = MyLogger("kimi_blueprint_api")

# 依赖注入
async def get_user_service():
    """获取用户服务实例"""
    return UserService()

@router.post("/quick", response_model=BlueprintResponse)
async def generate_kimi_blueprint_quick(
    request: BlueprintGenerateRequest,
    kimi_blueprint_service: KimiBlueprintService = Depends(get_kimi_blueprint_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    使用Kimi快速生成五行蓝图
    
    与原有的 /api/v1/blueprint/quick 接口保持相同的输入输出格式
    仅AI服务提供商不同
    """
    start_time = time.time()
    request_datetime = datetime.now()
    
    logger.info("=== Kimi 快速蓝图生成请求开始 ===")
    logger.info(f"请求时间: {request_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"用户ID: {request.user_id}")
    logger.info(f"请求数据: {request.dict()}")
    
    try:
        # 验证用户是否存在（与原有接口完全一致）
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 快速生成五行结果（与原有接口完全一致）
        blueprint_result = await kimi_blueprint_service.generate_blueprint_quick(
            request.user_id, 
            request.user_profile
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"=== Kimi 快速蓝图生成完成 ===")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info(f"生成结果: 成功")
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="Kimi快速蓝图生成成功"
        )
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.error(f"Kimi蓝图生成异常: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Kimi蓝图生成异常: {str(e)}"
        )

@router.post("/complete", response_model=BlueprintResponse)
async def generate_kimi_blueprint_complete(
    request: BlueprintGenerateRequest,
    kimi_blueprint_service: KimiBlueprintService = Depends(get_kimi_blueprint_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    基于五行结果生成完整蓝图 (Kimi版本)
    """
    start_time = time.time()
    request_datetime = datetime.now()
    logger.info(f"=== Kimi 完整蓝图生成请求开始 ===")
    logger.info(f"请求时间: {request_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"用户ID: {request.user_id}")
    
    try:
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        blueprint_result = await kimi_blueprint_service.generate_blueprint_complete(
            request.user_id, 
            request.user_profile
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"=== Kimi 完整蓝图生成完成 ===")
        logger.info(f"总耗时: {total_time:.2f}秒")
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="Kimi完整蓝图生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kimi完整蓝图生成异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Kimi完整蓝图生成异常: {e}")

@router.post("/generate", response_model=BlueprintResponse)
async def generate_kimi_blueprint(
    request: BlueprintGenerateRequest,
    kimi_blueprint_service: KimiBlueprintService = Depends(get_kimi_blueprint_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    生成个人蓝图（算命结果）- Kimi版本
    
    与原有的 /api/v1/blueprint/generate 接口保持相同的输入输出格式
    仅AI服务提供商不同
    """
    try:
        logger.info(f"Kimi生成用户 {request.user_id} 的算命结果")
        
        # 验证用户是否存在（与原有接口完全一致）
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 由于Kimi服务目前只支持分层生成，这里先进行快速生成，然后完整生成
        quick_result = await kimi_blueprint_service.generate_blueprint_quick(
            request.user_id, 
            request.user_profile
        )
        
        # 基于快速结果生成完整蓝图
        blueprint_result = await kimi_blueprint_service.generate_blueprint_complete(
            request.user_id, 
            request.user_profile
        )
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="Kimi算命结果生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Kimi生成算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=BlueprintResponse)
async def get_kimi_blueprint(
    user_id: str,
    kimi_blueprint_service: KimiBlueprintService = Depends(get_kimi_blueprint_service)
):
    """
    获取用户的算命结果 - Kimi版本
    
    - **user_id**: 用户ID
    
    返回用户的完整算命结果
    """
    try:
        logger.info(f"获取用户 {user_id} 的Kimi算命结果")
        
        # 通过数据库直接查询（因为Kimi服务没有get_blueprint方法）
        from app.core.database import Database
        blueprint_data = await Database.find_one("blueprint_results", {"user_id": user_id})
        
        if not blueprint_data:
            raise HTTPException(status_code=404, detail="算命结果不存在")
        
        from app.models.blueprint import BlueprintResult
        blueprint_result = BlueprintResult(**blueprint_data)
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Kimi算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/regenerate", response_model=BlueprintResponse)
async def regenerate_kimi_blueprint(
    user_id: str,
    user_profile: dict,
    kimi_blueprint_service: KimiBlueprintService = Depends(get_kimi_blueprint_service)
):
    """
    重新生成算命结果 - Kimi版本
    
    - **user_id**: 用户ID
    - **user_profile**: 用户信息
    
    注意：此操作将删除旧的算命结果并重新生成
    """
    try:
        logger.info(f"Kimi重新生成用户 {user_id} 的算命结果")
        
        # 删除旧的算命结果
        from app.core.database import Database
        await Database.delete_one("blueprint_results", {"user_id": user_id})
        
        # 重新生成（快速+完整）
        quick_result = await kimi_blueprint_service.generate_blueprint_quick(
            user_id, 
            user_profile
        )
        
        blueprint_result = await kimi_blueprint_service.generate_blueprint_complete(
            user_id, 
            user_profile
        )
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="Kimi算命结果已重新生成"
        )
        
    except Exception as e:
        logger.error(f"Kimi重新生成算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_kimi_blueprint(
    user_id: str,
    kimi_blueprint_service: KimiBlueprintService = Depends(get_kimi_blueprint_service)
):
    """
    删除用户的算命结果 - Kimi版本
    
    - **user_id**: 用户ID
    
    注意：此操作将永久删除算命结果，无法恢复
    """
    try:
        logger.info(f"删除用户 {user_id} 的Kimi算命结果")
        
        from app.core.database import Database
        result = await Database.delete_one("blueprint_results", {"user_id": user_id})
        
        if result > 0:
            return {"success": True, "message": "Kimi算命结果删除成功"}
        else:
            raise HTTPException(status_code=404, detail="算命结果不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除Kimi算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/status")
async def get_kimi_blueprint_status(
    user_id: str
):
    """
    获取用户的蓝图生成状态 - Kimi版本
    
    - **user_id**: 用户ID
    
    返回生成状态和进度信息
    """
    try:
        logger.info(f"获取用户 {user_id} 的Kimi蓝图生成状态")
        
        from app.core.database import Database
        blueprint_data = await Database.find_one("blueprint_results", {"user_id": user_id})
        
        if not blueprint_data:
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "status": "not_found",
                    "message": "没有找到蓝图数据"
                }
            }
        
        from app.models.blueprint import BlueprintResult
        blueprint_result = BlueprintResult(**blueprint_data)
        
        # 构建状态信息
        status_info = {
            "user_id": user_id,
            "generation_status": blueprint_result.generation_status,
            "task_id": blueprint_result.task_id,
            "has_quick_data": blueprint_result.quick_data is not None,
            "has_complete_data": blueprint_result.inner_blueprint is not None,
            "created_at": blueprint_result.created_at,
            "updated_at": blueprint_result.updated_at
        }
        
        return {
            "success": True,
            "data": status_info
        }
        
    except Exception as e:
        logger.error(f"获取Kimi蓝图状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_kimi_service_status():
    """
    获取Kimi服务状态
    """
    return {
        'success': True,
        'service': 'Kimi moonshot-v1-8k',
        'status': 'active',
        'description': 'Kimi版本的五行蓝图生成服务',
        'endpoints': {
            'generate': '/api/v2/kimi-blueprint/generate',
            'get': '/api/v2/kimi-blueprint/{user_id}',
            'regenerate': '/api/v2/kimi-blueprint/{user_id}/regenerate',
            'delete': '/api/v2/kimi-blueprint/{user_id}',
            'quick': '/api/v2/kimi-blueprint/quick',
            'complete': '/api/v2/kimi-blueprint/complete',
            'status': '/api/v2/kimi-blueprint/{user_id}/status'
        }
    }
