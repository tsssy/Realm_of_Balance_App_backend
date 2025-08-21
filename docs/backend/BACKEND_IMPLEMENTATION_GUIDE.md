# Realm of Balance App 后端搭建指导文档

## 项目概述

Realm of Balance App 是一个基于东方玄学理论的个人命运分析应用，主要功能包括：
1. **用户个人信息收集与算命** - 新用户首次使用时的完整算命流程
2. **Heart Compass** - 用户提问获取个性化指导
3. **Daily Fortune** - 基于用户信息和当前时间生成每日运势
4. **Personal Blueprint** - 存储和展示用户的算命结果

## 技术架构

### 后端技术栈
- **框架**: Python + FastAPI
- **数据库**: MongoDB
- **AI集成**: Google Gemini API
- **认证**: JWT Token
- **缓存**: Redis (可选，用于缓存AI响应)

### 系统架构图
```
前端 React App
    ↓
后端 FastAPI Server
    ↓
├── 用户管理模块
├── 算命分析模块 (Gemini AI)
├── 运势生成模块 (Gemini AI)
├── 指导生成模块 (Gemini AI)
└── MongoDB 数据存储模块
```

## 数据库设计

### 1. 数据库连接管理
```python
class Database:
    """MongoDB 数据库连接管理类"""
    
    client: AsyncIOMotorClient = None
    db = None
    
    @classmethod
    async def connect(cls):
        """连接到 MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                username=settings.MONGODB_USERNAME,
                password=settings.MONGODB_PASSWORD,
                authSource=settings.MONGODB_AUTH_SOURCE,
                serverSelectionTimeoutMS=5000,
            )
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close(cls):
        """关闭 MongoDB 连接"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")
    
    @classmethod
    async def insert_one(cls, collection_name: str, document: dict):
        """插入单个文档"""
        try:
            result = await cls.get_collection(collection_name).insert_one(document)
            logger.info(f"Inserted document with id: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise
    
    @classmethod
    async def find_one(cls, collection_name: str, filter_dict: dict):
        """查找单个文档"""
        try:
            document = await cls.get_collection(collection_name).find_one(filter_dict)
            return document
        except Exception as e:
            logger.error(f"Error finding document: {e}")
            raise
    
    @classmethod
    async def find(cls, collection_name: str, filter_dict: dict, sort=None, limit=None):
        """查找多个文档"""
        try:
            cursor = cls.get_collection(collection_name).find(filter_dict)
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
            documents = await cursor.to_list(length=None)
            return documents
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            raise
```

### 2. 数据表设计

#### 2.1 用户表 (users) - 统一字段命名规范
```python
{
  "_id": ObjectId,
  "user_id": str,           # 唯一用户标识 (snake_case for DB)
  "device_id": str,         # 设备ID，用于老用户识别 (snake_case for DB)
  "gender": str,            # 性别: 'male', 'female', 'other'
  "birth_date": str,        # 出生日期 "YYYY-MM-DD" (snake_case for DB)
  "birth_time": str,        # 出生时间 "HH:MM" (snake_case for DB)
  "birth_location": str,    # 出生地点 (snake_case for DB)
  "is_new_user": bool,      # 是否为新用户 (snake_case for DB)
  "created_at": datetime,   # 创建时间 (snake_case for DB)
  "updated_at": datetime,   # 更新时间 (snake_case for DB)
  "last_login_at": datetime # 最后登录时间 (snake_case for DB)
}
```

**注意**: 数据库字段和API响应现在都统一使用下划线命名(snake_case)，确保字段命名的完全一致性。

#### 2.2 算命结果表 (blueprint_results)
```python
{
  "_id": ObjectId,
  "user_id": str,           # 关联用户ID (snake_case)
  
  # 八字排盘基础数据
  "bazi": {
    "year_pillar": {"heavenly_stem": str, "earthly_branch": str},    # 年柱
    "month_pillar": {"heavenly_stem": str, "earthly_branch": str},   # 月柱
    "day_pillar": {"heavenly_stem": str, "earthly_branch": str},     # 日柱
    "hour_pillar": {"heavenly_stem": str, "earthly_branch": str}     # 时柱
  },
  
  # 五行分析结果
  "elemental_profile": {
    "metal": {"strength": int, "characteristics": [str]},      # 金
    "wood": {"strength": int, "characteristics": [str]},       # 木
    "water": {"strength": int, "characteristics": [str]},      # 水
    "fire": {"strength": int, "characteristics": [str]},       # 火
    "earth": {"strength": int, "characteristics": [str]}       # 土
  },
  
  # 核心分析结果
  "core_analysis": {
    "dominant_element": str,           # 主导元素
    "weakest_element": str,            # 最弱元素
    "personality_traits": [str],       # 性格特征
    "life_guidance": str,              # 人生指导
    "compatibility": {                 # 兼容性分析
      "best_elements": [str],
      "challenging_elements": [str]
    }
  },
  
  # 内在蓝图报告
  "inner_blueprint": {
    "core_energy_field": {             # 核心能量场
      "title": str,
      "description": str,
      "chart_data": [{
        "axis": str,                   # 如 "金 | Metal"
        "value": int                   # 0-100 的数值
      }]
    },
    "core_essence": {                  # 核心本质
      "title": str,
      "description": str               # 主导元素的性格解读
    },
    "natural_strengths": {             # 天生优势
      "title": str,
      "strengths": [str]               # 三个核心优点
    },
    "growth_areas": {                  # 成长挑战
      "analysis": str,                 # 能量失衡分析
      "balance_path": {                # 平衡之道
        "title": str,
        "suggestions": [str]           # 三条具体建议
      }
    },
    "life_journey_curve": {            # 生命曲线
      "title": str,
      "description": str,
      "chart_data": [{
        "year": int,                   # 年份
        "energy_level": int,           # 能量值 0-100
        "is_turning_point": bool,      # 是否为转折点
        "icon_id": str,                # 图标标识
        "event_description": str       # 年度描述
      }]
    }
  },
  
  # 原始AI分析内容
  "ai_analysis": str,                  # Gemini AI 生成的详细分析
  "created_at": datetime,              # 创建时间
  "updated_at": datetime               # 更新时间
}
```

#### 2.3 每日运势表 (daily_fortune_records)
```python
{
  "_id": ObjectId,
  "user_id": str,           # 关联用户ID (snake_case)
  "date": datetime,         # 运势日期
  "hexagram": {             # 当日卦象
    "name": str,            # 卦名
    "pinyin": str,          # 拼音
    "english_name": str,    # 英文含义
    "title": str,           # 完整标题
    "energy": str,          # 能量描述
    "luck": int,            # 幸运指数 (0-100)
    "hexagram_text": str,   # 卦辞
    "image_text": str       # 象辞
  },
  "time_advice": [{         # 时段建议
    "period": str,          # 时间段
    "start_time": str,      # 开始时间
    "end_time": str,        # 结束时间
    "activity": str,        # 建议活动
    "description": str,     # 详细描述
    "energy": str,          # 能量状态
    "priority": str         # 优先级
  }],
  "lucky_elements": {       # 幸运元素
    "color": str,           # 幸运颜色
    "direction": str,       # 幸运方向
    "number": int,          # 幸运数字
    "element": str,         # 幸运元素
    "gemstone": str         # 幸运宝石
  },
  "personal_advice": str,   # 个性化建议
  "ai_generated": str,      # Gemini AI 生成的运势内容
  "created_at": datetime    # 创建时间
}
```

#### 2.4 Heart Compass 指导记录表 (heart_compass_records)
```python
{
  "_id": ObjectId,
  "user_id": str,           # 关联用户ID (snake_case)
  "question": str,          # 用户问题/困惑文本
  "hexagram": {             # 对应的卦象信息
    "code": str,            # 卦序 (如 "1")
    "name": str,            # 卦名 (如 "乾卦")
    "english_name": str,    # 英文名 (如 "The Creative, Heaven")
    "title": str,           # 卦题 (如 "乾卦 - The Creative, Heaven")
    "hexagram_text": str,   # 卦辞
    "image_text": str,      # 象辞
    "focus_yao": {          # 焦点爻辞
      "yao_number": int,    # 爻位 (1-6)
      "yao_text": str       # 爻辞内容
    }
  },
  "dialogue_flow": {        # 对话流 (四个环节)
    "revelation": str,      # 启示 - 短诗或箴言
    "analysis": str,        # 分析 - 基于象辞的处境分析
    "guidance": str,        # 指引 - 行动方向或心态建议
    "encouragement": str    # 鼓励 - 温暖治愈的话语
  },
  "deep_wisdom": {          # 深层智慧
    "title": str,           # 标题
    "explanation": str,     # 详细解释
    "philosophical_meaning": str, # 哲学含义
    "personal_interpretation": str # 个人解读
  },
  "action_guide": {         # 行动指南
    "title": str,           # 标题
    "main_actions": [str],  # 主要行动
    "supporting_actions": [str], # 支持行动
    "inspirational_message": str # 激励话语
  },
  "decision_protocol": {    # 决策协议
    "title": str,           # 标题
    "situation_code": str,  # 情境代码
    "core_strategy": str,   # 核心策略
    "action_guide": [str]   # 行动指南
  },
  "ai_generated": str,      # Gemini AI 生成的完整指导
  "created_at": datetime,   # 创建时间
  "updated_at": datetime    # 更新时间
}
```

