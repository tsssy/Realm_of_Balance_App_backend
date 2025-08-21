# 测试指南和策略

## 📋 概述

本目录包含 Realm of Balance App 后端的测试策略、测试用例和测试工具使用指南等所有测试相关文档。

## 📁 目录结构

```
testing/
├── README.md                    # 本文件 - 测试指南说明
└── TESTING_GUIDE.md            # 详细的测试指南文档
```

## 🧪 测试策略

### 测试金字塔

```
        /\
       /  \      E2E 测试 (端到端)
      /____\     少量，覆盖关键用户流程
     /      \
    /        \   集成测试
   /__________\   中等数量，测试组件交互
  /            \
 /              \  单元测试
/________________\  大量，测试单个函数/类
```

### 测试类型

1. **单元测试 (Unit Tests)**
   - 测试单个函数、类或方法
   - 快速执行，易于调试
   - 覆盖核心业务逻辑

2. **集成测试 (Integration Tests)**
   - 测试组件间的交互
   - 验证数据流和接口
   - 测试数据库和缓存集成

3. **API 测试 (API Tests)**
   - 测试 HTTP 接口
   - 验证请求/响应格式
   - 测试认证和授权

4. **端到端测试 (E2E Tests)**
   - 测试完整的用户流程
   - 模拟真实用户操作
   - 验证系统整体功能

## 🚀 快速开始

### 环境准备

```bash
# 安装测试依赖
pip install pytest
pip install pytest-asyncio
pip install httpx
pip install pytest-cov
pip install pytest-mock

# 或使用 requirements-dev.txt
pip install -r requirements-dev.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_user.py

# 运行特定测试函数
pytest tests/test_user.py::test_create_user

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 并行运行测试
pytest -n auto
```

## 📁 测试项目结构

### 推荐目录结构

```
tests/
├── __init__.py
├── conftest.py                 # 测试配置和共享 fixtures
├── unit/                       # 单元测试
│   ├── __init__.py
│   ├── test_models.py         # 数据模型测试
│   ├── test_services.py       # 业务逻辑测试
│   └── test_utils.py          # 工具函数测试
├── integration/                # 集成测试
│   ├── __init__.py
│   ├── test_database.py       # 数据库集成测试
│   ├── test_cache.py          # 缓存集成测试
│   └── test_ai_service.py     # AI 服务集成测试
├── api/                        # API 接口测试
│   ├── __init__.py
│   ├── test_user_api.py       # 用户接口测试
│   ├── test_blueprint_api.py  # 算命接口测试
│   ├── test_heart_compass_api.py # Heart Compass接口测试
│   └── test_daily_fortune_api.py # 每日运势接口测试
├── e2e/                        # 端到端测试
│   ├── __init__.py
│   ├── test_user_flow.py      # 用户流程测试
│   └── test_complete_flow.py  # 完整流程测试
└── fixtures/                   # 测试数据
    ├── __init__.py
    ├── user_data.py           # 用户测试数据
    └── test_data.py           # 通用测试数据
```

## 🔧 测试配置

### pytest 配置

```python
# pytest.ini 或 pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--disable-warnings",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html"
]
markers = [
    "unit: 单元测试",
    "integration: 集成测试",
    "api: API 接口测试",
    "e2e: 端到端测试",
    "slow: 慢速测试",
    "database: 数据库相关测试"
]
```

### 测试环境配置

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.core.database import get_database
from app.core.cache import get_cache

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_db():
    """测试数据库连接"""
    db = get_database()
    yield db
    # 清理测试数据

@pytest.fixture
async def test_cache():
    """测试缓存连接"""
    cache = get_cache()
    yield cache
    # 清理测试缓存
```

## 📝 测试用例编写

### 1. 单元测试示例

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.models.user import User

class TestUserService:
    """用户服务单元测试"""
    
    @pytest.fixture
    def user_service(self):
        """创建用户服务实例"""
        return UserService()
    
    @pytest.fixture
    def mock_user_data(self):
        """模拟用户数据"""
        return {
            "device_id": "test-device-123",
            "name": "测试用户",
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "gender": "男"
        }
    
    def test_create_user_success(self, user_service, mock_user_data):
        """测试成功创建用户"""
        # 模拟数据库操作
        with patch.object(user_service, '_save_user') as mock_save:
            mock_save.return_value = User(**mock_user_data)
            
            result = user_service.create_user(mock_user_data)
            
            assert result.success is True
            assert result.data.name == "测试用户"
            mock_save.assert_called_once()
    
    def test_create_user_invalid_data(self, user_service):
        """测试无效数据创建用户"""
        invalid_data = {"device_id": ""}  # 缺少必要字段
        
        with pytest.raises(ValueError, match="设备ID不能为空"):
            user_service.create_user(invalid_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_device_id(self, user_service):
        """测试通过设备ID获取用户"""
        device_id = "test-device-123"
        
        with patch.object(user_service, '_get_user_from_db') as mock_get:
            mock_get.return_value = User(device_id=device_id, name="测试用户")
            
            result = await user_service.get_user_by_device_id(device_id)
            
            assert result is not None
            assert result.device_id == device_id
            mock_get.assert_called_once_with(device_id)
```

