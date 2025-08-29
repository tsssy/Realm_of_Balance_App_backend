#!/usr/bin/env python3
"""
Realm of Balance App 生产环境启动脚本
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 启动生产环境 {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 服务地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API 文档: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔍 健康检查: http://{settings.HOST}:{settings.PORT}/health")
    print("-" * 50)
    
    # 生产环境配置
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # 生产环境关闭自动重载
        workers=4,     # 使用多进程提高性能
        log_level="info",
        access_log=True,
        use_colors=False,  # 生产环境关闭颜色输出
    )
