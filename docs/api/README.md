# API 接口文档

## 📋 概述

本目录包含 Realm of Balance App 后端的所有 API 接口文档和规范。

## 📁 目录结构

```
api/
├── README.md                    # 本文件 - API 文档说明
└── [待添加]                     # 具体的 API 接口文档
```

## 🚀 快速开始

### API 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Token (Bearer)
- **数据格式**: JSON
- **字符编码**: UTF-8

### 接口分类

1. **用户管理** (`/user/*`)
   - 用户注册、登录、信息管理
   - 设备识别和状态跟踪

2. **算命分析** (`/blueprint/*`)
   - 个人蓝图生成
   - 八字排盘和五行分析
   - 内在特质和生命曲线

3. **Heart Compass** (`/heart-compass/*`)
   - 易经指导系统
   - 情境匹配和决策建议
   - 指导历史管理

4. **每日运势** (`/daily-fortune/*`)
   - 个性化运势生成
   - 时段建议和幸运元素
   - 运势历史查询

5. **管理员功能** (`/admin/*`)
   - 系统监控和管理
   - 用户数据管理
   - 系统配置

## 🔐 认证和授权

### JWT Token 获取

```bash
# 用户登录后获取 token
POST /api/v1/user/create
```

### 使用 Token

```bash
# 在请求头中添加
Authorization: Bearer <your_jwt_token>
```

## 📊 响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 具体数据
  },
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

## 🧪 测试接口

### 健康检查

```bash
GET /health
```

### API 文档

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## 📝 接口规范

### 请求规范

- 使用 `snake_case` 命名
- 所有时间字段使用 ISO 8601 格式
- 文件上传使用 `multipart/form-data`

### 响应规范

- HTTP 状态码遵循 RESTful 规范
- 错误码统一管理
- 分页数据包含总数和分页信息

## 🔄 版本控制

- 当前版本: `v1`
- 版本号在 URL 中体现: `/api/v1/`
- 向后兼容性保证

## 📚 相关文档

- [后端实现指南](../backend/BACKEND_IMPLEMENTATION_GUIDE.md)
- [业务流程说明](../business/BUSINESS_FLOW.md)
- [前端集成指南](../frontend/FRONTEND_API_INTEGRATION_GUIDE.md)
- [测试指南](../testing/TESTING_GUIDE.md)

## 🚨 注意事项

1. **API 限流**: 部分接口有调用频率限制
2. **数据验证**: 所有输入都会进行严格验证
3. **错误处理**: 完善的错误处理和用户友好的错误信息
4. **日志记录**: 所有 API 调用都会被记录到日志中

## 💡 最佳实践

1. 始终检查响应状态码
2. 实现适当的重试机制
3. 缓存不经常变化的数据
4. 使用适当的超时设置
5. 实现错误处理和用户反馈

## 📞 支持

如有 API 相关问题，请：
1. 查看错误日志
2. 检查请求参数格式
3. 验证认证信息
4. 联系开发团队
