import sys
from pathlib import Path
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional, List, Dict, Any

# 添加项目根目录到路径
ROOT_PATH = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_PATH))

from app.config import settings
from app.utils.logger import MyLogger

logger = MyLogger("database")

def convert_objectid_to_str(data):
    """将字典中的所有ObjectID转换为字符串"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, ObjectId):
                data[key] = str(value)
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        convert_objectid_to_str(item)
    return data

class Database:
    """MongoDB 数据库连接管理类"""
    
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        """连接到 MongoDB"""
        try:
            # 构建连接参数
            connection_params = {
                'serverSelectionTimeoutMS': 5000
            }
            
            # 只有当有有效的认证信息时才添加认证参数
            if settings.MONGODB_USERNAME and settings.MONGODB_USERNAME.strip():
                connection_params['username'] = settings.MONGODB_USERNAME
            if settings.MONGODB_PASSWORD and settings.MONGODB_PASSWORD.strip():
                connection_params['password'] = settings.MONGODB_PASSWORD
            if settings.MONGODB_AUTH_SOURCE and settings.MONGODB_AUTH_SOURCE.strip():
                connection_params['authSource'] = settings.MONGODB_AUTH_SOURCE
            
            # 使用同步客户端测试连接
            test_client = MongoClient(settings.MONGODB_URL, **connection_params)
            test_client.server_info()  # 测试连接
            test_client.close()

            # 创建异步客户端
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL, **connection_params)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close(cls):
        """关闭 MongoDB 连接"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_db(cls):
        """获取数据库实例"""
        return cls.db

    @classmethod
    def get_collection(cls, collection_name: str):
        """获取集合实例"""
        return cls.get_db()[collection_name]

    @classmethod
    async def insert_one(cls, collection_name: str, document: dict):
        """插入单个文档"""
        try:
            result = await cls.get_collection(collection_name).insert_one(document)
            logger.info(f"Inserted document with id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise

    @classmethod
    async def insert_many(cls, collection_name: str, documents: list):
        """插入多个文档"""
        try:
            result = await cls.get_collection(collection_name).insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents")
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Error inserting documents: {e}")
            raise

    @classmethod
    async def find_one(cls, collection_name: str, filter_dict: dict):
        """查找单个文档"""
        try:
            document = await cls.get_collection(collection_name).find_one(filter_dict)
            if document:
                convert_objectid_to_str(document)
            return document
        except Exception as e:
            logger.error(f"Error finding document: {e}")
            raise

    @classmethod
    async def find(cls, collection_name: str, filter_dict: dict, sort=None, limit=None):
        """查找多个文档"""
        try:
            cursor = cls.get_collection(collection_name).find(filter_dict)
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            documents = await cursor.to_list(length=None)
            
            # 转换所有文档的ObjectID
            for doc in documents:
                convert_objectid_to_str(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            raise

    @classmethod
    async def update_one(cls, collection_name: str, filter_dict: dict, update_dict: dict, upsert=False):
        """更新单个文档"""
        try:
            result = await cls.get_collection(collection_name).update_one(
                filter_dict, update_dict, upsert=upsert
            )
            logger.info(f"Updated {result.modified_count} document(s)")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise

    @classmethod
    async def update_many(cls, collection_name: str, filter_dict: dict, update_dict: dict, upsert=False):
        """更新多个文档"""
        try:
            result = await cls.get_collection(collection_name).update_many(
                filter_dict, update_dict, upsert=upsert
            )
            logger.info(f"Updated {result.modified_count} document(s)")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise

    @classmethod
    async def delete_one(cls, collection_name: str, filter_dict: dict):
        """删除单个文档"""
        try:
            result = await cls.get_collection(collection_name).delete_one(filter_dict)
            logger.info(f"Deleted {result.deleted_count} document(s)")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise

    @classmethod
    async def delete_many(cls, collection_name: str, filter_dict: dict):
        """删除多个文档"""
        try:
            result = await cls.get_collection(collection_name).delete_many(filter_dict)
            logger.info(f"Deleted {result.deleted_count} document(s)")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise

    @classmethod
    async def count_documents(cls, collection_name: str, filter_dict: dict):
        """统计文档数量"""
        try:
            count = await cls.get_collection(collection_name).count_documents(filter_dict)
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise

    @classmethod
    async def aggregate(cls, collection_name: str, pipeline: list):
        """执行聚合查询"""
        try:
            cursor = cls.get_collection(collection_name).aggregate(pipeline)
            documents = await cursor.to_list(length=None)
            
            # 转换所有文档的ObjectID
            for doc in documents:
                convert_objectid_to_str(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error executing aggregation: {e}")
            raise
