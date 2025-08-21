# Realm of Balance App 完整业务流程

## 📋 目录
1. [系统架构概览](#系统架构概览)
2. [用户生命周期流程](#用户生命周期流程)
3. [新用户完整流程](#新用户完整流程)
4. [老用户使用流程](#老用户使用流程)
5. [核心功能流程](#核心功能流程)
6. [数据流转图](#数据流转图)
7. [API接口调用链](#api接口调用链)
8. [错误处理流程](#错误处理流程)
9. [缓存策略流程](#缓存策略流程)

---

## 🏗️ 系统架构概览

### 技术架构
```
前端 React App
    ↓
后端 FastAPI Server
    ↓
├── 用户管理模块 (UserService)
├── 算命分析模块 (BlueprintService + AIService)
├── Heart Compass 模块 (HeartCompassService + AIService)
├── 每日运势模块 (DailyFortuneService + AIService)
├── 数据存储层 (MongoDB + 版本化缓存系统)
└── AI服务层 (Gemini API + 提示词管理)
```

### 核心组件
- **API层**: FastAPI 路由和请求处理
- **服务层**: 业务逻辑和AI集成
- **数据层**: MongoDB存储 + 版本化缓存系统
- **AI层**: Gemini API (支持8192 tokens) + 提示词管理
- **缓存层**: 版本化缓存系统 (零脏数据风险)

### 核心组件
- **API层**: FastAPI 路由和请求处理
- **服务层**: 业务逻辑和AI集成
- **数据层**: MongoDB存储 + 版本化缓存系统
- **AI层**: Gemini API (支持8192 tokens) + 提示词管理
- **缓存层**: 版本化缓存系统 (零脏数据风险)

---

## 👤 用户生命周期流程

### 用户状态定义
```python
用户状态枚举:
├── NEW_USER (新用户)
│   ├── 首次访问
│   ├── 信息收集中
│   └── 算命结果生成中
├── ACTIVE_USER (活跃用户)
│   ├── 有算命结果
│   ├── 可访问所有功能
│   └── 数据完整
└── INACTIVE_USER (非活跃用户)
    ├── 长期未登录
    └── 数据可能过期
```

### 用户状态转换
```
新用户 → 信息收集 → 算命分析 → 活跃用户
    ↓
老用户 → 直接进入 → 功能使用
    ↓
所有用户 → 定期使用 → 数据更新
```

---

## 🆕 新用户完整流程

### 第一阶段：用户识别与状态检查

#### 1.1 前端启动
```
用户打开应用
    ↓
前端生成/获取设备ID
    ↓
调用用户状态检查接口
```

#### 1.2 用户状态检查
**接口**: `GET /api/v1/user/status`
**请求头**: `Device-ID: {device_unique_id}`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "is_new_user": true,
    "user_profile": null,
    "has_blueprint": false
  }
}
```

**业务逻辑**:
```python
UserService.check_user_status(device_id)
    ↓
Database.find_one("users", {"device_id": device_id})
    ↓
返回用户状态信息
```

### 第二阶段：用户信息收集

#### 2.1 前端表单收集
```
用户填写个人信息:
├── 性别 (male/female/other)
├── 出生日期 (YYYY-MM-DD)
├── 出生时间 (HH:MM)
└── 出生地点 (城市名称)
```

#### 2.2 创建用户
**接口**: `POST /api/v1/user/create`
**请求体**:
```json
{
  "device_id": "device_unique_id",
  "gender": "male",
  "birth_date": "1990-08-15",
  "birth_time": "10:30",
  "birth_location": "中国，四川省，成都市"
}
```

**业务逻辑**:
```python
UserService.create_user(user_create)
    ↓
验证用户信息
    ↓
Database.insert_one("users", user_data)
    ↓
返回用户ID和基本信息
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_unique_id",
    "device_id": "device_unique_id",
    "gender": "male",
    "birth_date": "1990-08-15",
    "birth_time": "10:30",
    "birth_location": "中国，四川省，成都市",
    "is_new_user": true,
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### 第三阶段：算命结果生成

#### 3.1 调用算命分析
**接口**: `POST /api/v1/blueprint/generate`
**请求体**:
```json
{
  "user_id": "user_unique_id",
  "user_profile": {
    "gender": "male",
    "birth_date": "1990-08-15",
    "birth_time": "10:30",
    "birth_location": "中国，四川省，成都市"
  }
}
```

#### 3.2 AI算命分析流程
```python
BlueprintService.generate_blueprint(user_id, user_profile)
    ↓
AIService.generate_blueprint(user_profile)
    ↓
PromptManager.get_complete_prompt("blueprint", user_profile)
    ↓
GeminiInteractionAPI.send_message_to_ai(prompt, context)
    ↓
解析AI响应，构建结构化数据
    ↓
Database.insert_one("blueprint_results", blueprint_data)
    ↓
返回完整的算命结果
```

#### 3.3 算命结果结构
```json
{
  "success": true,
  "data": {
    "user_id": "user_unique_id",
    "bazi": {
      "year_pillar": {"heavenly_stem": "庚", "earthly_branch": "午"},
      "month_pillar": {"heavenly_stem": "己", "earthly_branch": "未"},
      "day_pillar": {"heavenly_stem": "甲", "earthly_branch": "子"},
      "hour_pillar": {"heavenly_stem": "乙", "earthly_branch": "丑"}
    },
    "elemental_profile": {
      "metal": {"strength": 25, "characteristics": ["精确", "逻辑"]},
      "wood": {"strength": 15, "characteristics": ["生长", "创造"]},
      "water": {"strength": 30, "characteristics": ["智慧", "适应"]},
      "fire": {"strength": 20, "characteristics": ["热情", "领导"]},
      "earth": {"strength": 10, "characteristics": ["稳定", "承载"]}
    },
    "core_analysis": {
      "dominant_element": "water",
      "weakest_element": "earth",
      "personality_traits": ["深刻的同理心", "灵活的适应力", "卓越的沟通力"],
      "life_guidance": "你的人生指导内容"
    },
    "inner_blueprint": {
      "core_energy_field": {...},
      "core_essence": {...},
      "natural_strengths": {...},
      "growth_areas": {...},
      "life_journey_curve": {...}
    }
  }
}
```

### 第四阶段：进入主界面
```
算命结果生成完成
    ↓
前端状态更新 (is_new_user: false, has_blueprint: true)
    ↓
显示主界面，解锁所有功能
    ↓
用户可以开始使用 Heart Compass 和每日运势
```

---

## 🔄 老用户使用流程

### 第一阶段：快速识别
```
用户打开应用
    ↓
前端发送设备ID
    ↓
GET /api/v1/user/status
    ↓
返回用户信息和算命结果状态
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "is_new_user": false,
    "user_profile": {
      "user_id": "existing_user_id",
      "gender": "male",
      "birth_date": "1990-08-15",
      "birth_time": "10:30",
      "birth_location": "中国，四川省，成都市"
    },
    "has_blueprint": true
  }
}
```

### 第二阶段：数据加载
```
检查算命结果缓存
    ↓
GET /api/v1/blueprint/{user_id}
    ↓
返回完整的算命结果
    ↓
前端渲染个人蓝图页面
```

### 第三阶段：功能使用
老用户可以立即使用所有功能，无需等待数据生成。

---

## 🎯 核心功能流程

### 1. Heart Compass 指导系统

#### 1.1 寻求指导
**接口**: `POST /api/v1/heart-compass/seek-guidance`
**请求体**:
```json
{
  "user_id": "user_unique_id",
  "question": "我在工作中遇到了瓶颈，不知道该如何突破...",
  "user_profile": {
    "gender": "male",
    "birth_date": "1990-08-15",
    "birth_time": "10:30",
    "birth_location": "中国，四川省，成都市"
  }
}
```

#### 1.2 AI指导生成流程
```python
HeartCompassService.seek_guidance(user_id, question, user_profile)
    ↓
AIService.seek_heart_compass_guidance(question, user_profile)
    ↓
PromptManager.get_complete_prompt("heart_compass", context)
    ↓
GeminiInteractionAPI.send_message_to_ai(prompt, context)
    ↓
解析AI响应，构建结构化指导
    ↓
Database.insert_one("heart_compass_records", guidance_data)
    ↓
返回完整的指导内容
```

#### 1.3 指导结果结构
```json
{
  "success": true,
  "data": {
    "user_id": "user_unique_id",
    "question": "我在工作中遇到了瓶颈...",
    "hexagram": {
      "code": "35",
      "name": "晋卦",
      "title": "晋卦 - 旭日初升",
      "hexagram_text": "晋：康侯用锡马蕃庶，昼日三接。",
      "image_text": "明出地上，晋；君子以自昭明德。",
      "focus_yao": {
        "yao_number": 2,
        "yao_text": "六二：晋如，愁如，贞吉。受兹介福，于其王母。"
      }
    },
    "dialogue_flow": {
      "revelation": "旭日初升，光芒渐显，前进的时刻已然到来。",
      "analysis": "此刻的你，内在的光明与才华正如同破晓的太阳...",
      "guidance": "这是一个应当主动展示自我、顺势而为的时刻...",
      "encouragement": "相信你的太阳，它将照亮你前行的道路。"
    },
    "decision_protocol": {
      "title": "决策协议 | Decision Protocol",
      "situation_code": "晋卦 (#35)",
      "core_strategy": "蓄力待发，顺势而进",
      "action_guide": [
        "专注于展现你的核心能力与成果",
        "主动寻求能够赏识你的良师或合作伙伴",
        "保持内心的光明，让自信自然流露"
      ]
    }
  }
}
```

#### 1.4 指导历史管理
**获取历史**: `GET /api/v1/heart-compass/{user_id}/history?page=1&limit=10`
**查看详情**: `GET /api/v1/heart-compass/guidance/{guidance_id}`
**删除记录**: `DELETE /api/v1/heart-compass/guidance/{guidance_id}?user_id={user_id}`

### 2. 每日运势系统

#### 2.1 获取今日运势
**接口**: `GET /api/v1/daily-fortune/{user_id}/today`

**业务逻辑**:
```python
DailyFortuneService.get_today_fortune(user_id, user_profile)
    ↓
检查今日运势是否存在
    ↓
如果不存在，调用AI生成
    ↓
返回运势结果
```

#### 2.2 运势生成流程
```python
DailyFortuneService.generate_daily_fortune(user_id, user_profile, date)
    ↓
AIService.generate_daily_fortune(user_profile, date)
    ↓
PromptManager.get_complete_prompt("daily_fortune", context)
    ↓
GeminiInteractionAPI.send_message_to_ai(prompt, context)
    ↓
解析AI响应，构建结构化运势
    ↓
Database.insert_one("daily_fortune_records", fortune_data)
    ↓
返回完整的运势内容
```

#### 2.3 运势结果结构
```json
{
  "success": true,
  "data": {
    "user_id": "user_unique_id",
    "date": "2024-01-01T00:00:00Z",
    "hexagram": {
      "name": "乾卦",
      "title": "乾卦 - 天行健",
      "energy": "充满活力与创造力的能量",
      "luck": 85
    },
    "time_advice": [
      {
        "period": "早晨",
        "activity": "晨练或冥想",
        "description": "早晨是能量最充沛的时段...",
        "energy": "高涨"
      }
    ],
    "lucky_elements": {
      "color": "金色",
      "direction": "东方",
      "number": 8
    },
    "personal_advice": "今天你的能量状态很好..."
  }
}
```

#### 2.4 运势管理功能
**生成运势**: `POST /api/v1/daily-fortune/generate`
**历史记录**: `GET /api/v1/daily-fortune/{user_id}/history`
**指定日期**: `GET /api/v1/daily-fortune/{user_id}/date/{date}`
**删除运势**: `DELETE /api/v1/daily-fortune/{user_id}/date/{date}`

### 3. 算命结果管理

#### 3.1 查看算命结果
**接口**: `GET /api/v1/blueprint/{user_id}`

#### 3.2 重新生成算命结果
**接口**: `POST /api/v1/blueprint/{user_id}/regenerate`
**注意**: 此操作会删除旧的算命结果并重新生成

#### 3.3 删除算命结果
**接口**: `DELETE /api/v1/blueprint/{user_id}`

---

## 🔄 数据流转图

### 用户数据流
```
前端请求 → API路由 → 业务服务 → 数据服务 → 数据库
    ↓
数据库 → 数据服务 → 业务服务 → API路由 → 前端响应
```

### AI服务数据流
```
业务服务 → AI服务 → 提示词管理 → Gemini API
    ↓
Gemini API → AI服务 → 响应解析 → 业务服务
    ↓
业务服务 → 数据存储 → 缓存更新
```

### 缓存数据流
```
业务服务 → 版本化缓存 → Redis/内存缓存
    ↓
缓存命中 → 直接返回
    ↓
缓存未命中 → 数据库查询 → 缓存更新 → 返回结果
```

---

## 🌐 API接口调用链

### 完整的API调用序列

#### 新用户完整流程
```
1. GET /api/v1/user/status (检查用户状态)
2. POST /api/v1/user/create (创建用户)
3. POST /api/v1/blueprint/generate (生成算命结果)
4. GET /api/v1/blueprint/{user_id} (获取算命结果)
```

#### 老用户使用流程
```
1. GET /api/v1/user/status (检查用户状态)
2. GET /api/v1/blueprint/{user_id} (获取算命结果)
3. POST /api/v1/heart-compass/seek-guidance (获取指导)
4. GET /api/v1/daily-fortune/{user_id}/today (获取今日运势)
```

#### 功能使用流程
```
Heart Compass:
├── POST /api/v1/heart-compass/seek-guidance (寻求指导)
├── GET /api/v1/heart-compass/{user_id}/history (查看历史)
└── DELETE /api/v1/heart-compass/guidance/{guidance_id} (删除记录)

每日运势:
├── GET /api/v1/daily-fortune/{user_id}/today (今日运势)
├── POST /api/v1/daily-fortune/generate (生成运势)
└── GET /api/v1/daily-fortune/{user_id}/history (运势历史)

算命管理:
├── GET /api/v1/blueprint/{user_id} (查看结果)
├── POST /api/v1/blueprint/{user_id}/regenerate (重新生成)
└── DELETE /api/v1/blueprint/{user_id} (删除结果)
```

---

## ⚠️ 错误处理流程

### 错误分类
```python
错误类型枚举:
├── USER_ERRORS (1000-1999)
│   ├── USER_NOT_FOUND (1001)
│   ├── INVALID_BIRTH_INFO (1002)
│   └── USER_ALREADY_EXISTS (1003)
├── AI_ERRORS (2000-2999)
│   ├── AI_SERVICE_UNAVAILABLE (2001)
│   ├── AI_RESPONSE_INVALID (2002)
│   └── AI_TIMEOUT (2003)
├── DATABASE_ERRORS (3000-3999)
│   ├── DATABASE_ERROR (3001)
│   └── DATABASE_CONNECTION_FAILED (3002)
└── SYSTEM_ERRORS (5000-5999)
    ├── INTERNAL_SERVER_ERROR (5002)
    └── SERVICE_UNAVAILABLE (5003)
```

### 错误处理流程
```
业务异常 → 业务服务捕获 → 转换为AppException
    ↓
AppException → 全局异常处理器 → 统一错误响应
    ↓
前端接收错误响应 → 用户友好的错误提示
```

### 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": 1001,
    "message": "用户不存在",
    "details": "详细错误信息"
  }
}
```

---

## 🚀 缓存策略流程

### 版本化缓存机制

#### 缓存键设计
```
用户信息: user:profile:{user_id}:v{version}
算命结果: ai:blueprint:{user_id}:v{version}
Heart Compass: ai:heart_compass:{user_id}:v{version}
每日运势: ai:daily_fortune:{user_id}:v{version}
```

#### 缓存更新流程
```
数据更新 → 版本号递增 → 相关缓存失效
    ↓
下次查询 → 检查版本号 → 缓存未命中
    ↓
数据库查询 → 新版本缓存 → 返回结果
```

#### 缓存失效策略
```
用户信息更新 → 失效所有相关缓存
算命结果更新 → 失效算命和运势缓存
指导记录更新 → 失效指导缓存
运势记录更新 → 失效运势缓存
```

---

## 📊 系统监控流程

### 管理接口
```
系统状态: GET /api/v1/admin/system/status
提示词配置: GET /api/v1/admin/prompts
缓存统计: GET /api/v1/admin/cache/stats
详细健康检查: GET /api/v1/admin/health/detailed
清空缓存: POST /api/v1/admin/cache/clear
```

### 监控指标
- API响应时间
- 缓存命中率
- AI服务可用性
- 数据库连接状态
- 错误率统计

---

## 🔧 部署和运维流程

### 环境配置
```
1. 复制 env.example 为 .env
2. 配置 MongoDB 连接信息
3. 配置 Gemini API 密钥
4. 配置 Redis 连接信息（可选）
5. 配置日志级别和路径
```

### 启动流程
```
1. 安装依赖: pip install -r requirements.txt
2. 启动应用: python run.py
3. 访问文档: http://localhost:8000/docs
4. 健康检查: http://localhost:8000/health
```

### 数据备份
```
MongoDB 数据备份
├── 用户信息表 (users)
├── 算命结果表 (blueprint_results)
├── 指导记录表 (heart_compass_records)
└── 运势记录表 (daily_fortune_records)
```

---

## 📝 总结

### 核心业务流程
1. **用户识别** → 设备ID检查，确定新老用户
2. **信息收集** → 新用户填写个人信息
3. **算命分析** → AI生成个人蓝图
4. **功能使用** → Heart Compass、每日运势等
5. **数据管理** → 查看、更新、删除各类数据

### 技术特点
- **异步架构**: 全异步处理，高性能
- **版本化缓存**: 零脏数据风险
- **AI集成**: 智能提示词管理
- **错误处理**: 统一的异常处理机制
- **监控管理**: 完整的系统监控接口

### 扩展性
- 新增提示词类型只需在配置文件中添加
- 新增业务功能遵循相同的架构模式
- 缓存策略可配置和扩展
- API接口支持版本化管理
