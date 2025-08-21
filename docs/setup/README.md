# 环境配置和设置指南

## 📋 概述

本目录包含 Realm of Balance App 后端的环境配置、API 密钥设置和部署相关的所有文档。

## 📁 目录结构

```
setup/
├── README.md                    # 本文件 - 设置指南说明
└── API_KEYS_SETUP.md           # API 密钥配置详细说明
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **MongoDB**: 4.4+
- **Redis**: 6.0+ (可选，用于缓存)
- **操作系统**: Linux/macOS/Windows

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository_url>
   cd realm_of_balance_backend
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **环境配置**
   ```bash
   cp env.example .env
   # 编辑 .env 文件配置环境变量
   ```

5. **启动服务**
   ```bash
   python run.py
   ```

## 🔧 环境配置

### 必需的环境变量

```env
# MongoDB 配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=realm_of_balance

# Gemini API 配置
GEMINI_API_KEY=your_gemini_api_key_here

# JWT 配置
SECRET_KEY=your-secret-key-here

# 应用配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 可选的环境变量

```env
# Redis 配置 (可选)
REDIS_URL=redis://localhost:6379

# 日志配置
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/

# CORS 配置
ALLOWED_ORIGINS=["http://localhost:3000"]

# 缓存配置
CACHE_TTL=3600
```

## 🔑 API 密钥配置

### Gemini API 设置

1. **获取 API 密钥**
   - 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 创建新的 API 密钥
   - 复制密钥到 `.env` 文件

2. **配置环境变量**
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **验证配置**
   ```bash
   python -c "from app.services.ai_service import AIService; print('配置成功')"
   ```

### 其他 API 配置

根据项目需要，可能还需要配置：
- 短信服务 API
- 邮件服务 API
- 支付网关 API
- 第三方认证 API

## 🗄️ 数据库配置

### MongoDB 设置

1. **安装 MongoDB**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb
   
   # macOS
   brew install mongodb-community
   
   # Windows
   # 下载并安装 MongoDB Community Server
   ```

2. **启动 MongoDB 服务**
   ```bash
   # Linux/macOS
   sudo systemctl start mongod
   
   # macOS (Homebrew)
   brew services start mongodb-community
   ```

3. **创建数据库和用户**
   ```bash
   mongosh
   use realm_of_balance
   db.createUser({
     user: "app_user",
     pwd: "secure_password",
     roles: ["readWrite"]
   })
   ```

### Redis 设置 (可选)

1. **安装 Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   ```

2. **启动 Redis 服务**
   ```bash
   # Linux
   sudo systemctl start redis
   
   # macOS
   brew services start redis
   ```

## 🌐 网络配置

### 端口配置

- **应用端口**: 8000 (默认)
- **MongoDB**: 27017 (默认)
- **Redis**: 6379 (默认)

### 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw allow 8000
sudo ufw allow 27017
sudo ufw allow 6379

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=27017/tcp
sudo firewall-cmd --permanent --add-port=6379/tcp
sudo firewall-cmd --reload
```

## 📁 文件权限

### 日志目录

```bash
# 创建日志目录
mkdir -p logs

# 设置权限
chmod 755 logs
chown $USER:$USER logs
```

### 配置文件

```bash
# 设置 .env 文件权限
chmod 600 .env
```

## 🐳 Docker 配置

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:7.0
    ports:
      - "6379:6379"

volumes:
  mongo_data:
```

### 构建镜像

```bash
docker build -t realm-of-balance-backend .
docker run -p 8000:8000 realm-of-balance-backend
```

## 🔍 配置验证

### 健康检查

```bash
# 检查应用状态
curl http://localhost:8000/health

# 检查数据库连接
python -c "from app.core.database import get_database; print('数据库连接正常')"

# 检查缓存连接
python -c "from app.core.cache import get_cache; print('缓存连接正常')"
```

### 日志检查

```bash
# 查看应用日志
tail -f logs/main.log

# 查看数据库日志
tail -f logs/database.log

# 查看缓存日志
tail -f logs/cache.log
```

## 🚨 常见问题

### 1. MongoDB 连接失败

```bash
# 检查 MongoDB 服务状态
sudo systemctl status mongod

# 检查端口是否开放
netstat -tlnp | grep 27017
```

### 2. API 密钥无效

```bash
# 验证环境变量
echo $GEMINI_API_KEY

# 检查 .env 文件
cat .env | grep GEMINI_API_KEY
```

### 3. 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

## 📚 相关文档

- [API 密钥设置](API_KEYS_SETUP.md)
- [后端实现指南](../backend/BACKEND_IMPLEMENTATION_GUIDE.md)
- [业务流程说明](../business/BUSINESS_FLOW.md)
- [测试指南](../testing/TESTING_GUIDE.md)

## 💡 最佳实践

1. **安全性**
   - 不要在代码中硬编码敏感信息
   - 使用强密码和安全的密钥
   - 定期轮换 API 密钥

2. **环境管理**
   - 为不同环境使用不同的配置文件
   - 使用环境变量而不是配置文件
   - 版本控制中排除敏感文件

3. **监控**
   - 设置日志轮转
   - 监控服务状态
   - 设置告警机制

## 📞 支持

如遇到配置问题，请：
1. 检查环境变量配置
2. 查看相关日志文件
3. 验证服务状态
4. 联系开发团队
