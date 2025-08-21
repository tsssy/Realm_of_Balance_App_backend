import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from app.core.database import Database
from app.core.cache import versioned_cache, VersionedCacheManager
from app.models.user import UserCreate, UserUpdate, UserInDB, UserResponse, UserStatusResponse, UserStatusData
from app.utils.logger import MyLogger

logger = MyLogger("user_service")

class UserService:
    """用户服务类"""
    
    def __init__(self):
        self.cache_manager = VersionedCacheManager()
    
    @versioned_cache(entity_type="user", expire=3600)
    async def get_user_profile(self, user_id: str):
        """获取用户信息 - 自动版本化缓存"""
        try:
            # 从数据库获取用户信息
            user = await Database.find_one("users", {"user_id": user_id})
            if user:
                return UserInDB(**user)
            return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            raise
    
    async def get_user_by_device_id(self, device_id: str) -> Optional[UserInDB]:
        """根据设备ID获取用户"""
        try:
            user = await Database.find_one("users", {"device_id": device_id})
            if user:
                return UserInDB(**user)
            return None
        except Exception as e:
            logger.error(f"根据设备ID获取用户失败: {e}")
            raise
    
    async def create_user(self, user_create: UserCreate) -> UserInDB:
        """创建新用户"""
        try:
            # 检查设备ID是否已存在
            existing_user = await self.get_user_by_device_id(user_create.device_id)
            if existing_user:
                raise ValueError("设备ID已存在")
            
            # 生成用户ID
            user_id = str(uuid.uuid4())
            now = datetime.now()
            
            # 构建用户数据
            user_data = {
                "user_id": user_id,
                "device_id": user_create.device_id,
                "gender": user_create.profile.gender,
                "birth_date": user_create.profile.birth_date,
                "birth_time": user_create.profile.birth_time,
                "birth_location": user_create.profile.birth_location,
                "is_new_user": True,
                "created_at": now,
                "updated_at": now,
                "last_login_at": now
            }
            
            # 插入数据库
            result = await Database.insert_one("users", user_data)
            
            # 添加数据库返回的ID
            user_data["_id"] = result
            
            # 创建用户对象
            user = UserInDB(**user_data)
            
            logger.info(f"用户创建成功: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            raise
    
    async def update_user_profile(self, user_id: str, user_update: UserUpdate) -> UserInDB:
        """更新用户信息"""
        try:
            # 检查用户是否存在
            existing_user = await self.get_user_profile(user_id)
            if not existing_user:
                raise ValueError("用户不存在")
            
            # 构建更新数据
            update_data = {
                "gender": user_update.profile.gender,
                "birth_date": user_update.profile.birth_date,
                "birth_time": user_update.profile.birth_time,
                "birth_location": user_update.profile.birth_location,
                "updated_at": datetime.now(),
                "is_new_user": False
            }
            
            # 更新数据库
            await Database.update_one(
                "users",
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            # 失效用户所有相关缓存（自动递增版本号）
            await self.cache_manager.invalidate_entity_cache(
                user_id, "user", "用户信息更新"
            )
            
            # 获取更新后的用户信息
            updated_user = await self.get_user_profile(user_id)
            
            logger.info(f"用户信息更新成功: {user_id}")
            return updated_user
            
        except Exception as e:
            logger.error(f"更新用户信息失败: {e}")
            raise
    
    async def check_user_status(self, device_id: str) -> UserStatusResponse:
        """检查用户状态"""
        try:
            # 根据设备ID查找用户
            user = await self.get_user_by_device_id(device_id)
            
            if user:
                # 老用户
                has_blueprint = await self._check_has_blueprint(user.user_id)
                
                status_data = UserStatusData(
                    is_new_user=False,
                    user_profile={
                        "user_id": user.user_id,
                        "gender": user.gender,
                        "birth_date": user.birth_date,
                        "birth_time": user.birth_time,
                        "birth_location": user.birth_location
                    },
                    has_blueprint=has_blueprint
                )
                
                return UserStatusResponse(
                    success=True,
                    data=status_data
                )
            else:
                # 新用户
                status_data = UserStatusData(
                    is_new_user=True,
                    user_profile=None,
                    has_blueprint=False
                )
                
                return UserStatusResponse(
                    success=True,
                    data=status_data
                )
                
        except Exception as e:
            logger.error(f"检查用户状态失败: {e}")
            return UserStatusResponse(
                success=False,
                data=None,
                message=f"检查用户状态失败: {str(e)}"
            )
    
    async def _check_has_blueprint(self, user_id: str) -> bool:
        """检查用户是否有算命结果"""
        try:
            count = await Database.count_documents("blueprint_results", {"user_id": user_id})
            return count > 0
        except Exception as e:
            logger.error(f"检查算命结果失败: {e}")
            return False
    
    async def get_user_status_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户状态摘要"""
        try:
            user = await self.get_user_profile(user_id)
            if not user:
                return {}
            
            has_blueprint = await self._check_has_blueprint(user_id)
            
            return {
                "user_id": user.user_id,
                "is_new_user": user.is_new_user,
                "has_blueprint": has_blueprint,
                "last_login_at": user.last_login_at
            }
            
        except Exception as e:
            logger.error(f"获取用户状态摘要失败: {e}")
            return {}
    
    async def update_last_login(self, user_id: str):
        """更新最后登录时间"""
        try:
            await Database.update_one(
                "users",
                {"user_id": user_id},
                {"$set": {"last_login_at": datetime.now()}}
            )
            logger.debug(f"用户 {user_id} 最后登录时间已更新")
        except Exception as e:
            logger.error(f"更新最后登录时间失败: {e}")
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        try:
            # 删除用户信息
            await Database.delete_one("users", {"user_id": user_id})
            
            # 删除算命结果
            await Database.delete_many("blueprint_results", {"user_id": user_id})
            
            # 删除每日运势
            await Database.delete_many("daily_fortune_records", {"user_id": user_id})
            
            # 删除 Heart Compass 记录
            await Database.delete_many("heart_compass_records", {"user_id": user_id})
            
            # 失效用户所有缓存
            await self.cache_manager.invalidate_entity_cache(
                user_id, "user", "用户删除"
            )
            
            logger.info(f"用户 {user_id} 已删除")
            return True
            
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False
