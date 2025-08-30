#!/usr/bin/env python3
"""
本地开发环境启动脚本
启动后端服务在 localhost:8000
使用本地MongoDB数据库 realm_of_balance_local
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动本地开发服务器"""
    
    # 设置环境变量
    os.environ['ENVIRONMENT'] = 'local'
    os.environ['HOST'] = 'localhost'
    os.environ['PORT'] = '8000'
    os.environ['MONGODB_DB_NAME'] = 'realm_of_balance_local'
    
    print("🚀 启动本地开发环境...")
    print("📍 后端服务: http://localhost:8000")
    print("📍 API文档: http://localhost:8000/docs")
    print("📍 数据库: realm_of_balance_local")
    print("=" * 50)
    
    try:
        # 启动服务器
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', 'localhost',
            '--port', '8000',
            '--reload',
            '--log-level', 'info'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
