from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 项目基本信息
    PROJECT_NAME: str = "Realm of Balance App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "realm_of_balance"
    MONGODB_USERNAME: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    MONGODB_AUTH_SOURCE: Optional[str] = None
    
    # Gemini API 配置
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyC3H7E-QNYloxM7jHcLcL9FHEYhqvhoF5M")
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    
    # Kimi API 配置（Moonshot）
    KIMI_API_KEY: str = os.getenv("KIMI_API_KEY", "sk-k6FqWbmEJJa9TKxK39fjCEflSG7JraFGlK2BnhAYcaHi89PJ")
    KIMI_API_URL: str = "https://api.moonshot.cn/v1/chat/completions"
    KIMI_MODEL_NAME: str = "moonshot-v1-8k"
    
    # 豆包API配置（保留，但暂时不使用）
    DOUBAO_API_KEY: str = os.getenv("DOUBAO_API_KEY", "1e65c3d6-b827-4706-9fa8-93732bed0a8a")
    DOUBAO_API_URL: str = "https://api.doubao.com/v1/chat/completions"
    DOUBAO_MODEL_NAME: str = "doubao-seed-1.6-250615"
    
    # 当前使用的AI服务
    CURRENT_AI_SERVICE: str = "gemini"  # gemini, kimi, doubao
    
    # 语音转文字配置
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    WHISPER_DEVICE: str = "cpu"  # cpu, cuda
    MAX_AUDIO_FILE_SIZE: int = 52428800  # 50MB
    # 默认支持的音频容器/编码格式（以逗号分隔）
    SUPPORTED_AUDIO_FORMATS: str = "mp3,wav,m4a,flac,ogg,aac,mp4,webm"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis 配置（可选）
    REDIS_URL: Optional[str] = None
    
    # 服务配置
    PORT: int = 8080  # 改为8080端口，提高移动网络兼容性
    HOST: str = "0.0.0.0"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # AI服务超时配置
    AI_REQUEST_TIMEOUT: int = 60  # 秒
    AI_MAX_RETRIES: int = 3
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    CACHE_MAX_SIZE: int = 1000  # 最大缓存条目数
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
