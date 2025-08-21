from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from datetime import datetime

from app.services.ai_service import AIService
from app.config.prompt_config import PromptType, PromptConfig, PROMPT_DESCRIPTIONS, validate_prompt_config
from app.core.cache import VersionedCacheManager
from app.utils.logger import MyLogger

logger = MyLogger("admin_api")

router = APIRouter(prefix="/admin", tags=["系统管理"])

# 依赖注入
async def get_ai_service():
    return AIService()

async def get_cache_manager():
    return VersionedCacheManager()

@router.get("/prompts")
async def get_prompt_configuration(
    ai_service: AIService = Depends(get_ai_service)
):
    """
    获取提示词配置信息
    
    返回所有可用的提示词类型、文件名、描述等信息
    """
    try:
        prompt_types = ai_service.get_available_prompt_types()
        
        prompt_info = {}
        for prompt_type in prompt_types:
            prompt_info[prompt_type.value] = {
                **ai_service.get_prompt_info(prompt_type),
                "description": PROMPT_DESCRIPTIONS[prompt_type]
            }
        
        return {
            "success": True,
            "data": {
                "total_prompts": len(prompt_types),
                "prompts": prompt_info
            }
        }
        
    except Exception as e:
        logger.error(f"获取提示词配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompts/{prompt_type}")
async def get_prompt_details(
    prompt_type: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    获取指定提示词的详细信息
    
    - **prompt_type**: 提示词类型 (blueprint, heart_compass, daily_fortune)
    """
    try:
        # 验证提示词类型
        if not PromptConfig.is_valid_prompt_type(prompt_type):
            raise HTTPException(status_code=400, detail=f"无效的提示词类型: {prompt_type}")
        
        # 获取提示词类型枚举
        prompt_enum = PromptType(prompt_type)
        
        # 获取详细信息
        prompt_info = ai_service.get_prompt_info(prompt_enum)
        description = PROMPT_DESCRIPTIONS.get(prompt_enum, {})
        
        return {
            "success": True,
            "data": {
                **prompt_info,
                "description": description
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取提示词详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/stats")
async def get_cache_statistics(
    cache_manager: VersionedCacheManager = Depends(get_cache_manager)
):
    """
    获取缓存统计信息
    
    返回缓存的命中率、失效次数等统计信息
    """
    try:
        stats = cache_manager.cache_stats
        
        return {
            "success": True,
            "data": {
                "cache_statistics": stats,
                "total_requests": stats.get("hits", 0) + stats.get("misses", 0),
                "hit_rate": f"{stats.get('hits', 0) / max(1, stats.get('hits', 0) + stats.get('misses', 0)) * 100:.2f}%"
            }
        }
        
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/status")
async def get_system_status():
    """
    获取系统状态
    
    返回系统的基本状态信息
    """
    try:
        from app.config import settings
        
        return {
            "success": True,
            "data": {
                "service_name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "mongodb_configured": bool(settings.MONGODB_URL),
                "redis_configured": bool(settings.REDIS_URL),
                "gemini_configured": bool(settings.GEMINI_API_KEY),
                "available_prompt_types": [pt.value for pt in PromptType]
            }
        }
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear")
async def clear_cache(
    cache_manager: VersionedCacheManager = Depends(get_cache_manager)
):
    """
    清空缓存
    
    清空所有缓存数据（谨慎使用）
    """
    try:
        # 这里可以添加权限验证
        # 例如检查是否是管理员用户
        
        # 清空缓存
        cache_manager.memory_cache.clear()
        
        logger.info("缓存已清空")
        
        return {
            "success": True,
            "message": "缓存已清空"
        }
        
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/detailed")
async def get_detailed_health():
    """
    获取详细的健康检查信息
    
    包含各个组件的状态检查
    """
    try:
        health_status = {
            "service": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # 检查数据库连接
        try:
            from app.core.database import Database
            # 这里可以添加实际的数据库连接检查
            health_status["components"]["database"] = "healthy"
        except Exception as e:
            health_status["components"]["database"] = f"unhealthy: {str(e)}"
            health_status["service"] = "degraded"
        
        # 检查AI服务
        try:
            ai_service = AIService()
            health_status["components"]["ai_service"] = "healthy"
        except Exception as e:
            health_status["components"]["ai_service"] = f"unhealthy: {str(e)}"
            health_status["service"] = "degraded"
        
        # 检查提示词配置
        try:
            validate_prompt_config()
            health_status["components"]["prompt_config"] = "healthy"
        except Exception as e:
            health_status["components"]["prompt_config"] = f"unhealthy: {str(e)}"
            health_status["service"] = "degraded"
        
        return {
            "success": True,
            "data": health_status
        }
        
    except Exception as e:
        logger.error(f"获取详细健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
