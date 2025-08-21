# Realm of Balance App 后端

## 📚 文档中心

**重要**: 项目文档已重新整理，请查看 `docs/` 文件夹获取完整的技术文档。

### 🚀 快速开始

1. **环境配置**: 查看 [docs/setup/](docs/setup/) 进行环境配置
2. **启动服务**: 按照配置说明启动后端服务
3. **API测试**: 使用 [docs/testing/](docs/testing/) 中的测试脚本验证功能
4. **前端集成**: 参考 [docs/frontend/](docs/frontend/) 进行前端开发

### 📁 文档结构

```
docs/
├── setup/          # 环境配置和API密钥设置
├── testing/        # 测试指南和测试脚本
├── backend/        # 后端架构设计和实现指南
├── business/       # 业务流程和系统架构
├── frontend/       # 前端API集成指南
└── api/            # API接口文档和规范
```

### 🔧 系统状态

**当前状态**: 🟢 完全正常运行
- ✅ 所有26个API接口已测试通过
- ✅ 字段命名完全统一 (snake_case)
- ✅ AI服务完全正常工作
- ✅ 性能优化完成

### 📖 详细文档

- **完整文档**: [docs/README.md](docs/README.md)
- **后端实现**: [docs/backend/](docs/backend/)
- **业务流程**: [docs/business/](docs/business/)
- **前端集成**: [docs/frontend/](docs/frontend/)
- **API规范**: [docs/api/](docs/api/)

基于东方玄学理论的个人命运分析应用后端，提供用户管理、算命分析、Heart Compass 指导和每日运势等功能。

## 🚀 特性

- **版本化缓存系统**：零脏数据风险的高性能缓存
- **AI 集成**：与 Google Gemini API 深度集成
- **用户管理**：完整的用户生命周期管理
- **算命分析**：专业的八字排盘和五行分析
- **Heart Compass**：智能易经指导系统
- **每日运势**：个性化运势生成
- **高性能**：异步处理、智能缓存、自动优化

## 🏗️ 技术架构

- **框架**: FastAPI
- **数据库**: MongoDB (异步驱动)
- **缓存**: Redis + 内存缓存
- **AI 服务**: Google Gemini API
- **认证**: JWT Token
- **日志**: 自定义日志管理器

## 📁 项目结构

```
realm_of_balance_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # 数据库连接管理
│   │   └── cache.py            # 版本化缓存管理
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── user.py         # 用户管理接口
│   │       ├── blueprint.py    # 算命分析接口
│   │       ├── heart_compass.py # Heart Compass接口
│   │       └── daily_fortune.py # 每日运势接口
│   ├── models/                 # Pydantic 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── blueprint.py
│   │   ├── heart_compass.py
│   │   └── daily_fortune.py
│   ├── services/               # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── blueprint_service.py
│   │   ├── heart_compass_service.py
│   │   ├── daily_fortune_service.py
│   │   └── ai_service.py       # AI 服务集成
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py           # 日志管理
│   │   └── prompt_manager.py   # 提示词管理
│   └── prompts/                # AI 提示词模板
│       ├── blueprint.md        # 算命分析提示词
│       ├── heart_compass.md    # Heart Compass提示词
│       └── daily_fortune.md    # 每日运势提示词
├── tests/                      # 测试文件
├── logs/                       # 日志文件
├── requirements.txt             # 依赖包
├── env.example                 # 环境变量示例
└── README.md
```

## 🛠️ 安装和运行

### 1. 环境要求

- Python 3.8+
- MongoDB
- Redis (可选)

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境配置

复制环境变量示例文件并配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，配置必要的环境变量：

```env
# MongoDB 配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=realm_of_balance

# Gemini API 配置
GEMINI_API_KEY=your_gemini_api_key_here

# JWT 配置
SECRET_KEY=your-secret-key-here
```

### 4. 启动应用

```bash
# 开发模式
python run.py

# 或者使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 核心功能

### 版本化缓存系统

- **零脏数据风险**：通过版本号机制确保缓存一致性
- **智能失效**：自动失效相关缓存，避免数据不一致
- **高性能**：Redis + 内存双重缓存，热点数据优先

### AI 服务集成

- **重试机制**：指数退避策略，确保 API 调用稳定性
- **错误处理**：完善的错误处理和备用响应
- **提示词管理**：动态提示词加载和上下文替换

### 用户管理

- **设备识别**：基于设备ID的新老用户识别
- **信息收集**：完整的用户信息收集流程
- **状态管理**：用户状态跟踪和管理

### 算命分析系统

- **八字排盘**：基于二十四节气的准确时间校准
- **五行分析**：专业的五行强度计算和性格分析
- **内在蓝图**：结构化的个人特质报告
- **生命曲线**：未来几年的成长主题预测

### Heart Compass 指导系统

- **易经决策**：基于64卦的智能情境匹配
- **对话流**：四个环节的渐进式指导体验
- **决策协议**：具体的行动指南和建议
- **历史记录**：完整的指导历史管理

### 每日运势系统

- **个性化运势**：基于用户信息的定制化分析
- **时段建议**：早中晚三个时段的行动指导
- **幸运元素**：颜色、方向、数字等幸运信息
- **智能生成**：AI驱动的动态运势内容

## 📚 API 接口

### 用户管理

- `GET /api/v1/user/status` - 检查用户状态
- `POST /api/v1/user/create` - 创建新用户
- `PUT /api/v1/user/{user_id}` - 更新用户信息
- `GET /api/v1/user/{user_id}` - 获取用户信息
- `DELETE /api/v1/user/{user_id}` - 删除用户

### 算命分析

- `POST /api/v1/blueprint/generate` - 生成个人蓝图
- `GET /api/v1/blueprint/{user_id}` - 获取算命结果
- `POST /api/v1/blueprint/{user_id}/regenerate` - 重新生成算命结果
- `DELETE /api/v1/blueprint/{user_id}` - 删除算命结果

### Heart Compass 指导

- `POST /api/v1/heart-compass/seek-guidance` - 获取指导
- `GET /api/v1/heart-compass/{user_id}/history` - 获取指导历史
- `GET /api/v1/heart-compass/guidance/{guidance_id}` - 获取指导详情
- `DELETE /api/v1/heart-compass/guidance/{guidance_id}` - 删除指导记录

### 每日运势

- `POST /api/v1/daily-fortune/generate` - 生成今日运势
- `GET /api/v1/daily-fortune/{user_id}/today` - 获取今日运势
- `GET /api/v1/daily-fortune/{user_id}/history` - 获取运势历史
- `GET /api/v1/daily-fortune/{user_id}/date/{date}` - 获取指定日期运势

## 🧪 测试

```bash
# 运行测试
pytest

# 运行特定测试
pytest tests/test_user.py
```

## 📊 监控和日志

- **日志文件**: `logs/` 目录
- **健康检查**: `GET /health`
- **缓存统计**: 通过缓存管理器获取统计信息

## 🔒 安全特性

- **输入验证**：Pydantic 模型验证
- **错误处理**：全局异常处理器
- **CORS 配置**：可配置的跨域策略

## 🚀 部署

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 生产环境配置

- 设置 `HOST=0.0.0.0`
- 配置 `MONGODB_URL` 和 `REDIS_URL`
- 设置 `SECRET_KEY`
- 配置日志级别和文件路径

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交 Issue 或联系开发团队。