### 2. 集成测试示例

```python
# tests/integration/test_database_integration.py
import pytest
from app.core.database import get_database
from app.models.user import User

class TestDatabaseIntegration:
    """数据库集成测试"""
    
    @pytest.mark.asyncio
    async def test_user_crud_operations(self, test_db):
        """测试用户增删改查操作"""
        # 创建用户
        user_data = {
            "device_id": "test-device-123",
            "name": "测试用户",
            "birth_date": "1990-01-01"
        }
        
        user = User(**user_data)
        result = await test_db.users.insert_one(user.dict())
        assert result.inserted_id is not None
        
        # 查询用户
        found_user = await test_db.users.find_one({"device_id": "test-device-123"})
        assert found_user is not None
        assert found_user["name"] == "测试用户"
        
        # 更新用户
        update_result = await test_db.users.update_one(
            {"device_id": "test-device-123"},
            {"$set": {"name": "更新后的用户名"}}
        )
        assert update_result.modified_count == 1
        
        # 删除用户
        delete_result = await test_db.users.delete_one({"device_id": "test-device-123"})
        assert delete_result.deleted_count == 1
        
        # 验证删除
        deleted_user = await test_db.users.find_one({"device_id": "test-device-123"})
        assert deleted_user is None
```

### 3. API 测试示例

```python
# tests/api/test_user_api.py
import pytest
from httpx import AsyncClient

class TestUserAPI:
    """用户 API 接口测试"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, client: AsyncClient):
        """测试成功创建用户"""
        user_data = {
            "device_id": "test-device-123",
            "name": "测试用户",
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "gender": "男"
        }
        
        response = await client.post("/api/v1/user/create", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "测试用户"
        assert "user_id" in data["data"]
    
    @pytest.mark.asyncio
    async def test_create_user_missing_device_id(self, client: AsyncClient):
        """测试缺少设备ID创建用户"""
        user_data = {
            "name": "测试用户",
            "birth_date": "1990-01-01"
        }
        
        response = await client.post("/api/v1/user/create", json=user_data)
        
        assert response.status_code == 422  # 验证错误
        data = response.json()
        assert "device_id" in str(data["detail"])
    
    @pytest.mark.asyncio
    async def test_get_user_status(self, client: AsyncClient):
        """测试获取用户状态"""
        device_id = "test-device-123"
        
        response = await client.get(f"/api/v1/user/status?device_id={device_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data["data"]
        assert "exists" in data["data"]
    
    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient):
        """测试更新用户信息"""
        # 先创建用户
        user_data = {
            "device_id": "test-device-123",
            "name": "原始用户名",
            "birth_date": "1990-01-01"
        }
        
        create_response = await client.post("/api/v1/user/create", json=user_data)
        user_id = create_response.json()["data"]["user_id"]
        
        # 更新用户
        update_data = {"name": "更新后的用户名"}
        response = await client.put(f"/api/v1/user/{user_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "更新后的用户名"
```

### 4. 端到端测试示例

```python
# tests/e2e/test_user_flow.py
import pytest
from httpx import AsyncClient

class TestUserFlow:
    """用户流程端到端测试"""
    
    @pytest.mark.asyncio
    async def test_complete_user_journey(self, client: AsyncClient):
        """测试完整的用户旅程"""
        device_id = "test-device-e2e-123"
        
        # 1. 检查用户状态
        status_response = await client.get(f"/api/v1/user/status?device_id={device_id}")
        assert status_response.status_code == 200
        
        # 2. 创建用户
        user_data = {
            "device_id": device_id,
            "name": "E2E测试用户",
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "gender": "男"
        }
        
        create_response = await client.post("/api/v1/user/create", json=user_data)
        assert create_response.status_code == 200
        user_id = create_response.json()["data"]["user_id"]
        
        # 3. 生成个人蓝图
        blueprint_data = {
            "user_id": user_id,
            "birth_info": {
                "date": "1990-01-01",
                "time": "12:00",
                "gender": "男"
            }
        }
        
        blueprint_response = await client.post("/api/v1/blueprint/generate", json=blueprint_data)
        assert blueprint_response.status_code == 200
        
        # 4. 获取个人蓝图
        get_blueprint_response = await client.get(f"/api/v1/blueprint/{user_id}")
        assert get_blueprint_response.status_code == 200
        
        # 5. 寻求 Heart Compass 指导
        guidance_data = {
            "user_id": user_id,
            "situation": "我正在考虑是否要换工作，请给我一些建议。"
        }
        
        guidance_response = await client.post("/api/v1/heart-compass/seek-guidance", json=guidance_data)
        assert guidance_response.status_code == 200
        
        # 6. 生成每日运势
        fortune_data = {"user_id": user_id}
        fortune_response = await client.post("/api/v1/daily-fortune/generate", json=fortune_data)
        assert fortune_response.status_code == 200
        
        # 7. 清理测试数据
        await client.delete(f"/api/v1/user/{user_id}")
```

