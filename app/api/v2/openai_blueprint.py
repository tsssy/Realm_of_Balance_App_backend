#!/usr/bin/env python3
"""
OpenAI版本的蓝图API路由
使用GPT-4o-mini模型替代Gemini进行五行计算
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import time
from datetime import datetime

from app.models.blueprint import BlueprintGenerateRequest, BlueprintResponse
from app.services.openai_blueprint_service import get_openai_blueprint_service, OpenAIBlueprintService
from app.services.user_service import UserService
from app.utils.logger import MyLogger

# 创建路由器
router = APIRouter(prefix="/openai-blueprint", tags=["OpenAI Blueprint"])
logger = MyLogger("openai_blueprint_api")

# 依赖注入
async def get_user_service():
    """获取用户服务实例"""
    return UserService()

@router.post("/quick", response_model=BlueprintResponse)
async def generate_openai_blueprint_quick(
    request: BlueprintGenerateRequest,
    openai_blueprint_service: OpenAIBlueprintService = Depends(get_openai_blueprint_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    使用OpenAI GPT-4o-mini快速生成五行蓝图
    
    与原有的 /api/v1/blueprint/quick 接口保持相同的输入输出格式
    仅AI服务提供商不同
    """
    start_time = time.time()
    request_datetime = datetime.now()
    
    logger.info("=== OpenAI 快速蓝图生成请求开始 ===")
    logger.info(f"请求时间: {request_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"用户ID: {request.user_id}")
    logger.info(f"请求数据: {request.dict()}")
    
    try:
        # 验证用户是否存在（与原有接口完全一致）
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 快速生成五行结果（与原有接口完全一致）
        blueprint_result = await openai_blueprint_service.generate_blueprint_quick(
            request.user_id, 
            request.user_profile
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"=== OpenAI 快速蓝图生成完成 ===")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info(f"生成结果: {blueprint_result.get('success', False)}")
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="OpenAI快速蓝图生成成功"
        )
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.error(f"OpenAI蓝图生成异常: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=f"OpenAI蓝图生成异常: {str(e)}"
        )

@router.get("/status")
async def get_openai_status():
    """
    获取OpenAI服务状态
    """
    return {
        'success': True,
        'service': 'OpenAI GPT-4o-mini',
        'status': 'active',
        'description': 'OpenAI版本的五行蓝图生成服务',
        'endpoint': '/api/v2/openai-blueprint/quick'
    }