## 数据结构统一设计

### 1. 统一响应格式

#### 1.1 基础响应模型
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    """统一的API响应基础模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: Optional[str] = Field(None, description="响应消息，用于错误或提示")

class ListResponse(BaseModel, Generic[T]):
    """统一的列表响应基础模型，包含分页信息"""
    success: bool = Field(..., description="请求是否成功")
    data: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page: Optional[int] = Field(None, description="当前页码")
    page_size: Optional[int] = Field(None, description="每页记录数")
    message: Optional[str] = Field(None, description="响应消息，用于错误或提示")
```

#### 1.2 数据库模型基类
```python
class BaseDBModel(BaseModel):
    """数据库实体基础模型，包含通用字段"""
    id: Optional[str] = Field(None, alias="_id", description="MongoDB文档ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        from_attributes = True
        populate_by_name = True
        # 允许额外字段，便于数据库兼容
        extra = "allow"
        # 允许别名
        allow_population_by_field_name = True
```

#### 1.3 共享子模型
```python
class UserProfileBase(BaseModel):
    """用户基本信息的基础模型，用于请求和响应中的嵌套"""
    gender: str = Field(..., description="性别 (male/female/other)")
    birth_date: str = Field(..., description="出生日期，格式：YYYY-MM-DD")
    birth_time: str = Field(..., description="出生时间，格式：HH:MM")
    birth_location: str = Field(..., description="出生地点")

class Hexagram(BaseModel):
    """卦象基础模型，用于Heart Compass和Daily Fortune的共同部分"""
    name: str = Field(..., description="卦名")
    english_name: str = Field(..., description="英文含义")
    title: str = Field(..., description="完整标题")
    hexagram_text: str = Field(..., description="卦辞")
    image_text: str = Field(..., description="象辞")
```

### 2. 字段命名规范

#### 2.1 统一snake_case命名 (重要更新)
- **数据库字段**: 统一使用下划线命名法：`user_id`, `device_id`, `birth_date`, `birth_time`, `birth_location`, `is_new_user`, `created_at`, `updated_at`, `last_login_at`
- **API响应字段**: 统一使用下划线命名法：`user_id`, `device_id`, `birth_date`, `birth_time`, `birth_location`, `is_new_user`, `created_at`, `updated_at`, `last_login_at`
- **模型字段**: 统一使用下划线命名法：`user_id`, `device_id`, `birth_date`, `birth_time`, `birth_location`, `is_new_user`, `created_at`, `updated_at`, `last_login_at`

#### 2.2 字段命名一致性保证
- **零脏数据风险**: 通过统一命名规范确保数据库、模型、API响应完全一致
- **无需映射转换**: 取消了之前的camelCase到snake_case的映射转换
- **简化维护**: 减少了字段名不一致导致的潜在问题

### 3. 模型继承体系

#### 3.1 用户相关模型
```python
# 数据库模型 - 使用snake_case匹配MongoDB
class UserInDB(BaseDBModel):
    user_id: str = Field(..., description="用户ID")
    device_id: str = Field(..., description="设备ID")
    gender: Gender = Field(..., description="性别")
    birth_date: str = Field(..., description="出生日期")
    birth_time: str = Field(..., description="出生时间")
    birth_location: str = Field(..., description="出生地点")
    is_new_user: bool = Field(True, description="是否为新用户")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")

# API响应模型 - 使用snake_case
class UserResponse(BaseModel):
    user_id: str = Field(..., description="用户ID")
    device_id: str = Field(..., description="设备ID")
    gender: str = Field(..., description="性别")
    birth_date: str = Field(..., description="出生日期")
    birth_time: str = Field(..., description="出生时间")
    birth_location: str = Field(..., description="出生地点")
    is_new_user: bool = Field(..., description="是否为新用户")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")

# 统一响应格式
class UserStatusResponse(BaseResponse[UserStatusData]):
    pass
```

#### 3.2 其他模型继承
- `BlueprintResult` → `BaseDBModel`
- `HeartCompassRecord` → `BaseDBModel`
- `DailyFortune` → `BaseDBModel`
- 所有API响应 → `BaseResponse[T]` 或 `ListResponse[T]`

## API 接口设计

### 1. 用户管理接口

#### 1.1 检查用户状态
```javascript
GET /api/v1/user/status?device_id=device_unique_id

Response (统一格式):
{
  "success": true,
  "data": {
    "is_new_user": boolean,
    "user_profile": {
      "user_id": "user_unique_id",
      "gender": "male" | "female" | "other",
      "birth_date": "YYYY-MM-DD",
      "birth_time": "HH:MM", 
      "birth_location": "城市名称"
    } | null,
    "has_blueprint": boolean
  },
  "message": null
}
```

#### 1.2 创建新用户
```javascript
POST /api/v1/user/create
Body: {
  "device_id": "device_unique_id",
  "profile": {
  "gender": "male" | "female" | "other",
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM",
    "birth_location": "城市名称"
  }
}

Response (统一格式):
{
  "success": true,
  "data": {
    "user_id": "user_unique_id",
    "device_id": "device_unique_id",
    "gender": "male",
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM",
    "birth_location": "城市名称",
    "is_new_user": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "last_login_at": null
  },
    "message": "用户创建成功"
}
```

#### 1.3 更新用户信息
```javascript
PUT /api/v1/user/{userId}
Body: {
  "profile": {
  "gender": "male" | "female" | "other",
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM",
    "birth_location": "城市名称"
  }
}

Response (统一格式):
{
  "success": true,
  "data": {
    "user_id": "user_unique_id",
    "device_id": "device_unique_id",
    "gender": "male",
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM",
    "birth_location": "城市名称",
    "is_new_user": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "last_login_at": "2024-01-01T11:30:00Z"
  },
    "message": "用户信息更新成功"
}
```

### 2. 算命分析接口

#### 2.1 生成个人蓝图
```javascript
POST /api/blueprint/generate
Body: {
  "userId": "user_unique_id",
  "userProfile": {
    "gender": "male" | "female" | "other",
    "birthDate": "YYYY-MM-DD",
    "birthTime": "HH:MM",
    "birthLocation": "城市名称"
  }
}

Response:
{
  "success": true,
  "data": {
    "blueprintId": "blueprint_unique_id",
    "bazi": {
      "yearPillar": { "heavenlyStem": "庚", "earthlyBranch": "午" },
      "monthPillar": { "heavenlyStem": "己", "earthlyBranch": "未" },
      "dayPillar": { "heavenlyStem": "甲", "earthlyBranch": "子" },
      "hourPillar": { "heavenlyStem": "乙", "earthlyBranch": "丑" }
    },
    "elementalProfile": {
      "metal": { "strength": 25, "characteristics": ["精确", "逻辑"] },
      "wood": { "strength": 15, "characteristics": ["生长", "创造"] },
      "water": { "strength": 30, "characteristics": ["智慧", "适应"] },
      "fire": { "strength": 20, "characteristics": ["热情", "领导"] },
      "earth": { "strength": 10, "characteristics": ["稳定", "承载"] }
    },
    "coreAnalysis": {
      "dominantElement": "water",
      "weakestElement": "earth",
      "personalityTraits": ["深刻的同理心", "灵活的适应力", "卓越的沟通力"],
      "lifeGuidance": "你的人生指导内容",
      "compatibility": {
        "bestElements": ["metal", "wood"],
        "challengingElements": ["earth"]
      }
    },
    "innerBlueprint": {
      "coreEnergyField": {
        "title": "核心能量场 | Elemental Composition",
        "description": "这是构成你内在世界的五种基本能量...",
        "chartData": [
          {"axis": "金 | Metal", "value": 25},
          {"axis": "木 | Wood", "value": 15},
          {"axis": "水 | Water", "value": 30},
          {"axis": "火 | Fire", "value": 20},
          {"axis": "土 | Earth", "value": 10}
        ]
      },
      "coreEssence": {
        "title": "核心本质 | Core Essence",
        "description": "你的核心能量如水，深邃、包容且极具适应性..."
      },
      "naturalStrengths": {
        "title": "天生优势 | Natural Strengths",
        "strengths": ["深刻的同理心", "灵活的适应力", "卓越的沟通力"]
      },
      "growthAreas": {
        "title": "成长挑战 | Growth Areas",
        "analysis": "你的能量构成中，'土'元素稍显不足...",
        "balancePath": {
          "title": "平衡之道 | Path to Balance",
          "suggestions": [
            "每日5分钟接地冥想练习，感受身体与大地的连接",
            "定期与朋友家人沟通，建立稳定的情感支持网络",
            "制定明确的计划和目标，培养决策的果断性"
          ]
        }
      },
      "lifeJourneyCurve": {
        "title": "生命曲线 | Life Journey Forecast",
        "description": "未来数年你的能量将经历自然波动...",
        "chartData": [
          {
            "year": 2025,
            "energyLevel": 55,
            "isTurningPoint": true,
            "iconId": "self_growth",
            "eventDescription": "一个建立内在稳定和清晰规划的年份..."
          }
        ]
      }
    },
    "aiAnalysis": "Gemini AI 生成的完整分析内容"
  }
}
```

#### 2.2 获取个人蓝图
```javascript
GET /api/blueprint/:userId

Response:
{
  "success": true,
  "data": BlueprintResult
}
```

### 3. Heart Compass 接口

#### 3.1 获取指导
```javascript
POST /api/heart-compass/seek-guidance
Body: {
  "userId": "user_unique_id",
  "question": "用户的具体困惑文本",
  "userProfile": UserProfile  // 用于个性化分析
}

Response:
{
  "success": true,
  "data": {
    "hexagram": {
      "code": "1",
      "name": "乾卦",
      "english_name": "The Creative, Heaven",
      "title": "乾卦 - The Creative, Heaven",
      "hexagramText": "乾：元，亨，利，贞。",
      "imageText": "天行健，君子以自强不息。",
      "focusYao": {
        "yaoNumber": 1,
        "yaoText": "初九：潜龙，勿用。"
      }
    },
    "dialogueFlow": {
      "revelation": "天行健，君子以自强不息。",
      "analysis": "此刻的你，内在的创造力和领导力正如同天空般广阔...",
      "guidance": "这是一个应当展现自我、发挥创造力的时刻...",
      "encouragement": "相信你的天赋，它将指引你走向成功。"
    },
    "deepWisdom": {
      "title": "Deep Wisdom",
      "explanation": "The Qián hexagram symbolizes the power of Heaven...",
      "philosophical_meaning": "This is the most powerful hexagram among the 64...",
      "personal_interpretation": "When Qián appears, the universe is telling you..."
    },
    "actionGuide": {
      "title": "Action Guide",
      "main_actions": [
        "Trust in your inner creativity and leadership abilities",
        "Take initiative and become a catalyst for positive change"
      ],
      "supporting_actions": [
        "Maintain strong will while leading with virtue and compassion",
        "Transform your vision into concrete action plans"
      ],
      "inspirational_message": "The energy of Qián flows through you..."
    },
    "decisionProtocol": {
      "title": "决策协议 | Decision Protocol",
      "situationCode": "乾卦 (#1)",
      "coreStrategy": "自强不息，创造无限",
      "actionGuide": [
        "展现你的创造力和领导力",
        "主动承担责任，推动积极变化",
        "保持坚定的意志和美德"
      ]
    },
    "aiGenerated": "Gemini AI 生成的完整指导内容"
  }
}
```

#### 3.2 重新提问
```javascript
POST /api/heart-compass/ask-again
Body: {
  "userId": "user_unique_id",
  "question": "新的问题或深入探讨",
  "previous_guidance_id": "guidance_unique_id"  // 可选，用于上下文关联
}

Response:
{
  "success": true,
  "data": HeartCompassRecord  // 新的指导记录，可能基于之前的分析进行深入
}
```

#### 3.3 获取指导历史
```javascript
GET /api/v1/heart-compass/{userId}/history?page=1&limit=10

Response (统一列表格式):
{
  "success": true,
  "data": [HeartCompassRecord],
      "total": 25,
  "page": 1,
  "page_size": 10,
  "message": null
}
```

### 4. 每日运势接口

#### 4.1 生成今日运势
```javascript
POST /api/daily-fortune/generate
Body: {
  "userId": "user_unique_id",
  "userProfile": UserProfile,
  "date": "YYYY-MM-DD"  // 可选，默认为今天
}

Response:
{
  "success": true,
  "data": {
    "hexagram": {
      "name": "晋卦",
      "pinyin": "Jìn",
      "english_name": "The Progress, Radiance",
      "title": "晋卦 (Jìn) - The Progress, Radiance",
      "energy": "Dynamic & Expansive",
      "luck": 85,
      "hexagram_text": "晋：康侯用锡马蕃庶，昼日三接。",
      "image_text": "明出地上，晋；君子以自昭明德。"
    },
    "timeAdvice": [
      {
        "period": "Morning (6:00 AM - 12:00 PM)",
        "start_time": "6:00 AM",
        "end_time": "12:00 PM",
        "activity": "Embrace New Beginnings",
        "description": "The morning brings fresh energy. Focus on planning and initiating new tasks. Your mind is sharpest now.",
        "energy": "High & Focused",
        "priority": "High"
      },
      {
        "period": "Afternoon (12:00 PM - 6:00 PM)",
        "start_time": "12:00 PM",
        "end_time": "6:00 PM",
        "activity": "Collaborate & Connect",
        "description": "Social interactions are favored. Engage in discussions, networking, and teamwork. Seek diverse perspectives.",
        "energy": "Social & Harmonious",
        "priority": "Medium"
      },
      {
        "period": "Evening (6:00 PM - 12:00 AM)",
        "start_time": "6:00 PM",
        "end_time": "12:00 AM",
        "activity": "Reflect & Recharge",
        "description": "Wind down and process the day's events. Engage in calming activities like meditation or reading. Prioritize rest.",
        "energy": "Calm & Restorative",
        "priority": "Medium"
      }
    ],
    "luckyElements": {
      "color": "Emerald Green",
      "direction": "Southeast",
      "number": 8,
      "element": "Wood",
      "gemstone": "Jade"
    },
    "personalAdvice": "Today, the energy of 'Progress' (晋卦) illuminates your path. Embrace opportunities for growth and expansion...",
    "aiGenerated": "Gemini AI 生成的运势内容"
  }
}
```

#### 4.2 获取运势历史
```javascript
GET /api/v1/daily-fortune/{userId}/history?limit=30

Response (统一列表格式):
{
  "success": true,
  "data": [DailyFortune],
  "total": 30,
  "page": null,
  "page_size": null,
  "message": null
}
```

## AI 集成设计

### 1. 提示词管理系统

#### 1.1 提示词管理器
```python
class PromptManager:
    """提示词管理器，负责读取和组合 prompt 文件"""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / "prompts"
        self._cache = {}  # 缓存读取的文件内容
    
    def get_complete_prompt(self, prompt_type: str, context: Dict[str, Any] = None) -> str:
        """获取完整的系统提示词"""
        # 根据类型获取对应的提示词模板
        base_prompt = self._read_prompt_file(f"{prompt_type}.md")
        
        # 如果有上下文信息，进行动态替换
        if context:
            base_prompt = self._replace_placeholders(base_prompt, context)
        
        return base_prompt
    
    def _read_prompt_file(self, filename: str) -> str:
        """读取指定的 prompt 文件"""
        if filename in self._cache:
            return self._cache[filename]
        
        file_path = self.prompts_dir / filename
        if not file_path.exists():
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self._cache[filename] = content
                return content
        except Exception as e:
            logger.error(f"读取 prompt 文件 {filename} 失败: {e}")
            return ""
    
    def _replace_placeholders(self, prompt: str, context: Dict[str, Any]) -> str:
        """替换提示词中的占位符"""
        for key, value in context.items():
            placeholder = f"${{{key}}}"
            prompt = prompt.replace(placeholder, str(value))
        return prompt
```

### 2. Gemini API 集成

#### 1.1 算命分析提示词（内在蓝图计算与生成指令）
```javascript
const fortuneTellingPrompt = `
# 内在蓝图计算与生成指令
## Inner Blueprint Calculation & Generation Command

## 角色与目标
你将扮演"平衡之境"应用中的一位整合生命策略师与心理顾问。你的核心任务分为两部分：
1. **计算与分析**：首先，作为一位精通八字命理的专家，你需要根据用户提供的出生信息，精确地完成八字排盘和五行分析。
2. **解读与撰写**：然后，你将切换到一位富有东方知识和魅力的心理顾问的角色，将这些分析结果转化为一份现代、科学、富有治愈感且具有优雅东方风格的个人特质报告，帮助用户自我认知与成长。

## 输入数据
你的提示词将直接接收用户的原始出生信息，格式如下：
- 性别：男生，女生，非二元，其他
- 出生日期：例如 "1990年8月15日"
- 出生时间：例如 "上午10:30"
- 出生地点：例如 "中国，四川省，成都市"

## 任务指令
你的任务是严格遵循以下两个步骤，完成从数据计算到报告生成的全过程：

### 第一步：八字排盘与五行分析（内部计算过程）
1. **校准时间与定盘**：根据输入的出生地点（经度），将出生时间校准为"真太阳时"。
2. **确立四柱**：依据校准后的时间，并严格按照二十四节气作为月份的划分标准，排出该用户的年、月、日、时四柱所对应的八个天干地支。
3. **分析五行强度**：基于排出的八字，以及天干地支的藏干，综合计算出金、木、水、火、土五个元素的各自力量得分（可以是一个相对的百分比或强度值）。
4. **识别核心要素**：确定用户命盘中的"主导元素"（最强的五行），并提炼出其八字格局的主要优势与潜在挑战，形成一段内部的文字摘要。

### 第二步：生成"内在蓝图"报告（最终输出内容）
利用你在第一步中计算和分析得出的所有结果（五行得分、主导元素、格局摘要等），生成一份用户报告。报告必须严格按照以下五个部分构成，每个部分都有固定的标题和内容规范：

#### 1. 核心能量场
- **标题**：此部分的标题应为"核心能量场 | Elemental Composition"
- **描述文字**：紧随标题的是一段固定的描述性文字："这是构成你内在世界的五种基本能量。它们之间的平衡与互动，塑造了你独特的个性与天赋。"
- **内容**：此部分的核心是为前端雷达图提供数据。你需要列出五行的名称（格式为"金 | Metal"、"木 | Wood"等）及它们各自对应的得分值。

#### 2. 核心本质
- **标题**："核心本质 | Core Essence"
- **内容**：根据输入数据中的"主导元素"，用一到两句精炼的语言，描绘出用户最核心的性格特质。例如，如果主导元素是"水"，描述可以是："你的核心能量如水，深邃、包容且极具适应性。你天生拥有强大的直觉和洞察力，能够敏锐地感知环境与人心的流动。"

#### 3. 天生优势
- **标题**："天生优势 | Natural Strengths"
- **内容**：基于用户的整体能量分布，提炼出三个最主要的优点。每个优点都应以一个简洁的短语呈现，并与一个具体的心理特质相关联，例如："深刻的同理心"、"灵活的适应力"或"卓越的沟通力"

#### 4. 成长挑战
- **标题**："成长挑战 | Growth Areas"
- **分析内容**：首先，你需要借助科学知识识别用户能量构成中的短板（最弱的元素）或潜在的冲突点。然后，用神秘、优雅、中立的口吻分析这种能量失衡在心理和行为上可能的表现。切记，要将其描述为成长的机会而非性格缺陷。例如，对于土元素不足，可以这样描述："你的能量构成中，'土'元素稍显不足。这可能意味着有时缺乏根基，没有归属感或安全感，在决断时犹豫不决，或在快节奏的生活中难以保持内心的稳定。"
- **平衡建议**：在分析之后，提供一个名为"平衡之道 | Path to Balance"的小节。其中包含三条具体、可在日常生活中执行的建议，每条建议都应简洁明了，并可对应一个前端的图标（如冥想、沟通、自然等）。例如："每日5分钟接地冥想练习，感受身体与大地的连接。"

#### 5. 生命曲线 (Life Journey Forecast)
1. **任务目标**：现在，你将扮演一位具有深刻洞见的生命规划与数据洞察顾问。你的任务是基于你在前面步骤中刚刚分析出的用户核心五行构成、优势和成长挑战，将其量化为可供雷达图使用的数据，并且结合用户的流年大运推演用户未来几年的生命成长主题，将其量化为可供曲线图使用的"能量波动"数据。因此，你的输出主要包含"核心能量场雷达图"和"生命曲线图"两个模块，并且，你的所有输出都必须同时服务于"数据可视化"和"人性化解读"两个目的。

2. **核心原则**：你生成的是一个充满可能性的"成长原型地图"。你需要将五行哲学的核心思想（生发、绽放、承载、收敛、蕴藏）与普适的个人成长心理学相结合，为用户提供一个积极、可操作的视角来看待未来。

3. **子模块一：核心能量场 (Core Energy Field)**
   - **任务目标**：将你在最开始第一步内部计算出的五行能量分数，在这里进行格式化输出，用于驱动雷达图。
   - **输出JSON结构**：
   ```json
   "core_energy_field": {
       "title": "核心能量场 | Elemental Composition",
       "description": "这是构成你内在世界的五种基本能量...",
       "chart_data": [
           {"axis": "金 | Metal", "value": 25},
           {"axis": "木 | Wood", "value": 15},
           {"axis": "水 | Water", "value": 30},
           {"axis": "火 | Fire", "value": 20},
           {"axis": "土 | Earth", "value": 10}
       ]
   }
   ```

4. **子模块二：生命曲线 (Life Journey Curve)**
   1. **内部推演步骤（Chain of Thought）**：在生成最终的JSON输出之前，请在你的"内心"遵循以下思考路径：
      1. **第一步：确立核心成长动力**
         - 回顾你为用户分析出的"主导元素"和"最弱元素"
         - 将此转化为未来几年的一个核心成长主题
         - 示例：如果用户主导元素是"木"（代表生长、开创），最弱元素是"金"（代表结构、纪律），那么她的核心成长主题可能是"为创造力建立秩序，将想法落地为成果"
      
      2. **第二步：分配年度原型主题与能量值**
         - 将上述核心成长主题分解到未来几年，为每一年分配一个符合逻辑递进关系的"五行原型"或"成长关键词"
         - 你必须严格遵循以下的"能量对应约定"，为每个主题分配一个0-100的"能量值"：
           - 85-100 (火原型): 用于表达"巅峰、绽放、热情"的年份
           - 60-84 (木原型): 用于表达"生长、开创、学习"的年份
           - 40-59 (土原型): 用于表达"稳定、规划、整合"的年份
           - 20-39 (金原型): 用于表达"收敛、精炼、建立规则"的年份
           - 0-19 (水原型): 用于表达"内省、休息、蓄力"的年份
         - 你的分配必须具有叙事逻辑。能量曲线的波动应尽量平滑自然，避免在没有合理解释的情况下，从"蕴藏期(15)"直接跳到"巅峰期(95)"
         - 示例（延续上例）：
           - 2025年 (近期)：分配"承载与规划 (土原型)"。理由：在将创造力构建为秩序之前，首先需要一个稳固的根基和清晰的计划。这是播种的准备阶段。
           - 2026年 (中期)：分配"绽放与表达 (火原型)"。理由：在有了规划之后，是时候将内在能量与才华向外展现，进行积极的尝试和表达。
           - 2027年 (远期)：分配"收敛与精炼 (金原型)"。理由：在经历了一年的绽放后，需要开始收敛成果，进行反思、优化，并建立更高效的系统和规则，这直接呼应了她的核心成长主题。
      
      3. **第三步：转化为用户语言**
         - 将你上述的"后台逻辑"翻译成最终用户看到的、充满鼓励和智慧的语言
      
      4. **第四步：可视化**
         - 按照你在上述"后台逻辑"中所分配的年份能量数值进行输出，用于生成曲线图，即"生命曲线"
         - **输出JSON结构**：
         ```json
         "life_journey_curve": {
             "title": "生命曲线 | Life Journey Forecast",
             "description": "未来数年你的能量将经历自然波动...",
             "chart_data": [
                 {
                     "year": 2025,
                     "energy_level": 55,
                     "is_turning_point": true,
                     "icon_id": "self_growth",
                     "event_description": "一个建立内在稳定和清晰规划的年份..."
                 }
                 // ... more data points
             ]
         }
         ```

## 核心规则与限制
1. **语言风格**：必须简洁、清晰、优雅，避免使用晦涩难懂或过度文学化的词藻
2. **积极正向**：所有的分析，尤其是挑战部分，都必须以积极、赋能的口吻呈现
3. **建议的可操作性**：提供的行动指南必须是具体的、现实可行的
4. **避免过度专业**：不能单独出现"天干地支"、"食神"、"七杀"等生僻命理术语。必须将其哲学内涵转化为易于理解、且富有神秘色彩的日常表达。可以适当出现通俗的命理表达，但是要搭配易于理解的日常化阐发

## 输出要求
请严格按照上述结构输出，确保每个部分都有明确的标题和内容，数据格式要规范，便于前端进行数据可视化和展示。
`;

#### 1.2 Heart Compass 指导提示词（心引罗盘）
```javascript
const heartCompassPrompt = `
# Heart Compass 指导提示词

## 概述
你是一个基于易经64卦的智慧指导师，专门为用户提供人生困惑的指导和建议。你需要根据用户的问题，结合易经智慧，生成结构化的指导内容。

## 输出格式要求
请严格按照以下JSON格式输出，不要添加任何其他内容：

\`\`\`json
{
  "hexagram": {
    "code": "卦序数字",
    "name": "中文卦名",
    "english_name": "英文卦名",
    "title": "完整标题",
    "hexagram_text": "卦辞",
    "image_text": "象辞",
    "focus_yao": {
      "yao_number": 爻位数字,
      "yao_text": "爻辞内容"
    }
  },
  "dialogue_flow": {
    "revelation": "启示内容",
    "analysis": "分析内容",
    "guidance": "指引内容",
    "encouragement": "鼓励内容"
  },
  "deep_wisdom": {
    "title": "Deep Wisdom",
    "explanation": "详细解释",
    "philosophical_meaning": "哲学含义",
    "personal_interpretation": "个人解读"
  },
  "action_guide": {
    "title": "Action Guide",
    "main_actions": ["主要行动1", "主要行动2"],
    "supporting_actions": ["支持行动1", "支持行动2"],
    "inspirational_message": "激励话语"
  },
  "decision_protocol": {
    "title": "决策协议 | Decision Protocol",
    "situation_code": "情境代码",
    "core_strategy": "核心策略",
    "action_guide": ["行动指南1", "行动指南2", "行动指南3"]
  }
}
\`\`\`

## 内容要求

### 1. 卦象信息 (hexagram)
- **code**: 卦序，从1到64
- **name**: 中文卦名，如"乾卦"
- **english_name**: 英文卦名，如"The Creative, Heaven"
- **title**: 完整标题，如"乾卦 - The Creative, Heaven"
- **hexagram_text**: 经典卦辞
- **image_text**: 象辞，解释卦象含义
- **focus_yao**: 焦点爻辞，选择最相关的爻位

### 2. 对话流 (dialogue_flow)
- **revelation**: 启示，用优美的语言表达核心智慧
- **analysis**: 分析，基于象辞分析用户当前处境
- **guidance**: 指引，提供具体的行动方向或心态建议
- **encouragement**: 鼓励，用温暖治愈的话语给予支持

### 3. 深层智慧 (deep_wisdom)
- **title**: 固定为"Deep Wisdom"
- **explanation**: 详细解释卦象的含义和象征
- **philosophical_meaning**: 哲学层面的深层含义
- **personal_interpretation**: 对用户个人情况的解读

### 4. 行动指南 (action_guide)
- **title**: 固定为"Action Guide"
- **main_actions**: 2条主要行动建议
- **supporting_actions**: 2条支持性行动建议
- **inspirational_message**: 激励话语，鼓励用户行动

### 5. 决策协议 (decision_protocol)
- **title**: 固定为"决策协议 | Decision Protocol"
- **situation_code**: 情境代码，如"乾卦 (#1)"
- **core_strategy**: 核心策略，四字短语
- **action_guide**: 3条具体的行动指南

## 指导原则

1. **个性化**: 根据用户的具体问题和背景，选择最合适的卦象
2. **实用性**: 提供具体可操作的建议，避免空洞的理论
3. **平衡性**: 既要指出优势，也要提醒需要注意的方面
4. **鼓励性**: 用积极正面的语言，给予用户信心和力量
5. **文化融合**: 结合中西方智慧，让指导更易理解

## 注意事项

1. 确保所有字段都有内容，不要留空
2. 卦象选择要准确，符合易经传统
3. 语言要温暖、智慧、实用
4. 建议要具体可操作
5. 保持中英文的准确对应
`;
```

#### 1.3 每日运势提示词
```javascript
const dailyFortunePrompt = `
# Daily Fortune 每日运势提示词

## 概述
你是一个基于易经64卦的每日运势分析师，专门为用户生成个性化的每日运势分析。你需要根据用户的出生信息，结合当日的天象和易经智慧，生成结构化的运势内容。

## 输出格式要求
请严格按照以下JSON格式输出，不要添加任何其他内容：

\`\`\`json
{
  "hexagram": {
    "name": "中文卦名",
    "pinyin": "拼音",
    "english_name": "英文含义",
    "title": "完整标题",
    "energy": "能量描述",
    "luck": 幸运指数,
    "hexagram_text": "卦辞",
    "image_text": "象辞"
  },
  "time_advice": [
    {
      "period": "时间段",
      "start_time": "开始时间",
      "end_time": "结束时间",
      "activity": "建议活动",
      "description": "详细描述",
      "energy": "能量状态",
      "priority": "优先级"
    }
  ],
  "lucky_elements": {
    "color": "幸运颜色",
    "direction": "幸运方向",
    "number": 幸运数字,
    "element": "幸运元素",
    "gemstone": "幸运宝石"
  },
  "personal_advice": "个性化建议"
}
\`\`\`

## 内容要求

### 1. 卦象信息 (hexagram)
- **name**: 中文卦名，如"晋卦"
- **pinyin**: 拼音，如"Jìn"
- **english_name**: 英文含义，如"The Progress, Radiance"
- **title**: 完整标题，如"晋卦 (Jìn) - The Progress, Radiance"
- **energy**: 能量描述，如"Dynamic & Expansive"
- **luck**: 幸运指数，0-100的整数
- **hexagram_text**: 经典卦辞
- **image_text**: 象辞，解释卦象含义

### 2. 时段建议 (time_advice)
必须包含三个时段，每个时段包含：

- **period**: 时间段名称，如"Morning (6:00 AM - 12:00 PM)"
- **start_time**: 开始时间，如"6:00 AM"
- **end_time**: 结束时间，如"12:00 PM"
- **activity**: 建议活动，如"Embrace New Beginnings"
- **description**: 详细描述，如"The morning brings fresh energy. Focus on planning and initiating new tasks. Your mind is sharpest now."
- **energy**: 能量状态，如"High & Focused"
- **priority**: 优先级，如"High"

**三个时段要求**：
1. **Morning**: 6:00 AM - 12:00 PM
2. **Afternoon**: 12:00 PM - 6:00 PM  
3. **Evening**: 6:00 PM - 12:00 AM

### 3. 幸运元素 (lucky_elements)
- **color**: 幸运颜色，如"Emerald Green"
- **direction**: 幸运方向，如"Southeast"
- **number**: 幸运数字，如8
- **element**: 幸运元素，如"Wood"
- **gemstone**: 幸运宝石，如"Jade"

### 4. 个性化建议 (personal_advice)
一段详细的个性化建议，包含：
- 当日卦象对用户的影响
- 基于用户特质的建议
- 具体的行动指导
- 注意事项和提醒

## 指导原则

1. **个性化**: 根据用户的出生信息和特质，生成相关的运势分析
2. **实用性**: 提供具体可操作的建议，避免空洞的理论
3. **平衡性**: 既要指出优势，也要提醒需要注意的方面
4. **鼓励性**: 用积极正面的语言，给予用户信心和力量
5. **文化融合**: 结合中西方智慧，让运势更易理解

## 注意事项

1. 确保所有字段都有内容，不要留空
2. 卦象选择要准确，符合易经传统
3. 时段建议要具体可操作
4. 幸运元素要符合五行理论
5. 个性化建议要温暖、智慧、实用
6. 幸运指数要根据卦象和用户特质合理设定
7. 保持中英文的准确对应
`;
```

### 2. AI 响应处理

#### 2.1 基础 AI 服务封装
```python
# AI 服务基础封装示例
import os
import asyncio
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import time

class GeminiInteractionAPI:
    """与 Gemini AI 模型进行交互的 API 封装"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        self.model_name = "gemini-2.5-flash"
        self.max_retries = 3  # 最大重试次数
        self.timeout = 60  # 请求超时时间（秒）
        
    async def send_message_to_ai(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """向 Gemini API 发送消息并获取响应"""
        try:
            # 构建请求数据
            request_data = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.95,
                    "maxOutputTokens": 8192  # 增加输出token限制，支持长提示词
                }
            }
            
            # 发送 API 请求（包含重试机制）
            response_json = await self._make_api_request(request_data)
            
            # 解析响应
            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                candidate = response_json['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    ai_response = candidate['content']['parts'][0]['text'].strip()
                    return {
                        "success": True,
                        "message": ai_response,
                        "timestamp": datetime.now().isoformat()
                    }
            
            raise Exception("API 响应格式错误")
            
        except Exception as e:
            logger.error(f'Gemini API 调用失败: {e}')
            return await self.get_fallback_response()
    
    async def _make_api_request(self, request_data: dict) -> dict:
        """向 Gemini API 发送请求（包含重试机制）"""
        full_url = f"{self.api_url}?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        # 重试机制
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                response = requests.post(
                    full_url, 
                    json=request_data, 
                    headers=headers, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    response.raise_for_status()
                    
            except Exception as e:
                retry_count += 1
                if retry_count >= self.max_retries:
                    raise Exception(f"Gemini API 调用最终失败，已达到最大重试次数 {self.max_retries}")
                
                # 指数退避策略：2^retry_count 秒
                sleep_time = 2 ** retry_count
                await asyncio.sleep(sleep_time)
        
        raise Exception("Gemini API 调用最终失败")
    
    async def get_fallback_response(self) -> Dict[str, Any]:
        """获取备用响应（当 API 调用失败时使用）"""
        return {
            "success": False,
            "message": "抱歉，AI 服务暂时不可用，请稍后再试。",
            "timestamp": datetime.now().isoformat()
        }
```

#### 2.2 AI 响应处理器
```python
class AIResponseProcessor:
    """AI 响应处理器类 - 单例模式"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.ai_responses = {}  # 缓存 AI 响应
        return cls._instance
    
    async def process_ai_response(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理 AI 响应，包含缓存和错误处理"""
        try:
            # 检查缓存
            cache_key = self._generate_cache_key(prompt, context)
            if cache_key in self.ai_responses:
                return self.ai_responses[cache_key]
            
            # 调用 AI 服务
            ai_service = GeminiInteractionAPI()
            response = await ai_service.send_message_to_ai(prompt, context)
            
            # 缓存成功响应
            if response.get("success"):
                self.ai_responses[cache_key] = response
            
            return response
            
        except Exception as e:
            logger.error(f'AI 响应处理失败: {e}')
            return {
                "success": False,
                "message": "AI 服务处理失败，请稍后再试。",
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_cache_key(self, prompt: str, context: Dict[str, Any]) -> str:
        """生成缓存键"""
        import hashlib
        content = f"{prompt}_{str(context)}"
        return hashlib.md5(content.encode()).hexdigest()
```

## 数据流设计

### 1. 新用户流程
```
1. 前端检查用户状态 → GET /api/user/status
2. 收集用户信息 → 前端表单收集（性别、出生日期、出生时间、出生地点）
3. 创建用户 → POST /api/user/create
4. 生成算命结果 → POST /api/blueprint/generate
   - 调用 Gemini AI 进行八字排盘和五行分析
   - 生成内在蓝图报告（核心能量场、核心本质、天生优势、成长挑战、生命曲线）
5. 存储结果 → 数据库存储（包含完整的八字数据和内在蓝图）
6. 进入主界面 → 前端状态更新
```

### 2. 老用户流程
```
1. 前端检查用户状态 → GET /api/user/status
2. 直接进入主界面 → 前端状态更新
3. 加载用户数据 → GET /api/blueprint/:userId
   - 获取完整的八字排盘数据
   - 获取内在蓝图报告（用于前端数据可视化）
   - 获取历史运势和指导记录
```

### 3. Heart Compass 流程
```
1. 用户提问 → 前端收集困惑文本
2. 发送请求 → POST /api/heart-compass/seek-guidance
3. 调用 Gemini API → 生成结构化指导
   - 内部推演与匹配（分析困惑核心、匹配最佳卦象、定位焦点爻辞）
   - 生成结构化回复（对话流四个环节 + 深层智慧 + 行动指南 + 决策协议）
4. 存储记录 → 数据库存储（包含完整的卦象信息和结构化指导）
5. 返回结果 → 前端展示（支持逐段动画展示和决策协议卡片）

6. 重新提问流程（可选）：
   - 用户深入探讨 → POST /api/heart-compass/ask-again
   - 基于之前指导的上下文关联
   - 生成更深入的指导内容
   - 支持连续对话和深入分析
```

### 4. Daily Fortune 流程
```
1. 用户进入 → 前端触发
2. 检查今日运势 → 查询数据库
3. 如果不存在 → POST /api/daily-fortune/generate
4. 调用 Gemini API → 生成运势分析
5. 存储结果 → 数据库存储
6. 返回结果 → 前端展示
```

## 错误处理

### 1. 错误码定义
```python
from enum import IntEnum
from fastapi import HTTPException
from typing import Dict, Any

class ErrorCodes(IntEnum):
    # 用户相关错误 (1000-1999)
    USER_NOT_FOUND = 1001
    INVALID_BIRTH_INFO = 1002
    USER_ALREADY_EXISTS = 1003
    INVALID_DEVICE_ID = 1004
    
    # AI 服务相关错误 (2000-2999)
    AI_SERVICE_UNAVAILABLE = 2001
    AI_RESPONSE_INVALID = 2002
    AI_TIMEOUT = 2003
    AI_RATE_LIMIT_EXCEEDED = 2004
    
    # 数据库相关错误 (3000-3999)
    DATABASE_ERROR = 3001
    DATABASE_CONNECTION_FAILED = 3002
    DATA_VALIDATION_ERROR = 3003
    
    # 验证相关错误 (4000-4999)
    VALIDATION_ERROR = 4001
    INVALID_TOKEN = 4002
    TOKEN_EXPIRED = 4003
    
    # 系统相关错误 (5000-5999)
    RATE_LIMIT_EXCEEDED = 5001
    INTERNAL_SERVER_ERROR = 5002
    SERVICE_UNAVAILABLE = 5003

class AppException(HTTPException):
    """自定义应用异常类"""
    
    def __init__(self, error_code: int, message: str, details: str = None):
        self.error_code = error_code
        self.details = details
        
        super().__init__(
            status_code=self._get_status_code(error_code),
            detail={
                "success": False,
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": details
                }
            }
        )
    
    def _get_status_code(self, error_code: int) -> int:
        """根据错误码获取 HTTP 状态码"""
        if error_code < 2000:
            return 400  # Bad Request
        elif error_code < 3000:
            return 503  # Service Unavailable
        elif error_code < 4000:
            return 500  # Internal Server Error
        elif error_code < 5000:
            return 401  # Unauthorized
        else:
            return 500  # Internal Server Error

# 错误处理装饰器
def handle_errors(func):
    """统一错误处理装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppException:
            raise
        except Exception as e:
            logger.error(f"未处理的异常: {str(e)}", exc_info=True)
            raise AppException(
                ErrorCodes.INTERNAL_SERVER_ERROR,
                "服务器内部错误",
                str(e)
            )
    return wrapper
```

### 2. 错误响应格式
```python
from enum import IntEnum

class ErrorCodes(IntEnum):
    USER_NOT_FOUND = 1001
    INVALID_BIRTH_INFO = 1002
    AI_SERVICE_UNAVAILABLE = 2001
    DATABASE_ERROR = 3001
    VALIDATION_ERROR = 4001
    RATE_LIMIT_EXCEEDED = 5001
```

### 2. 错误响应格式
```python
{
  "success": False,
  "error": {
    "code": 1001,
    "message": "用户不存在",
    "details": "详细错误信息"
  }
}
```

## 性能优化建议

### 1. 版本化缓存策略（零脏数据风险）

#### 1.1 核心设计理念
```python
"""
版本化缓存的核心思想：
1. 每个实体（用户、算命结果等）都有唯一的版本号
2. 缓存键包含版本号，确保数据一致性
3. 数据更新时版本号递增，旧版本自动失效
4. 通过版本号匹配，从根本上避免脏数据问题
"""
```

#### 1.2 智能缓存管理器
```python
import redis
import json
import hashlib
from typing import Any, Optional, Dict
from functools import wraps
from datetime import datetime, timedelta

class VersionedCacheManager:
    """版本化缓存管理器 - 零脏数据风险"""
    
    def __init__(self):
        # Redis 客户端（主缓存）
        self.redis_client = None
        try:
            self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
            self.redis_client.ping()
        except:
            self.redis_client = None
            logger.warning("Redis 连接失败，将使用内存缓存")
        
        # 内存缓存（热点数据 + 备用）
        self.memory_cache = {}
        
        # 实体版本管理（Redis 或内存）
        self.version_store = {}
        
        # 依赖关系映射
        self.dependency_map = {
            "user:profile": ["ai:blueprint", "ai:daily_fortune", "ai:heart_compass"],
            "ai:blueprint": ["ai:daily_fortune"],
            "ai:daily_fortune": [],
            "ai:heart_compass": []
        }
        
        # 缓存统计
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0,
            "version_mismatches": 0
        }
    
    async def get_entity_version(self, entity_id: str, entity_type: str = "user") -> int:
        """获取实体当前版本号"""
        try:
            if self.redis_client:
                version_key = f"{entity_type}:{entity_id}:version"
                version = await self.redis_client.get(version_key)
                return int(version) if version else 1
            else:
                key = f"{entity_type}:{entity_id}"
                return self.version_store.get(key, 1)
        except Exception as e:
            logger.error(f"获取实体版本失败: {e}")
            return 1
    
    async def increment_entity_version(self, entity_id: str, entity_type: str = "user") -> int:
        """递增实体版本号"""
        try:
            current_version = await self.get_entity_version(entity_id, entity_type)
            new_version = current_version + 1
            
            if self.redis_client:
                version_key = f"{entity_type}:{entity_id}:version"
                await self.redis_client.set(version_key, new_version)
            else:
                key = f"{entity_type}:{entity_id}"
                self.version_store[key] = new_version
            
            logger.info(f"实体 {entity_type}:{entity_id} 版本已更新: {current_version} -> {new_version}")
            return new_version
            
        except Exception as e:
            logger.error(f"更新实体版本失败: {e}")
            return current_version + 1
    
    async def set_with_version(self, key: str, value: Any, entity_id: str, entity_type: str = "user", expire: int = 3600):
        """设置带版本号的缓存（核心方法）"""
        try:
            # 1. 获取当前版本号
            version = await self.get_entity_version(entity_id, entity_type)
            
            # 2. 构建版本化缓存键
            versioned_key = f"{key}:v{version}"
            
            # 3. 构建缓存数据
            cache_data = {
                "value": value,
                "version": version,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "created_at": datetime.now().isoformat(),
                "expire_at": (datetime.now() + timedelta(seconds=expire)).isoformat()
            }
            
            # 4. 存储到 Redis
            if self.redis_client:
                await self.redis_client.setex(
                    versioned_key, 
                    expire, 
                    json.dumps(cache_data, ensure_ascii=False)
                )
            
            # 5. 存储到内存（热点数据）
            if self._is_hot_data(key):
                self.memory_cache[versioned_key] = cache_data
            
            logger.debug(f"已缓存 {versioned_key}，版本: {version}")
            
        except Exception as e:
            logger.error(f"设置版本化缓存失败: {e}")
    
    async def get_with_version_check(self, key: str, entity_id: str, entity_type: str = "user"):
        """获取带版本检查的缓存（核心方法）"""
        try:
            # 1. 获取当前版本号
            current_version = await self.get_entity_version(entity_id, entity_type)
            
            # 2. 尝试从内存缓存获取
            memory_key = f"{key}:v{current_version}"
            if memory_key in self.memory_cache:
                cache_data = self.memory_cache[memory_key]
                if self._is_cache_valid(cache_data):
                    self.cache_stats["hits"] += 1
                    return cache_data["value"]
            
            # 3. 尝试从 Redis 获取
            if self.redis_client:
                redis_key = f"{key}:v{current_version}"
                cache_data = await self._get_from_redis(redis_key)
                
                if cache_data and self._is_cache_valid(cache_data):
                    # 缓存命中，更新内存缓存
                    if self._is_hot_data(key):
                        self.memory_cache[memory_key] = cache_data
                    self.cache_stats["hits"] += 1
                    return cache_data["value"]
            
            # 4. 缓存未命中
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"获取版本化缓存失败: {e}")
            return None
    
    async def invalidate_entity_cache(self, entity_id: str, entity_type: str = "user", reason: str = "数据更新"):
        """失效实体所有相关缓存（核心方法）"""
        try:
            # 1. 递增版本号
            new_version = await self.increment_entity_version(entity_id, entity_type)
            
            # 2. 失效所有相关缓存
            patterns = self._get_invalidation_patterns(entity_id, entity_type)
            
            for pattern in patterns:
                await self._invalidate_pattern(pattern)
            
            # 3. 记录失效日志
            await self._log_invalidation(entity_id, entity_type, reason, patterns, new_version)
            
            logger.info(f"实体 {entity_type}:{entity_id} 缓存已失效，新版本: {new_version}")
            
        except Exception as e:
            logger.error(f"失效实体缓存失败: {e}")
            raise
    
    def _get_invalidation_patterns(self, entity_id: str, entity_type: str) -> list:
        """获取需要失效的缓存模式"""
        patterns = []
        
        # 基础模式
        if entity_type == "user":
            patterns.extend([
                f"user:profile:{entity_id}:*",
                f"ai:blueprint:{entity_id}:*",
                f"ai:daily_fortune:{entity_id}:*",
                f"ai:heart_compass:{entity_id}:*"
            ])
        elif entity_type == "blueprint":
            patterns.extend([
                f"ai:blueprint:{entity_id}:*",
                f"ai:daily_fortune:{entity_id}:*"
            ])
        
        return patterns
    
    def _is_cache_valid(self, cache_data: dict) -> bool:
        """检查缓存是否有效"""
        try:
            if not cache_data:
                return False
            
            # 检查过期时间
            if "expire_at" in cache_data:
                expire_time = datetime.fromisoformat(cache_data["expire_at"])
                if datetime.now() > expire_time:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"缓存有效性检查失败: {e}")
            return False
    
    def _is_hot_data(self, key: str) -> bool:
        """判断是否为热点数据"""
        hot_patterns = [
            "user:profile",
            "ai:blueprint",
            "ai:daily_fortune"
        ]
        return any(pattern in key for pattern in hot_patterns)
```

#### 1.3 智能缓存装饰器
```python
def versioned_cache(entity_type: str = "user", expire: int = 3600):
    """版本化缓存装饰器 - 自动处理版本号"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中提取 entity_id
            entity_id = kwargs.get('user_id') or args[0] if args else None
            
            if not entity_id:
                # 如果没有 entity_id，使用传统缓存
                return await func(*args, **kwargs)
            
            # 构建缓存键
            cache_key = f"{func.__name__}:{entity_id}"
            
            # 尝试从版本化缓存获取
            cache_manager = VersionedCacheManager()
            cached_result = await cache_manager.get_with_version_check(
                cache_key, entity_id, entity_type
            )
            
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            
            # 设置版本化缓存
            await cache_manager.set_with_version(
                cache_key, result, entity_id, entity_type, expire
            )
            
            return result
        return wrapper
    return decorator
```

### 2. 版本化缓存使用示例

#### 2.1 用户信息管理
```python
class UserService:
    """用户服务 - 使用版本化缓存"""
    
    @versioned_cache(entity_type="user", expire=3600)
    async def get_user_profile(self, user_id: str):
        """获取用户信息 - 自动版本化缓存"""
        # 从数据库获取用户信息
        user = await Database.find_one("users", {"userId": user_id})
        return user
    
    async def update_user_profile(self, user_id: str, new_profile: dict):
        """更新用户信息 - 自动失效相关缓存"""
        try:
            # 1. 更新数据库
            await Database.update_one(
                "users", 
                {"userId": user_id}, 
                {"$set": new_profile}
            )
            
            # 2. 失效用户所有相关缓存（自动递增版本号）
            cache_manager = VersionedCacheManager()
            await cache_manager.invalidate_entity_cache(
                user_id, "user", "用户信息更新"
            )
            
            logger.info(f"用户 {user_id} 信息已更新，缓存已失效")
            
        except Exception as e:
            logger.error(f"更新用户信息失败: {e}")
            raise
```

#### 2.2 AI 服务集成
```python
class BlueprintService:
    """算命分析服务 - 使用版本化缓存"""
    
    @versioned_cache(entity_type="blueprint", expire=86400)
    async def generate_blueprint(self, user_id: str, user_profile: dict):
        """生成算命结果 - 自动版本化缓存"""
        # 调用 Gemini AI 生成算命结果
        ai_service = GeminiInteractionAPI()
        result = await ai_service.generate_blueprint(user_profile)
        
        # 保存到数据库
        await Database.insert_one("blueprint_results", {
            "userId": user_id,
            "result": result,
            "createdAt": datetime.now()
        })
        
        return result
    
    async def regenerate_blueprint(self, user_id: str, user_profile: dict):
        """重新生成算命结果 - 自动失效缓存"""
        try:
            # 1. 删除旧的算命结果
            await Database.delete_one("blueprint_results", {"userId": user_id})
            
            # 2. 失效相关缓存（自动递增版本号）
            cache_manager = VersionedCacheManager()
            await cache_manager.invalidate_entity_cache(
                user_id, "blueprint", "算命结果重新生成"
            )
            
            # 3. 重新生成
            return await self.generate_blueprint(user_id, user_profile)
            
        except Exception as e:
            logger.error(f"重新生成算命结果失败: {e}")
            raise
```

### 3. 版本化缓存的核心优势

#### 3.1 零脏数据风险
- **版本号隔离**：每个缓存项都有唯一版本号，旧版本数据自动失效
- **自动失效**：数据更新时版本号递增，相关缓存自动失效
- **一致性保证**：通过版本号匹配，确保用户始终看到最新数据

#### 3.2 高性能缓存
- **热点数据优先**：热点数据存储在内存中，响应速度极快
- **智能缓存选择**：自动判断数据应该存储在 Redis 还是内存
- **版本化查找**：通过版本号快速定位有效缓存

#### 3.3 运维友好
- **完整日志记录**：所有缓存操作都有详细日志
- **统计信息**：缓存命中率、失效次数等统计
- **自动清理**：过期缓存自动清理，防止内存泄漏

### 4. 版本化缓存工作流程

#### 4.1 完整的数据更新流程
```
用户更新信息 → 数据库更新 → 版本号递增 → 相关缓存失效 → 新数据缓存
    ↓
1. 用户修改出生日期
2. 系统更新 MongoDB 中的用户记录
3. 用户版本号从 v1 递增到 v2
4. 自动失效所有 v1 版本的缓存：
   - user:profile:12345:v1
   - ai:blueprint:12345:hash:v1
   - ai:daily_fortune:12345:2024-01-01:v1
   - ai:heart_compass:12345:question_hash:2024-01-01:v1
5. 下次查询时自动使用 v2 版本
```

#### 4.2 缓存读取流程
```
用户查询 → 版本号检查 → 缓存查找 → 缓存命中/未命中 → 数据返回
    ↓
1. 用户请求个人信息
2. 系统检查用户当前版本号（v2）
3. 在缓存中查找 user:profile:12345:v2
4. 如果找到且未过期 → 直接返回（缓存命中）
5. 如果没找到 → 从数据库读取并缓存为 v2 版本
```

#### 4.3 版本号管理机制
```
实体版本存储：
- Redis: user:12345:version = 2
- 内存: version_store["user:12345"] = 2

缓存键格式：
- 用户信息: user:profile:12345:v2
- 算命结果: ai:blueprint:12345:hash:v2
- 每日运势: ai:daily_fortune:12345:2024-01-01:v2
- Heart Compass: ai:heart_compass:12345:question_hash:2024-01-01:v2
```

### 5. 数据库优化
- 用户查询索引：在 userId 和 deviceId 上建立索引
- 时间查询索引：在 createdAt 和 date 字段上建立索引
- 复合索引：在 userId + date 上建立复合索引
- MongoDB 聚合查询优化：使用聚合管道优化复杂查询

### 3. API 优化
- 响应压缩：启用 gzip 压缩
- 分页查询：大数据量查询使用分页
- 异步处理：AI 调用使用异步队列处理
- FastAPI 自动文档：自动生成 OpenAPI 文档和交互式测试界面

## 配置管理

### 1. 环境配置
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = "Realm of Balance App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "realm_of_balance"
    MONGODB_USERNAME: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_AUTH_SOURCE: str = ""
    
    # Gemini API 配置
    GEMINI_API_KEY: str
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    GEMINI_MODEL_NAME: str = "gemini-2.5-flash"
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis 配置（可选）
    REDIS_URL: Optional[str] = None
    
    # 服务配置
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### 2. 日志配置
```python
import logging
from datetime import datetime

class MyLogger:
    """自定义日志管理器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(f"logs/{name}.log", encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str, exc_info=False):
        self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
```

## 部署建议

### 1. 环境配置
```python
# 环境变量配置
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8000
    mongo_uri: str
    gemini_api_key: str
    jwt_secret: str
    redis_url: str = None
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. 安全措施
- API 限流：防止恶意请求
- 输入验证：严格验证用户输入
- 数据加密：敏感信息加密存储
- CORS 配置：限制跨域请求

### 3. 监控告警
- 性能监控：API 响应时间监控
- 错误监控：错误率监控和告警
- AI 服务监控：Gemini API 调用状态监控
- 数据库监控：数据库性能监控

## 测试建议

### 1. 单元测试
- 使用 pytest 测试所有 API 接口
- 测试 AI 提示词生成
- 测试数据验证逻辑
- 测试 Pydantic 模型验证

### 2. 集成测试
- 测试完整的用户流程
- 测试 AI 集成功能
- 测试 MongoDB 数据库操作
- 测试 FastAPI 中间件

### 3. 性能测试
- 测试并发用户处理能力
- 测试 AI 响应时间
- 测试 MongoDB 查询性能
- 使用 FastAPI 内置的性能监控

## 项目结构建议

### 1. 目录结构
```
realm_of_balance_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # 数据库连接管理
│   │   ├── security.py         # 安全相关（JWT等）
│   │   └── cache.py            # 缓存管理
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── user.py         # 用户管理接口
│   │   │   ├── blueprint.py    # 算命分析接口
│   │   │   ├── heart_compass.py # Heart Compass接口
│   │   │   └── daily_fortune.py # 每日运势接口
│   │   └── dependencies.py     # 依赖注入
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
│   │   ├── prompt_manager.py   # 提示词管理
│   │   └── helpers.py          # 辅助函数
│   └── prompts/                # AI 提示词模板
│       ├── blueprint.md        # 算命分析提示词
│       ├── heart_compass.md    # Heart Compass提示词
│       └── daily_fortune.md    # 每日运势提示词
├── tests/                      # 测试文件
├── logs/                       # 日志文件
├── requirements.txt             # 依赖包
├── .env                        # 环境变量
├── .gitignore
└── README.md
```

### 2. 核心依赖包
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.1
pymongo==4.6.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
requests==2.31.0
python-dotenv==1.0.0
```

## 总结

这个后端系统已经实现：
1. **完整的用户管理功能**：支持新老用户识别、信息收集和更新 ✅
2. **专业的八字排盘系统**：基于二十四节气的准确时间校准和四柱计算 ✅
3. **与 Gemini AI 的深度集成**：三个核心功能的专业提示词设计，支持长提示词 ✅
4. **结构化的内在蓝图数据**：支持前端雷达图、曲线图等数据可视化 ✅
5. **高效的数据存储和查询**：MongoDB 存储复杂的八字和蓝图数据结构 ✅
6. **稳定的错误处理和性能优化**：确保 AI 集成的稳定性和用户体验的流畅性 ✅
7. **零脏数据风险的版本化缓存系统**：通过版本号机制从根本上解决缓存一致性问题 ✅
8. **数据结构统一**：所有API使用统一的响应格式，字段命名规范 ✅
9. **AI服务优化**：Gemini API配置优化，支持复杂生成任务 ✅

### 技术特点
- **数据结构化**：内在蓝图报告采用标准化的 JSON 结构，便于前端渲染 ✅
- **AI 专业化**：算命分析提示词包含完整的八字排盘逻辑和报告生成规范 ✅
- **Heart Compass 结构化**：对话流四环节 + 深层智慧 + 行动指南 + 决策协议的结构化指导系统 ✅
- **可视化支持**：核心能量场雷达图、生命曲线图和 Heart Compass 动画展示 ✅
- **用户体验优化**：新老用户流程分离，减少重复操作 ✅
- **版本化缓存系统**：通过版本号机制实现零脏数据风险的高性能缓存 ✅
- **FastAPI 优势**：自动文档生成、类型安全、异步支持、高性能 ✅
- **MongoDB 优势**：灵活的文档结构、强大的聚合查询、水平扩展能力 ✅
- **数据结构统一**：所有API使用统一的响应格式，字段命名规范 ✅
- **AI服务优化**：Gemini API配置优化，支持复杂生成任务 ✅

### 当前系统状态 (2024年8月最新)
- **所有核心功能已实现并测试通过** ✅
- **AI服务完全正常工作**：个人蓝图、Heart Compass、每日运势生成 ✅
- **数据结构完全统一**：API响应格式、字段命名、模型继承体系 ✅
- **字段命名问题已修复**：所有数据库字段统一使用snake_case ✅
- **性能优化完成**：版本化缓存、AI服务配置、错误处理 ✅
- **系统稳定性**：所有API端点正常工作，错误处理完善 ✅
- **测试覆盖率**：26个API接口全部测试通过，无未测试接口 ✅

### 最新更新内容 (2024年8月)

#### 0. 字段命名统一修复 (重要更新)
- **统一snake_case命名**: 数据库、API、模型全部统一使用snake_case命名
- **字段映射问题修复**: 修复了用户服务中的`deviceId`→`device_id`等字段名不一致问题
- **Heart Compass排序字段修复**: 修复了`createdAt`→`created_at`排序字段问题
- **用户模型别名移除**: 移除了Pydantic模型中的冗余alias配置
- **集合名称统一**: 修复了`daily_fortunes`→`daily_fortune_records`的集合名不一致问题
- **API文档字段名更新**: 所有API文档示例统一使用snake_case字段名

#### 1. 数据结构统一 (重要更新)
- **统一响应格式**: 所有API使用`BaseResponse[T]`或`ListResponse[T]`统一响应格式
- **字段命名规范**: 数据库、API、模型全部统一使用snake_case，确保完全一致
- **模型继承体系**: 创建`BaseDBModel`、`UserProfileBase`、`Hexagram`等基础模型
- **类型安全**: 使用泛型确保响应数据类型安全，消除运行时错误
- **零脏数据缓存**: 版本化缓存系统确保数据一致性

#### 1. AI服务配置优化 (重要更新)
- **Gemini API配置**: 将`maxOutputTokens`从2048提升到8192，支持长提示词
- **个人蓝图提示词**: 恢复使用原版`blueprint.md`提示词，支持完整的八字分析和内在蓝图生成
- **错误处理增强**: 改进token限制检测和部分响应处理
- **性能优化**: 支持更复杂的AI生成任务，响应时间优化

#### 1. Heart Compass 功能增强
- **新增深层智慧模块**：包含详细解释、哲学含义、个人解读
- **新增行动指南模块**：主要行动、支持行动、激励话语
- **支持英文卦名**：中英文双语支持，国际化友好
- **重新提问功能**：支持基于之前指导的深入探讨和上下文关联

#### 2. Daily Fortune 功能优化
- **扩展卦象信息**：新增拼音、英文含义、卦辞、象辞
- **精确时段建议**：支持开始时间、结束时间、优先级设置
- **丰富幸运元素**：新增幸运元素、幸运宝石
- **结构化输出**：严格按照JSON格式输出，便于前端解析

#### 3. 数据模型优化
- **统一字段命名**：采用下划线命名规范，保持一致性
- **增强数据验证**：使用Pydantic Field验证器，确保数据质量
- **支持可选字段**：灵活处理可选参数，提高系统健壮性

#### 4. API接口完善
- **新增重新提问接口**：`POST /api/heart-compass/ask-again`
- **优化运势历史接口**：支持分页和限制查询
- **统一响应格式**：所有接口采用一致的响应结构

建议采用 **Python + FastAPI + MongoDB** 的技术栈，这样可以快速开发并具有良好的扩展性。关键是要确保 AI 集成的稳定性和用户体验的流畅性，同时支持复杂的数据可视化需求。
