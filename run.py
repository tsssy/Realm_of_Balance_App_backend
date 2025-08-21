#!/usr/bin/env python3
"""
Realm of Balance App 后端启动脚本
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 启动 {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 服务地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API 文档: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔍 健康检查: http://{settings.HOST}:{settings.PORT}/health")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
