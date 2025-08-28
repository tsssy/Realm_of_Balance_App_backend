# 缓存与数据库机制详解

## 概述

本项目采用三层存储架构，通过版本化缓存系统实现高性能、零脏数据风险的数据访问机制。

## 架构设计

```
前端浏览器缓存 (localStorage) 
    ↓
服务器端缓存 (Redis + 内存缓存)
    ↓  
持久化数据库 (MongoDB)
```

## 1. 前端缓存机制（用户设备缓存）

### 1.1 存储内容
- **用户身份信息**：`user_id`、`device_id`
- **会话状态**：当前操作状态、临时数据
- **后端返回的数据**：API响应结果

### 1.2 存储位置
```javascript
// localStorage 存储
localStorage.setItem('user_id', userId);           // 用户ID
localStorage.setItem('device_id', deviceId);       // 设备ID
localStorage.setItem('heartCompass_guidanceData', JSON.stringify(guidanceRecord));  // 指导数据
localStorage.setItem('heartCompass_question', userQuestion);                        // 用户问题
```

### 1.3 特点
- **持久化存储**：关闭浏览器、重启设备后数据仍然存在
- **域名隔离**：每个网站有独立的 localStorage 空间
- **容量限制**：通常 5-10MB，足够存储用户会话数据
- **同步操作**：读写操作是同步的，可能阻塞主线程

## 2. 服务器端缓存机制

### 2.1 版本化缓存系统（核心创新）

**设计理念**：
- 每个实体（用户、蓝图等）都有版本号
- 缓存键包含版本号：`cache_key = f"{key}:v{version}"`
- 数据更新时版本号递增，旧版本自动失效

**缓存层级**：
1. **Redis 缓存**（主缓存）
   - 分布式缓存，支持多服务器实例
   - 持久化存储，重启后数据不丢失
   - 支持过期时间自动清理

2. **内存缓存**（热点数据）
   - 服务器进程内存中的缓存
   - 访问速度最快
   - 重启后数据丢失

### 2.2 版本化缓存工作流程

#### 数据读取流程
```
用户请求数据
    ↓
1. 获取实体当前版本号
   ├── 查询 user:123:version → 返回 5
   └── 构建缓存键: user:profile:123:v5
    ↓
2. 检查内存缓存
   ├── 查找 user:profile:123:v5
   ├── 找到 → 返回缓存数据 ✅
   └── 未找到 → 继续步骤3
    ↓
3. 检查Redis缓存
   ├── 查找 user:profile:123:v5
   ├── 找到 → 返回缓存数据，更新内存缓存 ✅
   └── 未找到 → 继续步骤4
    ↓
4. 查询数据库
   ├── MongoDB.users.find({"userId": "123"})
   ├── 获取最新数据
   └── 缓存结果到 user:profile:123:v5
    ↓
5. 返回数据给用户
```

#### 数据更新流程
```
用户更新数据
    ↓
1. 更新数据库
   ├── MongoDB.users.update_one({"userId": "123"}, new_data)
   └── 数据库已更新
    ↓
2. 递增版本号
   ├── 当前版本: user:123:version = 5
   ├── 新版本: user:123:version = 6
   └── 版本号已递增
    ↓
3. 旧版本缓存自动失效
   ├── 旧缓存键: user:profile:123:v5 ← 无法匹配新版本号
   ├── 新缓存键: user:profile:123:v6 ← 新请求使用此键
   └── 旧缓存自然失效
    ↓
4. 下次请求
   ├── 用户请求 → 获取版本号 6
   ├── 查找缓存: user:profile:123:v6
   ├── 未找到 → 查询数据库
   └── 获取最新数据并缓存
```

## 3. 数据库机制（MongoDB）

### 3.1 数据模型设计
- **用户数据**：`users` 集合存储用户基本信息
- **蓝图数据**：`blueprint_results` 集合存储算命结果
- **指导数据**：`heart_compass_records` 集合存储指导记录
- **运势数据**：`daily_fortune_records` 集合存储每日运势

### 3.2 数据库连接管理
```python
class Database:
    """MongoDB 数据库连接管理类"""
    
    @classmethod
    async def connect(cls):
        """连接到 MongoDB"""
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.db = cls.client[settings.MONGODB_DB_NAME]
    
    @classmethod
    async def find_one(cls, collection_name: str, filter_dict: dict):
        """查找单个文档"""
        document = await cls.get_collection(collection_name).find_one(filter_dict)
        return document
```

## 4. 三者联动机制

### 4.1 数据读取流程
```
1. 前端请求 → 2. 检查服务器内存缓存 → 3. 检查 Redis 缓存 → 4. 查询 MongoDB → 5. 缓存结果 → 6. 返回数据
```

### 4.2 数据更新流程
```
1. 前端更新请求 → 2. 更新 MongoDB → 3. 递增版本号 → 4. 旧缓存自动失效 → 5. 新请求获取最新数据
```

