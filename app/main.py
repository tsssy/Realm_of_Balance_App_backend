from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database import Database
from app.api.v1 import user, blueprint, heart_compass, daily_fortune, admin
from app.utils.logger import MyLogger

logger = MyLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("应用启动中...")
    try:
        await Database.connect()
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise
    
    yield
    
    # 关闭时
    logger.info("应用关闭中...")
    try:
        await Database.close()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Realm of Balance App 后端 API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS - 本地开发环境
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",             # 本地前端开发环境
        "http://127.0.0.1:3000",             # 本地前端开发环境（备用）
        # 生产环境域名（注释保留，方便切换）
        # "https://mystelleastro.com",         # 新的主域名
        # "https://www.mystelleastro.com",     # 新域名的www版本
        # "https://realm.lovetapoversea.xyz",  # 使用子域名
        # "https://8.216.32.239",              # HTTPS IP访问 (主要)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 5000,
                "message": "服务器内部错误",
                "details": str(exc)
            }
        }
    )

# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# 注册路由
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(blueprint.router, prefix=settings.API_V1_STR)
app.include_router(heart_compass.router, prefix=settings.API_V1_STR)
app.include_router(daily_fortune.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": f"欢迎使用 {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    )
