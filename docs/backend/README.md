# 后端架构和实现指南

## 📋 概述

本目录包含 Realm of Balance App 后端的架构设计、技术实现和开发指南等核心文档。

## 📁 目录结构

```
backend/
├── README.md                           # 本文件 - 后端指南说明
└── BACKEND_IMPLEMENTATION_GUIDE.md    # 详细的后端实现指南
```

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用      │    │   API 网关      │    │   后端服务      │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   缓存层        │    │   数据库层      │
                       │   (Redis)       │    │   (MongoDB)     │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   AI 服务       │    │   外部服务      │
                       │   (Gemini)      │    │   (第三方API)   │
                       └─────────────────┘    └─────────────────┘
```

### 技术栈

- **Web 框架**: FastAPI
- **数据库**: MongoDB (异步驱动)
- **缓存**: Redis + 内存缓存
- **AI 服务**: Google Gemini API
- **认证**: JWT Token
- **日志**: 自定义日志管理器
- **测试**: pytest + httpx

## 🚀 核心特性

### 1. 版本化缓存系统

- **零脏数据风险**: 通过版本号机制确保缓存一致性
- **智能失效**: 自动失效相关缓存，避免数据不一致
- **高性能**: Redis + 内存双重缓存，热点数据优先

### 2. AI 服务集成

- **重试机制**: 指数退避策略，确保 API 调用稳定性
- **错误处理**: 完善的错误处理和备用响应
- **提示词管理**: 动态提示词加载和上下文替换

### 3. 异步处理

- **高性能**: 基于 asyncio 的异步架构
- **并发处理**: 支持大量并发请求
- **资源优化**: 智能连接池管理

## 📁 项目结构

### 目录组织

```
app/
├── __init__.py                 # 应用初始化
├── main.py                     # FastAPI 应用入口
├── config/                     # 配置管理
│   ├── __init__.py
│   ├── settings.py            # 应用设置
│   └── prompt_config.py       # 提示词配置
├── core/                       # 核心功能
│   ├── __init__.py
│   ├── database.py            # 数据库连接管理
│   └── cache.py               # 版本化缓存管理
├── api/                        # API 接口
│   ├── __init__.py
│   └── v1/                    # API 版本 1
│       ├── __init__.py
│       ├── user.py            # 用户管理接口
│       ├── blueprint.py       # 算命分析接口
│       ├── heart_compass.py   # Heart Compass接口
│       ├── daily_fortune.py   # 每日运势接口
│       └── admin.py           # 管理员接口
├── models/                     # 数据模型
│   ├── __init__.py
│   ├── base.py                # 基础模型
│   ├── user.py                # 用户模型
│   ├── blueprint.py           # 算命模型
│   ├── heart_compass.py       # Heart Compass模型
│   └── daily_fortune.py       # 每日运势模型
├── services/                   # 业务逻辑服务
│   ├── __init__.py
│   ├── user_service.py        # 用户服务
│   ├── blueprint_service.py   # 算命服务
│   ├── heart_compass_service.py # Heart Compass服务
│   ├── daily_fortune_service.py # 每日运势服务
│   └── ai_service.py          # AI 服务集成
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── logger.py              # 日志管理
│   └── prompt_manager.py      # 提示词管理
└── prompts/                    # AI 提示词模板
    ├── blueprint.md            # 算命分析提示词
    ├── heart_compass.md        # Heart Compass提示词
    └── daily_fortune.md        # 每日运势提示词
```

## 🔧 核心组件

### 1. 数据库管理 (Database Manager)

```python
# 异步 MongoDB 连接管理
class DatabaseManager:
    def __init__(self):
        self.client = None
        self.database = None
    
    async def connect(self):
        # 建立数据库连接
        
    async def disconnect(self):
        # 关闭数据库连接
```

**特性**:
- 异步连接池管理
- 自动重连机制
- 连接状态监控

### 2. 缓存管理 (Cache Manager)

```python
# 版本化缓存系统
class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
    
    async def get(self, key: str, version: str = None):
        # 获取缓存数据
        
    async def set(self, key: str, value: Any, version: str = None):
        # 设置缓存数据
```

**特性**:
- 版本号机制
- 双重缓存策略
- 智能失效管理

### 3. AI 服务 (AI Service)

```python
# Gemini API 集成服务
class AIService:
    def __init__(self):
        self.client = None
        self.retry_config = {}
    
    async def generate_response(self, prompt: str, context: dict = None):
        # 生成 AI 响应
        
    async def _retry_with_backoff(self, func, *args, **kwargs):
        # 指数退避重试