### 4.3 依赖关系管理
```python
dependency_map = {
    "user:profile": ["ai:blueprint", "ai:daily_fortune", "ai:heart_compass"],
    "ai:blueprint": ["ai:daily_fortune"],
    "ai:daily_fortune": [],
    "ai:heart_compass": []
}
```

## 5. 新建数据流程

### 5.1 完整流程
```
用户请求生成新蓝图
    ↓
1. 前端发送请求
   ├── 对象：ElementalAnalysis.tsx
   ├── 操作：调用 BlueprintApiService.generateBlueprintQuick()
   └── 发送：POST /api/v1/blueprint/quick
    ↓
2. 服务器接收请求
   ├── 对象：BlueprintService.generate_blueprint_quick()
   ├── 操作：检查缓存
   └── 缓存键：ai:blueprint:123:v3
    ↓
3. 缓存检查
   ├── 内存缓存：未命中
   ├── Redis缓存：未命中
   └── 结果：缓存未命中
    ↓
4. 生成新数据
   ├── 对象：AIService
   ├── 操作：调用 Gemini API 生成蓝图数据
   └── 结果：生成新的蓝图数据
    ↓
5. 存储到数据库
   ├── 对象：Database
   ├── 操作：MongoDB.blueprint_results.insert_one()
   └── 结果：数据库存储成功
    ↓
6. 版本号递增
   ├── 对象：VersionedCacheManager
   ├── 操作：increment_entity_version("123", "blueprint")
   └── 版本号：blueprint:123:version = 3 → 4
    ↓
7. 失效旧缓存
   ├── 对象：VersionedCacheManager
   ├── 操作：invalidate_entity_cache("123", "blueprint")
   └── 失效：ai:blueprint:123:v3 (旧版本)
    ↓
8. 缓存新数据
   ├── 对象：VersionedCacheManager
   ├── 操作：set_with_version()
   ├── 缓存键：ai:blueprint:123:v4
   └── 结果：新数据已缓存
    ↓
9. 返回数据
   ├── 对象：BlueprintService
   └── 结果：前端收到新蓝图数据
```

## 6. 关键对象

### 6.1 前端对象
- **UserApiService**: 用户API服务，管理设备ID和用户ID
- **httpClient**: Axios实例，处理请求拦截和响应拦截
- **localStorage**: 浏览器本地存储，保存用户会话数据
- **ElementalAnalysis.tsx**: 元素分析组件，处理蓝图生成流程

### 6.2 服务器端对象
- **VersionedCacheManager**: 版本化缓存管理器，核心缓存逻辑
- **UserService**: 用户服务，处理用户相关业务逻辑
- **BlueprintService**: 蓝图服务，处理算命相关业务逻辑
- **AIService**: AI服务，调用外部AI API
- **Database**: 数据库操作类，封装MongoDB操作

### 6.3 数据库对象
- **MongoDB**: 主数据库，存储所有业务数据
- **Redis**: 分布式缓存，存储热点数据
- **内存缓存**: 服务器进程内存，存储最热数据

## 7. 配置管理

### 7.1 服务器端配置
```python
# settings.py
REDIS_URL: Optional[str] = None          # Redis 连接地址
CACHE_TTL: int = 3600                    # 缓存过期时间（1小时）
CACHE_MAX_SIZE: int = 1000               # 最大缓存条目数
```

### 7.2 缓存统计
```python
cache_stats = {
    "hits": 0,           # 缓存命中次数
    "misses": 0,         # 缓存未命中次数
    "invalidations": 0,  # 缓存失效次数
    "version_mismatches": 0  # 版本不匹配次数
}
```

## 8. 关键优势

### 8.1 零脏数据风险
- **版本号隔离**：每个缓存项都有唯一版本号
- **自动失效**：数据更新时版本号递增，旧版本自动失效
- **一致性保证**：通过版本号匹配，确保用户始终看到最新数据

### 8.2 高性能
- **多层缓存**：内存 → Redis → 数据库，逐层查找
- **热点数据优先**：热点数据存储在内存中，响应速度极快
- **智能缓存选择**：自动判断数据应该存储在 Redis 还是内存

### 8.3 运维友好
- **完整日志记录**：所有缓存操作都有详细日志
- **统计信息**：缓存命中率、失效次数等统计
- **自动清理**：过期缓存自动清理，防止内存泄漏

## 9. 数据流向总结

```
用户操作 → 前端localStorage → 服务器缓存检查 → 数据库查询 → 缓存更新 → 返回结果 → 前端显示
    ↑                                                                                    ↓
    └─────────────────── 缓存失效 ← 数据更新 ← 用户操作 ←─────────────────────────────────┘
```

## 10. 关键理解点

1. **版本号是核心**：每个实体都有版本号，缓存键包含版本号
2. **失效不是删除**：失效是通过版本号不匹配实现的，不是物理删除
3. **依赖关系管理**：一个实体更新时，相关实体的缓存也会失效
4. **自动一致性**：通过版本号机制，确保数据的一致性
5. **性能优化**：多层缓存架构，确保高性能访问

这个版本化缓存系统从根本上解决了传统缓存的脏数据问题，通过版本号机制确保了数据的一致性和可靠性。