## 🎯 测试数据管理

### 测试数据 Fixtures

```python
# tests/fixtures/user_data.py
import pytest
from datetime import datetime

@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "device_id": "test-device-123",
        "name": "测试用户",
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "gender": "男",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def sample_birth_info():
    """示例出生信息"""
    return {
        "date": "1990-01-01",
        "time": "12:00",
        "gender": "男",
        "location": "北京"
    }

@pytest.fixture
def sample_situation():
    """示例情境描述"""
    return "我正在考虑是否要换工作，请给我一些建议。"
```

### 测试数据清理

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """自动清理测试数据"""
    yield
    # 测试结束后清理
    await cleanup_database()
    await cleanup_cache()

async def cleanup_database():
    """清理数据库测试数据"""
    db = get_database()
    await db.users.delete_many({"device_id": {"$regex": "^test-"}})
    await db.blueprints.delete_many({"user_id": {"$regex": "^test-"}})
    await db.heart_compass.delete_many({"user_id": {"$regex": "^test-"}})
    await db.daily_fortunes.delete_many({"user_id": {"$regex": "^test-"}})

async def cleanup_cache():
    """清理缓存测试数据"""
    cache = get_cache()
    await cache.clear_pattern("test-*")
```

## 📊 测试覆盖率

### 覆盖率配置

```python
# .coveragerc
[run]
source = app
omit = 
    */tests/*
    */migrations/*
    */__init__.py
    */main.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

### 覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest --cov=app --cov-report=html

# 生成XML覆盖率报告 (用于CI/CD)
pytest --cov=app --cov-report=xml

# 生成终端覆盖率报告
pytest --cov=app --cov-report=term-missing
```

## 🚀 持续集成测试

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:6.0
        ports:
          - 27017:27017
      redis:
        image: redis:7.0
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      env:
        MONGODB_URL: mongodb://localhost:27017
        REDIS_URL: redis://localhost:6379
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: |
        pytest --cov=app --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 🔍 测试调试

### 调试技巧

```python
# 使用 pytest.set_trace() 设置断点
def test_debug_example():
    result = some_function()
    pytest.set_trace()  # 在这里设置断点
    assert result == expected_value

# 使用 -s 参数显示 print 输出
# pytest -s test_file.py

# 使用 -x 参数在第一个失败时停止
# pytest -x test_file.py

# 使用 --pdb 参数在失败时进入调试器
# pytest --pdb test_file.py
```

### 日志配置

```python
# tests/conftest.py
import logging

@pytest.fixture(autouse=True)
def setup_logging():
    """设置测试日志"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

## 📚 相关文档

- [API 接口文档](../api/README.md)
- [后端实现指南](../backend/BACKEND_IMPLEMENTATION_GUIDE.md)
- [业务流程说明](../business/BUSINESS_FLOW.md)
- [前端集成指南](../frontend/FRONTEND_API_INTEGRATION_GUIDE.md)
- [环境配置指南](../setup/README.md)

## 💡 测试最佳实践

### 1. 测试设计原则

- **单一职责**: 每个测试只测试一个功能点
- **独立性**: 测试之间不相互依赖
- **可重复性**: 测试结果应该一致
- **快速执行**: 测试应该快速完成

### 2. 测试数据管理

- **使用 Fixtures**: 复用测试数据
- **数据隔离**: 测试数据不相互影响
- **自动清理**: 测试结束后自动清理数据
- **真实数据**: 使用接近真实场景的测试数据

### 3. 测试维护

- **命名规范**: 清晰的测试函数命名
- **文档注释**: 详细的测试说明
- **定期重构**: 定期重构测试代码
- **版本控制**: 测试代码纳入版本控制

## 🚨 常见问题

### 1. 异步测试问题

```python
# 使用 @pytest.mark.asyncio 装饰器
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected_value
```

### 2. 数据库连接问题

```python
# 确保测试数据库配置正确
# 使用测试专用的数据库
# 测试结束后清理数据
```

### 3. 缓存问题

```python
# 测试前清理缓存
# 使用测试专用的缓存实例
# 避免缓存影响测试结果
```

## 📞 支持

如有测试相关问题，请：
1. 查看测试日志和错误信息
2. 检查测试环境配置
3. 验证测试数据准备
4. 联系测试团队