```

**特性**:
- 智能重试机制
- 上下文管理
- 错误处理

## 📊 数据模型

### 基础模型

```python
class BaseModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
```

### 用户模型

```python
class User(BaseModel):
    device_id: str = Field(..., description="设备唯一标识")
    name: Optional[str] = Field(None, description="用户姓名")
    birth_date: Optional[datetime] = Field(None, description="出生日期")
    birth_time: Optional[str] = Field(None, description="出生时间")
    gender: Optional[str] = Field(None, description="性别")
    # ... 其他字段
```

### 算命模型

```python
class Blueprint(BaseModel):
    user_id: str = Field(..., description="用户ID")
    birth_info: dict = Field(..., description="出生信息")
    analysis_result: dict = Field(..., description="分析结果")
    # ... 其他字段
```

## 🔐 安全机制

### 认证和授权

- **JWT Token**: 无状态认证
- **设备识别**: 基于设备ID的用户管理
- **输入验证**: Pydantic 模型验证
- **CORS 配置**: 可配置的跨域策略

### 数据安全

- **参数验证**: 严格的输入验证
- **SQL 注入防护**: 使用参数化查询
- **敏感信息保护**: 环境变量管理
- **日志脱敏**: 敏感信息不记录

## 📈 性能优化

### 缓存策略

1. **热点数据缓存**: 用户信息、配置等
2. **计算结果缓存**: AI 分析结果、运势数据
3. **版本控制**: 避免缓存不一致问题

### 数据库优化

1. **索引优化**: 关键字段建立索引
2. **连接池**: 异步连接池管理
3. **查询优化**: 避免 N+1 查询问题

### 异步处理

1. **并发请求**: 支持大量并发用户
2. **非阻塞 I/O**: 提高系统吞吐量
3. **资源管理**: 智能资源分配

## 🧪 测试策略

### 测试类型

- **单元测试**: 测试单个函数和类
- **集成测试**: 测试组件间交互
- **API 测试**: 测试 HTTP 接口
- **性能测试**: 测试系统性能

### 测试工具

- **pytest**: 测试框架
- **httpx**: HTTP 客户端测试
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 代码覆盖率

## 📚 开发指南

### 代码规范

1. **命名规范**: 使用 snake_case
2. **类型注解**: 完整的类型提示
3. **文档字符串**: 详细的函数说明
4. **错误处理**: 统一的错误处理机制

### 新功能开发

1. **需求分析**: 明确功能需求
2. **设计阶段**: 设计数据模型和接口
3. **实现阶段**: 编写业务逻辑
4. **测试阶段**: 编写测试用例
5. **文档更新**: 更新相关文档

### 调试技巧

1. **日志记录**: 使用结构化日志
2. **断点调试**: IDE 断点调试
3. **性能分析**: 使用性能分析工具
4. **错误追踪**: 完善的错误堆栈

## 🚨 常见问题

### 1. 数据库连接问题

- 检查 MongoDB 服务状态
- 验证连接字符串格式
- 检查网络连接和防火墙

### 2. 缓存失效问题

- 检查 Redis 服务状态
- 验证版本号机制
- 检查缓存配置

### 3. AI 服务问题

- 验证 API 密钥
- 检查网络连接
- 查看错误日志

## 📚 相关文档

- [API 接口文档](../api/README.md)
- [业务流程说明](../business/BUSINESS_FLOW.md)
- [前端集成指南](../frontend/FRONTEND_API_INTEGRATION_GUIDE.md)
- [测试指南](../testing/TESTING_GUIDE.md)
- [环境配置指南](../setup/README.md)

## 💡 最佳实践

1. **架构设计**
   - 遵循单一职责原则
   - 使用依赖注入
   - 保持模块间低耦合

2. **性能优化**
   - 合理使用缓存
   - 优化数据库查询
   - 异步处理耗时操作

3. **安全考虑**
   - 输入验证和清理
   - 敏感信息保护
   - 定期安全审计

4. **代码质量**
   - 编写测试用例
   - 代码审查
   - 持续集成

## 📞 支持

如遇到技术问题，请：
1. 查看相关日志
2. 检查配置参数
3. 运行测试用例
4. 联系开发团队
