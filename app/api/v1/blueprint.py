from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.models.blueprint import BlueprintGenerateRequest, BlueprintResponse
from app.services.blueprint_service import BlueprintService
from app.services.user_service import UserService
from app.utils.logger import MyLogger

logger = MyLogger("blueprint_api")

router = APIRouter(prefix="/blueprint", tags=["算命分析"])

# 依赖注入
async def get_blueprint_service():
    return BlueprintService()

async def get_user_service():
    return UserService()

@router.post("/generate", response_model=BlueprintResponse)
async def generate_blueprint(
    request: BlueprintGenerateRequest,
    blueprint_service: BlueprintService = Depends(get_blueprint_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    生成个人蓝图（算命结果）
    
    - **user_id**: 用户ID
    - **user_profile**: 用户信息，用于AI分析
    
    返回完整的算命结果，包括：
    - 八字排盘
    - 五行分析
    - 内在蓝图报告
    - 生命曲线预测
    """
    try:
        logger.info(f"生成用户 {request.user_id} 的算命结果")
        
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 生成算命结果
        blueprint_result = await blueprint_service.generate_blueprint(
            request.user_id, 
            request.user_profile
        )
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=BlueprintResponse)
async def get_blueprint(
    user_id: str,
    blueprint_service: BlueprintService = Depends(get_blueprint_service)
):
    """
    获取用户的算命结果
    
    - **user_id**: 用户ID
    
    返回用户的完整算命结果
    """
    try:
        logger.info(f"获取用户 {user_id} 的算命结果")
        
        blueprint_result = await blueprint_service.get_blueprint(user_id)
        
        if not blueprint_result:
            raise HTTPException(status_code=404, detail="算命结果不存在")
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/regenerate", response_model=BlueprintResponse)
async def regenerate_blueprint(
    user_id: str,
    user_profile: dict,
    blueprint_service: BlueprintService = Depends(get_blueprint_service)
):
    """
    重新生成算命结果
    
    - **user_id**: 用户ID
    - **user_profile**: 用户信息
    
    注意：此操作将删除旧的算命结果并重新生成
    """
    try:
        logger.info(f"重新生成用户 {user_id} 的算命结果")
        
        blueprint_result = await blueprint_service.regenerate_blueprint(
            user_id, 
            user_profile
        )
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="算命结果已重新生成"
        )
        
    except Exception as e:
        logger.error(f"重新生成算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_blueprint(
    user_id: str,
    blueprint_service: BlueprintService = Depends(get_blueprint_service)
):
    """
    删除用户的算命结果
    
    - **user_id**: 用户ID
    
    注意：此操作将永久删除算命结果，无法恢复
    """
    try:
        logger.info(f"删除用户 {user_id} 的算命结果")
        
        success = await blueprint_service.delete_blueprint(user_id)
        
        if success:
            return {"success": True, "message": "算命结果删除成功"}
        else:
            raise HTTPException(status_code=404, detail="算命结果不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除算命结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick", response_model=BlueprintResponse)
async def generate_blueprint_quick(
    request: BlueprintGenerateRequest,
    blueprint_service: BlueprintService = Depends(get_blueprint_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    快速生成五行计算结果
    
    - **user_id**: 用户ID
    - **user_profile**: 用户信息
    
    返回五行计算结果，状态为 partial
    """
    try:
        logger.info(f"快速生成用户 {request.user_id} 的五行结果")
        
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 快速生成五行结果
        blueprint_result = await blueprint_service.generate_blueprint_quick(
            request.user_id, 
            request.user_profile
        )
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="五行结果快速生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"快速生成五行结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete", response_model=BlueprintResponse)
async def generate_blueprint_complete(
    request: BlueprintGenerateRequest,
    blueprint_service: BlueprintService = Depends(get_blueprint_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    基于五行结果生成完整蓝图
    
    - **user_id**: 用户ID
    - **user_profile**: 用户信息
    
    注意：需要先调用快速生成接口
    """
    try:
        logger.info(f"生成用户 {request.user_id} 的完整蓝图")
        
        # 验证用户是否存在
        user = await user_service.get_user_profile(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 生成完整蓝图
        blueprint_result = await blueprint_service.generate_blueprint_complete(
            request.user_id, 
            request.user_profile
        )
        
        return BlueprintResponse(
            success=True,
            data=blueprint_result,
            message="完整蓝图生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成完整蓝图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/status")
async def get_blueprint_status(
    user_id: str,
    blueprint_service: BlueprintService = Depends(get_blueprint_service)
):
    """
    获取用户的蓝图生成状态
    
    - **user_id**: 用户ID
    
    返回生成状态和进度信息
    """
    try:
        logger.info(f"获取用户 {user_id} 的蓝图生成状态")
        
        status_info = await blueprint_service.get_blueprint_status(user_id)
        
        return {
            "success": True,
            "data": status_info
        }
        
    except Exception as e:
        logger.error(f"获取蓝图状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
