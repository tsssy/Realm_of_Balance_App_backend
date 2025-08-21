import redis
import json
import hashlib
from typing import Any, Optional, Dict
from functools import wraps
from datetime import datetime, timedelta
import asyncio

from app.config import settings
from app.utils.logger import MyLogger

logger = MyLogger("cache")

class VersionedCacheManager:
    """版本化缓存管理器 - 零脏数据风险"""
    
    def __init__(self):
        # Redis 客户端（主缓存）
        self.redis_client = None
        try:
            if settings.REDIS_URL:
                self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
                self.redis_client.ping()
                logger.info("Redis 连接成功")
            else:
                logger.warning("Redis 未配置，将使用内存缓存")
        except Exception as e:
            logger.warning(f"Redis 连接失败，将使用内存缓存: {e}")
            self.redis_client = None
        
        # 内存缓存（热点数据 + 备用）
        self.memory_cache = {}
        
        # 实体版本管理（Redis 或内存）
        self.version_store = {}
        
        # 依赖关系映射
        self.dependency_map = {
            "user:profile": ["ai:blueprint", "ai:daily_fortune", "ai:heart_compass"],
            "ai:blueprint": ["ai:daily_fortune"],
            "ai:daily_fortune": [],
            "ai:heart_compass": []
        }
        
        # 缓存统计
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "version_mismatches": 0
        }
    
    async def get_entity_version(self, entity_id: str, entity_type: str = "user") -> int:
        """获取实体当前版本号"""
        try:
            if self.redis_client:
                version_key = f"{entity_type}:{entity_id}:version"
                version = await self.redis_client.get(version_key)
                return int(version) if version else 1
            else:
                key = f"{entity_type}:{entity_id}"
                return self.version_store.get(key, 1)
        except Exception as e:
            logger.error(f"获取实体版本失败: {e}")
            return 1
    
    async def increment_entity_version(self, entity_id: str, entity_type: str = "user") -> int:
        """递增实体版本号"""
        try:
            current_version = await self.get_entity_version(entity_id, entity_type)
            new_version = current_version + 1
            
            if self.redis_client:
                version_key = f"{entity_type}:{entity_id}:version"
                await self.redis_client.set(version_key, new_version)
            else:
                key = f"{entity_type}:{entity_id}"
                self.version_store[key] = new_version
            
            logger.info(f"实体 {entity_type}:{entity_id} 版本已更新: {current_version} -> {new_version}")
            return new_version
            
        except Exception as e:
            logger.error(f"更新实体版本失败: {e}")
            return current_version + 1
    
    async def set_with_version(self, key: str, value: Any, entity_id: str, entity_type: str = "user", expire: int = 3600):
        """设置带版本号的缓存（核心方法）"""
        try:
            # 1. 获取当前版本号
            version = await self.get_entity_version(entity_id, entity_type)
            
            # 2. 构建版本化缓存键
            versioned_key = f"{key}:v{version}"
            
            # 3. 构建缓存数据
            cache_data = {
                "value": value,
                "version": version,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "created_at": datetime.now().isoformat(),
                "expire_at": (datetime.now() + timedelta(seconds=expire)).isoformat()
            }
            
            # 4. 存储到 Redis
            if self.redis_client:
                await self.redis_client.setex(
                    versioned_key, 
                    expire, 
                    json.dumps(cache_data, ensure_ascii=False)
                )
            
            # 5. 存储到内存（热点数据）
            if self._is_hot_data(key):
                self.memory_cache[versioned_key] = cache_data
            
            logger.debug(f"已缓存 {versioned_key}，版本: {version}")
            
        except Exception as e:
            logger.error(f"设置版本化缓存失败: {e}")
    
    async def get_with_version_check(self, key: str, entity_id: str, entity_type: str = "user"):
        """获取带版本检查的缓存（核心方法）"""
        try:
            # 1. 获取当前版本号
            current_version = await self.get_entity_version(entity_id, entity_type)
            
            # 2. 尝试从内存缓存获取
            memory_key = f"{key}:v{current_version}"
            if memory_key in self.memory_cache:
                cache_data = self.memory_cache[memory_key]
                if self._is_cache_valid(cache_data):
                    self.cache_stats["hits"] += 1
                    return cache_data["value"]
            
            # 3. 尝试从 Redis 获取
            if self.redis_client:
                redis_key = f"{key}:v{current_version}"
                cache_data = await self._get_from_redis(redis_key)
                
                if cache_data and self._is_cache_valid(cache_data):
                    # 缓存命中，更新内存缓存
                    if self._is_hot_data(key):
                        self.memory_cache[memory_key] = cache_data
                    self.cache_stats["hits"] += 1
                    return cache_data["value"]
            
            # 4. 缓存未命中
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"获取版本化缓存失败: {e}")
            return None
    
    async def invalidate_entity_cache(self, entity_id: str, entity_type: str = "user", reason: str = "数据更新"):
        """失效实体所有相关缓存（核心方法）"""
        try:
            # 1. 递增版本号
            new_version = await self.increment_entity_version(entity_id, entity_type)
            
            # 2. 失效所有相关缓存
            patterns = self._get_invalidation_patterns(entity_id, entity_type)
            
            for pattern in patterns:
                await self._invalidate_pattern(pattern)
            
            # 3. 记录失效日志
            await self._log_invalidation(entity_id, entity_type, reason, patterns, new_version)
            
            logger.info(f"实体 {entity_type}:{entity_id} 缓存已失效，新版本: {new_version}")
            
        except Exception as e:
            logger.error(f"失效实体缓存失败: {e}")
            raise
    
    def _get_invalidation_patterns(self, entity_id: str, entity_type: str) -> list:
        """获取需要失效的缓存模式"""
        patterns = []
        
        # 基础模式
        if entity_type == "user":
            patterns.extend([
                f"user:profile:{entity_id}:*",
                f"ai:blueprint:{entity_id}:*",
                f"ai:daily_fortune:{entity_id}:*",
                f"ai:heart_compass:{entity_id}:*"
            ])
        elif entity_type == "blueprint":
            patterns.extend([
                f"ai:blueprint:{entity_id}:*",
                f"ai:daily_fortune:{entity_id}:*"
            ])
        
        return patterns
    
    def _is_cache_valid(self, cache_data: dict) -> bool:
        """检查缓存是否有效"""
        try:
            if not cache_data:
                return False
            
            # 检查过期时间
            if "expire_at" in cache_data:
                expire_time = datetime.fromisoformat(cache_data["expire_at"])
                if datetime.now() > expire_time:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"缓存有效性检查失败: {e}")
            return False
    
    def _is_hot_data(self, key: str) -> bool:
        """判断是否为热点数据"""
        hot_patterns = [
            "user:profile",
            "ai:blueprint",
            "ai:daily_fortune"
        ]
        return any(pattern in key for pattern in hot_patterns)
    
    async def _get_from_redis(self, key: str):
        """从 Redis 获取数据"""
        try:
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
        except Exception as e:
            logger.error(f"从 Redis 获取数据失败: {e}")
        return None
    
    async def _invalidate_pattern(self, pattern: str):
        """失效匹配模式的缓存"""
        try:
            # 这里可以实现模式匹配的缓存失效
            # 简化实现：直接删除内存中的相关缓存
            keys_to_delete = []
            for key in self.memory_cache.keys():
                if pattern.replace("*", "") in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
            
            logger.debug(f"已失效模式 {pattern} 的缓存，删除 {len(keys_to_delete)} 个")
            
        except Exception as e:
            logger.error(f"失效模式缓存失败: {e}")
    
    async def _log_invalidation(self, entity_id: str, entity_type: str, reason: str, patterns: list, new_version: int):
        """记录缓存失效日志"""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "entity_id": entity_id,
                "entity_type": entity_type,
                "reason": reason,
                "patterns": patterns,
                "new_version": new_version
            }
            
            logger.info(f"缓存失效日志: {json.dumps(log_data, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"记录缓存失效日志失败: {e}")
    
    def get_cache_stats(self):
        """获取缓存统计信息"""
        return self.cache_stats.copy()

    async def get_entity_cache(self, cache_key: str) -> Optional[Any]:
        """获取实体缓存（简化版本）"""
        try:
            if self.redis_client:
                # 从Redis获取
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                # 从内存缓存获取
                if cache_key in self.memory_cache:
                    return self.memory_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"获取实体缓存失败: {e}")
            return None

# 缓存装饰器
def versioned_cache(entity_type: str = "user", expire: int = 3600):
    """版本化缓存装饰器 - 自动处理版本号"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中提取 entity_id
            entity_id = kwargs.get('user_id') or args[0] if args else None
            
            if not entity_id:
                # 如果没有 entity_id，使用传统缓存
                return await func(*args, **kwargs)
            
            # 构建缓存键
            cache_key = f"{func.__name__}:{entity_id}"
            
            # 尝试从版本化缓存获取
            cache_manager = VersionedCacheManager()
            cached_result = await cache_manager.get_with_version_check(
                cache_key, entity_id, entity_type
            )
            
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            
            # 设置版本化缓存
            await cache_manager.set_with_version(
                cache_key, result, entity_id, entity_type, expire
            )
            
            return result
        return wrapper
    return decorator
