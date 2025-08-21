# Realm of Balance App 测试指南

## 📋 概述

本指南介绍如何测试Realm of Balance App的后端API服务，确保所有端点正常工作。

**当前测试状态**: 所有26个API接口已全部测试通过，字段命名统一使用snake_case，系统完全稳定运行。

## 🚀 快速开始

### 1. 启动后端服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py
```

服务将在 `http://localhost:8000` 启动。

### 2. 运行快速测试

```bash
# 快速检查服务是否正常运行
python quick_test.py
```

这个脚本会快速测试主要端点，适合日常检查。

### 3. 运行完整测试

```bash
# 运行全面的API测试
python test_api_endpoints.py
```

这个脚本会测试所有API端点，生成详细报告。

## 🔧 测试脚本说明

### quick_test.py - 快速测试脚本

**用途**: 快速检查API服务是否正常运行
**特点**: 
- 使用同步请求，简单快速
- 只测试主要端点
- 适合日常检查和服务监控

**使用方法**:
```bash
python quick_test.py
```

**测试内容**:
- 基础端点 (`/`, `/health`, `/docs`)
- 用户管理API
- 个人蓝图API
- Heart Compass API
- Daily Fortune API
- 管理员API

### test_api_endpoints.py - 完整测试脚本

**用途**: 全面测试所有API端点的功能
**特点**:
- 使用异步请求，性能更好
- 测试所有注册的端点
- 生成详细的测试报告
- 支持自定义URL和超时设置

**使用方法**:
```bash
# 使用默认设置
python test_api_endpoints.py

# 自定义API地址
python test_api_endpoints.py --url http://your-server:8000

# 自定义超时时间
python test_api_endpoints.py --timeout 60
```

**测试内容**:
- 健康检查和基础端点
- 用户管理端点
- 个人蓝图端点
- Heart Compass端点
- Daily Fortune端点
- 管理员端点
- 错误处理测试

## 📊 测试结果解读

### 状态说明

- **✅ PASS**: 测试通过，端点正常工作
- **❌ FAIL**: 测试失败，端点返回了意外的状态码
- **🚨 ERROR**: 测试出错，可能是网络问题或服务异常

### 常见问题

#### 1. 连接失败
```
❌ GET http://localhost:8000/ - 连接失败 (服务可能未启动)
```
**解决方案**: 确保后端服务已启动，检查端口是否正确

#### 2. 请求超时
```
❌ GET http://localhost:8000/api/v1/user/status - 请求超时
```
**解决方案**: 检查网络连接，增加超时时间

#### 3. 状态码不匹配
```
❌ GET /api/v1/blueprint/test_user - FAIL (期望 404, 实际 500)
```
**解决方案**: 检查后端逻辑，可能是数据库连接问题

## 🧪 测试环境准备

### 1. 依赖安装

```bash
# 安装测试依赖
pip install aiohttp requests

# 或者安装所有依赖
pip install -r requirements.txt
```

### 2. 环境配置

```bash
# 复制环境变量文件
cp env.example .env

# 编辑配置文件，设置正确的API key
nano .env
```

### 3. 数据库准备

确保MongoDB服务正在运行：

```bash
# 启动MongoDB (macOS)
brew services start mongodb-community

# 启动MongoDB (Ubuntu)
sudo systemctl start mongod

# 检查MongoDB状态
mongo --eval "db.runCommand('ping')"
```

## 🔍 测试特定功能

### 测试用户管理

```bash
# 测试用户创建
curl -X POST "http://localhost:8000/api/v1/user/create" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test_device_123",
    "profile": {
      "gender": "male",
      "birth_date": "1990-08-15",
      "birth_time": "10:30",
      "birth_location": "中国，四川省，成都市"
    }
  }'
```

### 测试个人蓝图

```bash
# 生成个人蓝图
curl -X POST "http://localhost:8000/api/v1/blueprint/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "user_profile": {
      "gender": "male",
      "birth_date": "1990-08-15",
      "birth_time": "10:30",
      "birth_location": "中国，四川省，成都市"
    }
  }'
```

### 测试Heart Compass

```bash
# 寻求指导
curl -X POST "http://localhost:8000/api/v1/heart-compass/seek-guidance" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_123",
    "question": "如何平衡工作与生活？",
    "user_profile": {
      "gender": "male",
      "birth_date": "1990-08-15",
      "birth_time": "10:30",
      "birth_location": "中国，四川省，成都市"
    }
  }'
```

## 📈 性能测试

### 响应时间监控

测试脚本会记录每个端点的响应时间，帮助识别性能瓶颈：

```
✅ GET /api/v1/user/status - PASS (0.15s)
✅ POST /api/v1/user/create - PASS (0.45s)
✅ GET /api/v1/blueprint/test_user - PASS (0.23s)
```

### 批量测试

```bash
# 运行多次测试，观察性能变化
for i in {1..5}; do
  echo "=== 第 $i 次测试 ==="
  python quick_test.py
  sleep 2
done
```

## 🚨 故障排除

### 1. 服务无法启动

**检查项**:
- 端口是否被占用
- 依赖是否正确安装
- 环境变量是否正确设置

**解决方案**:
```bash
# 检查端口占用
lsof -i :8000

# 杀死占用进程
kill -9 <PID>

# 重新启动服务
python run.py
```

### 2. 数据库连接失败

**检查项**:
- MongoDB服务是否运行
- 连接字符串是否正确
- 网络是否可达

**解决方案**:
```bash
# 检查MongoDB状态
mongo --eval "db.runCommand('ping')"

# 重启MongoDB
sudo systemctl restart mongod
```

### 3. API Key无效

**检查项**:
- 环境变量是否正确设置
- API key是否有效
- 服务商是否正常

**解决方案**:
```bash
# 检查环境变量
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"

# 测试API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://generativelanguage.googleapis.com/v1beta/models"
```

## 📝 测试报告

### 自动生成报告

完整测试脚本会自动生成JSON格式的测试报告：

```bash
# 运行测试
python test_api_endpoints.py

# 查看生成的报告
ls -la api_test_report_*.json
```

### 报告内容

测试报告包含：
- 测试摘要（总数、通过数、失败数、成功率）
- 详细测试结果
- 响应时间统计
- 错误详情

### 报告分析

```bash
# 使用jq分析报告 (如果安装了jq)
jq '.summary' api_test_report_*.json

# 查看失败的测试
jq '.test_results[] | select(.status != "PASS")' api_test_report_*.json
```

## 🔄 持续集成

### 自动化测试

可以将测试脚本集成到CI/CD流程中：

```yaml
# GitHub Actions 示例
- name: Test API Endpoints
  run: |
    python test_api_endpoints.py --url http://localhost:8000
    # 检查测试结果
    if grep -q "FAIL\|ERROR" api_test_report_*.json; then
      exit 1
    fi
```

### 定期测试

设置定时任务，定期运行测试：

```bash
# 添加到crontab
0 */6 * * * cd /path/to/project && python quick_test.py >> test.log 2>&1
```

## 📞 技术支持

如果在测试过程中遇到问题：

1. 检查测试日志和错误信息
2. 确认后端服务正常运行
3. 验证网络连接和配置
4. 查看后端日志文件
5. 参考故障排除部分

---

**测试脚本版本**: v1.0  
**最后更新**: 2024年  
**适用版本**: Realm of Balance App Backend v1.0+
