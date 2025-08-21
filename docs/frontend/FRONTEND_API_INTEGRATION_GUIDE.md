# Realm of Balance App 前端API集成指南

> **重要更新**: 本文档已更新以反映最新的字段命名统一修复，所有API响应字段现在统一使用snake_case命名，确保前端集成的一致性。所有代码示例已更新以反映实际的API测试结果。

## 📋 目录
1. [AI服务优化说明](#ai服务优化说明)
2. [统一响应格式说明](#统一响应格式说明)
3. [基础配置](#基础配置)
4. [用户管理功能](#用户管理功能)
5. [Personal Blueprint 功能](#personal-blueprint-功能)
6. [Heart Compass 功能](#heart-compass-功能)
7. [Daily Fortune 功能](#daily-fortune-功能)
8. [错误处理](#错误处理)
9. [最佳实践](#最佳实践)

---

## 🚀 AI服务优化说明

### 1. Gemini API配置优化
- **输出Token限制**: 已从2048提升到8192，支持更复杂的AI生成任务
- **长提示词支持**: 个人蓝图现在使用原版`blueprint.md`提示词，生成完整的八字分析和内在蓝图
- **错误处理增强**: 改进token限制检测，支持部分响应处理
- **性能优化**: 支持更复杂的AI生成任务，响应时间优化

### 2. 支持的AI功能
- **个人蓝图生成**: 完整的八字排盘、五行分析、内在蓝图报告
- **Heart Compass指导**: 基于易经64卦的个性化指导和建议
- **每日运势生成**: 个性化的每日运势分析和时段建议

## 📊 统一响应格式说明

### 1. 基础响应格式
所有API接口现在使用统一的响应格式，确保数据结构的一致性：

```javascript
// 单个数据响应格式
{
  "success": boolean,        // 请求是否成功
  "data": object | null,     // 响应数据，失败时为null
  "message": string | null   // 响应消息，成功时通常为null，失败时包含错误信息
}

// 列表数据响应格式  
{
  "success": boolean,        // 请求是否成功
  "data": array,            // 数据数组
  "total": number,          // 总记录数
  "page": number | null,    // 当前页码（有分页时）
  "page_size": number | null, // 每页记录数（有分页时）
  "message": string | null  // 响应消息
}
```

### 2. 字段命名规范
- **API响应**: 使用下划线命名 (snake_case): `user_id`, `birth_date`, `is_new_user`
- **请求数据**: 使用下划线命名 (snake_case): `device_id`, `birth_time`, `birth_location`

### 3. 错误响应格式
```javascript
{
  "success": false,
  "data": null,
  "message": "具体的错误信息"
}
```

---

## 🚀 基础配置

### 1. 基础URL配置
```javascript
// 配置基础URL
const API_BASE_URL = 'http://localhost:8000/api/v1'; // 开发环境
// const API_BASE_URL = 'https://your-domain.com/api/v1'; // 生产环境

// 通用请求配置
const requestConfig = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};
```

### 2. 通用请求函数
```javascript
// 通用GET请求 - 支持统一响应格式
async function apiGet(endpoint) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      ...requestConfig
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // 检查统一响应格式
    if (!result.success) {
      throw new Error(result.message || '请求失败');
    }
    
    return result; // 返回完整的响应对象，包含 success, data, message
  } catch (error) {
    console.error('API GET Error:', error);
    throw error;
  }
}

// 通用POST请求 - 支持统一响应格式
async function apiPost(endpoint, data) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      ...requestConfig,
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // 检查统一响应格式
    if (!result.success) {
      throw new Error(result.message || '请求失败');
    }
    
    return result; // 返回完整的响应对象，包含 success, data, message
  } catch (error) {
    console.error('API POST Error:', error);
    throw error;
  }
}
```

---

## 👤 用户管理功能

### 1. 检查用户状态
**功能描述**: 检查用户是否为新用户，获取用户基本信息

**接口调用**:
```javascript
// 检查用户状态 - 使用统一响应格式
async function checkUserStatus(deviceId) {
  try {
    const response = await apiGet(`/user/status?device_id=${deviceId}`);
    
    // response 已经通过 apiGet 验证了 success 状态
    return {
      isNewUser: response.data.is_new_user,
      userProfile: response.data.user_profile,
      hasBlueprint: response.data.has_blueprint
    };
  } catch (error) {
    console.error('检查用户状态失败:', error);
    throw error;
  }
}

// 使用示例
const userStatus = await checkUserStatus('device_unique_id');
if (userStatus.isNewUser) {
  // 显示新用户引导页面
  showNewUserOnboarding();
} else {
  // 直接进入主界面，可以访问用户信息
  enterMainApp(userStatus.userProfile);
}
```

**路由**: `GET /api/v1/user/status?device_id={deviceId}`

### 2. 创建新用户
**功能描述**: 新用户首次使用时创建用户档案

**接口调用**:
```javascript
// 创建新用户 - 使用统一响应格式
async function createUser(userData) {
  try {
    const requestData = {
      device_id: userData.deviceId,
      profile: {
        gender: userData.gender,
        birth_date: userData.birthDate,
        birth_time: userData.birthTime,
        birth_location: userData.birthLocation
      }
    };
    
    const response = await apiPost('/user/create', requestData);
    
    // response 已经通过 apiPost 验证了 success 状态
    return {
      userId: response.data.user_id,
      deviceId: response.data.device_id,
      profile: {
        gender: response.data.gender,
        birthDate: response.data.birth_date,
        birthTime: response.data.birth_time,
        birthLocation: response.data.birth_location
      },
      isNewUser: response.data.is_new_user,
      createdAt: response.data.created_at,
      message: response.message
    };
  } catch (error) {
    console.error('创建用户失败:', error);
    throw error;
  }
}

// 使用示例
const newUser = await createUser({
  deviceId: 'device_unique_id',
  gender: 'male',
  birthDate: '1990-08-15',
  birthTime: '10:30',
  birthLocation: '中国，四川省，成都市'
});

console.log('用户创建成功，ID:', newUser.userId);
console.log('创建时间:', newUser.createdAt);
```

**路由**: `POST /api/v1/user/create`

### 3. 更新用户信息
**功能描述**: 更新现有用户的信息

**接口调用**:
```javascript
// 更新用户信息
async function updateUser(userId, userData) {
  try {
    const requestData = {
      profile: {
        gender: userData.gender,
        birth_date: userData.birthDate,
        birth_time: userData.birthTime,
        birth_location: userData.birthLocation
      }
    };
    
    const response = await apiPost(`/user/${userId}`, requestData);
    
    if (response.success) {
      return response.data.message;
    } else {
      throw new Error(response.message || '更新用户信息失败');
    }
  } catch (error) {
    console.error('更新用户信息失败:', error);
    throw error;
  }
}
```

**路由**: `PUT /api/v1/user/{userId}`

---

## 🔮 Personal Blueprint 功能

### 1. 生成个人蓝图
**功能描述**: 基于用户出生信息生成算命结果和内在蓝图

**接口调用**:
```javascript
// 生成个人蓝图
async function generateBlueprint(userId, userProfile) {
  try {
    const requestData = {
      user_id: userId,
      user_profile: userProfile
    };
    
    const response = await apiPost('/blueprint/generate', requestData);
    
    if (response.success) {
      return {
        blueprintId: response.data._id,
        bazi: response.data.bazi,
        elementalProfile: response.data.elemental_profile,
        coreAnalysis: response.data.core_analysis,
        innerBlueprint: response.data.inner_blueprint
      };
    } else {
      throw new Error(response.message || '生成个人蓝图失败');
    }
  } catch (error) {
    console.error('生成个人蓝图失败:', error);
    throw error;
  }
}

// 使用示例
const blueprint = await generateBlueprint('user_123', {
  gender: 'male',
  birth_date: '1990-08-15',
  birth_time: '10:30',
  birth_location: '中国，四川省，成都市'
});

// 处理返回的数据
console.log('主导元素:', blueprint.coreAnalysis.dominant_element);
console.log('五行分布:', blueprint.elementalProfile);
console.log('核心本质:', blueprint.innerBlueprint.core_essence);
```

**路由**: `POST /api/v1/blueprint/generate`

### 2. 获取个人蓝图
**功能描述**: 获取用户的算命结果和内在蓝图

**接口调用**:
```javascript
// 获取个人蓝图
async function getBlueprint(userId) {
  try {
    const response = await apiGet(`/blueprint/${userId}`);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '获取个人蓝图失败');
    }
  } catch (error) {
    console.error('获取个人蓝图失败:', error);
    throw error;
  }
}

// 使用示例
const blueprint = await getBlueprint('user_123');

// 渲染五行分布图表
renderElementalChart(blueprint.elemental_profile);

// 渲染生命曲线
renderLifeJourneyCurve(blueprint.inner_blueprint.life_journey_curve);

// 显示核心本质
displayCoreEssence(blueprint.inner_blueprint.core_essence);
```

**路由**: `GET /api/v1/blueprint/{userId}`

### 3. 重新生成个人蓝图
**功能描述**: 重新生成用户的算命结果

**接口调用**:
```javascript
// 重新生成个人蓝图
async function regenerateBlueprint(userId, userProfile) {
  try {
    const requestData = {
      user_id: userId,
      user_profile: userProfile
    };
    
    const response = await apiPost(`/blueprint/${userId}/regenerate`, requestData);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '重新生成个人蓝图失败');
    }
  } catch (error) {
    console.error('重新生成个人蓝图失败:', error);
    throw error;
  }
}
```

**路由**: `POST /api/v1/blueprint/{userId}/regenerate`

---

## 🧭 Heart Compass 功能

### 1. 寻求指导
**功能描述**: 用户提问获取个性化指导

**接口调用**:
```javascript
// 寻求指导
async function seekGuidance(userId, question, userProfile) {
  try {
    const requestData = {
      user_id: userId,
      question: question,
      user_profile: userProfile
    };
    
    const response = await apiPost('/heart-compass/seek-guidance', requestData);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '获取指导失败');
    }
  } catch (error) {
    console.error('获取指导失败:', error);
    throw error;
  }
}

// 使用示例
const guidance = await seekGuidance('user_123', '如何平衡工作与生活？', {
  gender: 'male',
  birth_date: '1990-08-15',
  birth_time: '10:30',
  birth_location: '中国，四川省，成都市'
});

// 渲染指导内容
renderHexagram(guidance.hexagram);
renderDialogueFlow(guidance.dialogue_flow);
renderDeepWisdom(guidance.deep_wisdom);
renderActionGuide(guidance.action_guide);
renderDecisionProtocol(guidance.decision_protocol);
```

**路由**: `POST /api/v1/heart-compass/seek-guidance`

### 2. 重新提问
**功能描述**: 基于之前的指导进行深入探讨

**接口调用**:
```javascript
// 重新提问
async function askAgain(userId, question, previousGuidanceId = null) {
  try {
    const requestData = {
      user_id: userId,
      question: question,
      previous_guidance_id: previousGuidanceId
    };
    
    const response = await apiPost('/heart-compass/ask-again', requestData);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '重新提问失败');
    }
  } catch (error) {
    console.error('重新提问失败:', error);
    throw error;
  }
}

// 使用示例
const newGuidance = await askAgain(
  'user_123', 
  '能给我更具体的建议吗？', 
  'guidance_456'
);

// 显示新的指导内容
displayNewGuidance(newGuidance);
```

**路由**: `POST /api/v1/heart-compass/ask-again`

### 3. 获取指导历史
**功能描述**: 获取用户的指导历史记录

**接口调用**:
```javascript
// 获取指导历史 - 使用统一列表响应格式
async function getGuidanceHistory(userId, page = 1, limit = 10) {
  try {
    const response = await apiGet(`/heart-compass/${userId}/history?page=${page}&limit=${limit}`);
    
    // response 已经通过 apiGet 验证了 success 状态
    return {
      records: response.data,
      total: response.total,
      page: response.page,
      pageSize: response.page_size
    };
  } catch (error) {
    console.error('获取指导历史失败:', error);
    throw error;
  }
}

// 使用示例
const history = await getGuidanceHistory('user_123', 1, 10);

// 渲染历史记录列表
renderGuidanceHistory(history.records);

// 渲染分页组件
renderPagination({
  page: history.page,
  pageSize: history.pageSize,
  total: history.total,
  pages: Math.ceil(history.total / history.pageSize)
});
```

**路由**: `GET /api/v1/heart-compass/{userId}/history?page={page}&limit={limit}`

### 4. 获取特定指导记录
**功能描述**: 根据ID获取特定的指导记录

**接口调用**:
```javascript
// 获取特定指导记录
async function getGuidanceById(guidanceId) {
  try {
    const response = await apiGet(`/heart-compass/guidance/${guidanceId}`);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '获取指导记录失败');
    }
  } catch (error) {
    console.error('获取指导记录失败:', error);
    throw error;
  }
}
```

**路由**: `GET /api/v1/heart-compass/guidance/{guidanceId}`

---

## 🎯 Daily Fortune 功能

### 1. 生成每日运势
**功能描述**: 生成用户的每日运势

**接口调用**:
```javascript
// 生成每日运势
async function generateDailyFortune(userId, userProfile, date = null) {
  try {
    const requestData = {
      user_id: userId,
      user_profile: userProfile,
      date: date // 可选，默认为今天
    };
    
    const response = await apiPost('/daily-fortune/generate', requestData);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '生成每日运势失败');
    }
  } catch (error) {
    console.error('生成每日运势失败:', error);
    throw error;
  }
}

// 使用示例
const fortune = await generateDailyFortune('user_123', {
  gender: 'male',
  birth_date: '1990-08-15',
  birth_time: '10:30',
  birth_location: '中国，四川省，成都市'
}, '2024-05-20');

// 渲染运势内容
renderHexagram(fortune.hexagram);
renderTimeAdvice(fortune.time_advice);
renderLuckyElements(fortune.lucky_elements);
renderPersonalAdvice(fortune.personal_advice);
```

**路由**: `POST /api/v1/daily-fortune/generate`

### 2. 获取今日运势
**功能描述**: 获取用户今天的运势

**接口调用**:
```javascript
// 获取今日运势
async function getTodayFortune(userId) {
  try {
    const response = await apiGet(`/daily-fortune/${userId}/today`);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '获取今日运势失败');
    }
  } catch (error) {
    console.error('获取今日运势失败:', error);
    throw error;
  }
}

// 使用示例
const todayFortune = await getTodayFortune('user_123');

if (todayFortune) {
  // 显示今日运势
  displayTodayFortune(todayFortune);
} else {
  // 生成今日运势
  const newFortune = await generateDailyFortune('user_123', userProfile);
  displayTodayFortune(newFortune);
}
```

**路由**: `GET /api/v1/daily-fortune/{userId}/today`

### 3. 获取指定日期运势
**功能描述**: 获取用户指定日期的运势

**接口调用**:
```javascript
// 获取指定日期运势
async function getFortuneByDate(userId, date) {
  try {
    const response = await apiGet(`/daily-fortune/${userId}/date/${date}`);
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.message || '获取指定日期运势失败');
    }
  } catch (error) {
    console.error('获取指定日期运势失败:', error);
    throw error;
  }
}

// 使用示例
const fortune = await getFortuneByDate('user_123', '2024-05-19');

if (fortune) {
  // 显示指定日期运势
  displayFortuneByDate(fortune);
} else {
  // 生成指定日期运势
  const newFortune = await generateDailyFortune('user_123', userProfile, '2024-05-19');
  displayFortuneByDate(newFortune);
}
```

**路由**: `GET /api/v1/daily-fortune/{userId}/date/{date}`

### 4. 获取运势历史
**功能描述**: 获取用户的运势历史记录

**接口调用**:
```javascript
// 获取运势历史 - 使用统一列表响应格式
async function getFortuneHistory(userId, limit = 30) {
  try {
    const response = await apiGet(`/daily-fortune/${userId}/history?limit=${limit}`);
    
    // response 已经通过 apiGet 验证了 success 状态
    return {
      fortunes: response.data,
      total: response.total
    };
  } catch (error) {
    console.error('获取运势历史失败:', error);
    throw error;
  }
}

// 使用示例
const history = await getFortuneHistory('user_123', 30);

// 渲染运势历史列表
renderFortuneHistory(history.fortunes);

// 显示总数信息
console.log(`共有 ${history.total} 条运势记录`);
```

**路由**: `GET /api/v1/daily-fortune/{userId}/history?limit={limit}`

---

## ❌ 错误处理

### 1. 统一错误处理
```javascript
// 统一错误处理函数 - 支持统一响应格式
function handleApiError(error, context = '') {
  console.error(`${context} API错误:`, error);
  
  let userMessage = '操作失败，请稍后重试';
  
  // 优先使用API返回的错误信息
  if (error.message) {
    userMessage = error.message;
  } else if (error.status === 404) {
    userMessage = '请求的资源不存在';
  } else if (error.status === 500) {
    userMessage = '服务器内部错误';
  }
  
  // 显示用户友好的错误信息
  showErrorMessage(userMessage);
  
  // 返回统一的错误格式
  return {
    success: false,
    data: null,
    message: userMessage,
    error: error
  };
}

// 使用示例
try {
  const result = await generateBlueprint(userId, userProfile);
  return result;
} catch (error) {
  return handleApiError(error, '生成个人蓝图');
}
```

### 2. 网络错误处理
```javascript
// 网络错误处理
function handleNetworkError(error) {
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    showErrorMessage('网络连接失败，请检查网络设置');
  } else if (error.name === 'AbortError') {
    showErrorMessage('请求超时，请稍后重试');
  } else {
    showErrorMessage('网络错误，请稍后重试');
  }
}
```

---

## 🎯 最佳实践

### 1. 数据缓存策略
```javascript
// 简单的内存缓存
const cache = new Map();

function getCachedData(key) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) { // 5分钟缓存
    return cached.data;
  }
  return null;
}

function setCachedData(key, data) {
  cache.set(key, {
    data: data,
    timestamp: Date.now()
  });
}

// 使用缓存
async function getBlueprintWithCache(userId) {
  const cacheKey = `blueprint_${userId}`;
  const cached = getCachedData(cacheKey);
  
  if (cached) {
    return cached;
  }
  
  const data = await getBlueprint(userId);
  setCachedData(cacheKey, data);
  return data;
}
```

### 2. 加载状态管理
```javascript
// 加载状态管理
class LoadingManager {
  constructor() {
    this.loadingStates = new Map();
  }
  
  setLoading(key, loading) {
    this.loadingStates.set(key, loading);
    this.updateUI(key);
  }
  
  isLoading(key) {
    return this.loadingStates.get(key) || false;
  }
  
  updateUI(key) {
    const loading = this.isLoading(key);
    // 更新UI显示加载状态
    if (loading) {
      showLoadingSpinner(key);
    } else {
      hideLoadingSpinner(key);
    }
  }
}

const loadingManager = new LoadingManager();

// 使用加载状态
async function generateBlueprintWithLoading(userId, userProfile) {
  loadingManager.setLoading('blueprint', true);
  
  try {
    const result = await generateBlueprint(userId, userProfile);
    return result;
  } finally {
    loadingManager.setLoading('blueprint', false);
  }
}
```

### 3. 重试机制
```javascript
// 重试机制
async function apiCallWithRetry(apiCall, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      if (i === maxRetries - 1) {
        throw error;
      }
      
      // 等待后重试
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

// 使用重试机制
const result = await apiCallWithRetry(() => generateBlueprint(userId, userProfile));
```

### 4. 数据验证
```javascript
// 数据验证
function validateUserData(userData) {
  const errors = [];
  
  if (!userData.birthDate) {
    errors.push('出生日期不能为空');
  }
  
  if (!userData.birthTime) {
    errors.push('出生时间不能为空');
  }
  
  if (!userData.birthLocation) {
    errors.push('出生地点不能为空');
  }
  
  if (errors.length > 0) {
    throw new Error(errors.join('; '));
  }
  
  return true;
}

// 使用验证
try {
  validateUserData(userData);
  const result = await createUser(userData);
  return result;
} catch (error) {
  showErrorMessage(error.message);
}
```

---

## 📱 前端集成示例

### 1. React组件示例 - 支持统一响应格式
```jsx
import React, { useState, useEffect } from 'react';

function BlueprintGenerator({ userId, userProfile }) {
  const [blueprint, setBlueprint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateBlueprint = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await generateBlueprint(userId, userProfile);
      // response.data 包含实际的蓝图数据
      setBlueprint(response.data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateBlueprint();
  }, [userId, userProfile]);

  if (loading) return <div className="loading">生成中...</div>;
  if (error) return <div className="error">错误: {error}</div>;
  if (!blueprint) return <div className="no-data">暂无数据</div>;

  return (
    <div className="blueprint-container">
      <h2>个人蓝图</h2>
      <div className="core-analysis">
        主导元素: {blueprint.core_analysis.dominant_element}
      </div>
      <div className="elemental-profile">
        {/* 渲染五行分布图表 */}
        {Object.entries(blueprint.elemental_profile).map(([element, data]) => (
          <div key={element} className="element-item">
            <span>{element}: {data.strength}%</span>
          </div>
        ))}
      </div>
      {/* 渲染其他蓝图内容 */}
    </div>
  );
}
```

### 2. Vue组件示例 - 支持统一响应格式
```vue
<template>
  <div class="fortune-container">
    <div v-if="loading" class="loading">生成中...</div>
    <div v-else-if="error" class="error">错误: {{ error }}</div>
    <div v-else-if="fortune" class="fortune-content">
      <h2>今日运势</h2>
      <div class="hexagram-info">
        <div class="hexagram-name">卦象: {{ fortune.hexagram.name }}</div>
        <div class="luck-index">幸运指数: {{ fortune.hexagram.luck }}%</div>
      </div>
      <div class="time-advice">
        <h3>时段建议</h3>
        <div v-for="advice in fortune.time_advice" :key="advice.period" class="time-period">
          <strong>{{ advice.period }}</strong>
          <p>{{ advice.description }}</p>
        </div>
      </div>
      <!-- 渲染其他运势内容 -->
    </div>
  </div>
</template>

<script>
export default {
  props: {
    userId: {
      type: String,
      required: true
    }
  },
  
  data() {
    return {
      fortune: null,
      loading: false,
      error: null
    };
  },
  
  async mounted() {
    await this.loadTodayFortune();
  },
  
  methods: {
    async loadTodayFortune() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await getTodayFortune(this.userId);
        // response.data 包含实际的运势数据
        this.fortune = response.data;
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## 🔗 完整API路由列表

| 功能 | 方法 | 路由 | 描述 |
|------|------|------|------|
| 检查用户状态 | GET | `/user/status?device_id={deviceId}` | 检查用户是否为新用户 |
| 创建用户 | POST | `/user/create` | 创建新用户档案 |
| 更新用户 | PUT | `/user/{userId}` | 更新用户信息 |
| 生成蓝图 | POST | `/blueprint/generate` | 生成个人蓝图 |
| 获取蓝图 | GET | `/blueprint/{userId}` | 获取个人蓝图 |
| 重新生成蓝图 | POST | `/blueprint/{userId}/regenerate` | 重新生成个人蓝图 |
| 寻求指导 | POST | `/heart-compass/seek-guidance` | 获取Heart Compass指导 |
| 重新提问 | POST | `/heart-compass/ask-again` | 基于之前指导深入探讨 |
| 获取指导历史 | GET | `/heart-compass/{userId}/history` | 获取指导历史记录 |
| 获取特定指导 | GET | `/heart-compass/guidance/{guidanceId}` | 获取特定指导记录 |
| 生成运势 | POST | `/daily-fortune/generate` | 生成每日运势 |
| 获取今日运势 | GET | `/daily-fortune/{userId}/today` | 获取今日运势 |
| 获取指定日期运势 | GET | `/daily-fortune/{userId}/date/{date}` | 获取指定日期运势 |
| 获取运势历史 | GET | `/daily-fortune/{userId}/history` | 获取运势历史记录 |

---

## 📞 技术支持

如果在集成过程中遇到问题，请：

1. 检查网络连接和API地址配置
2. 查看浏览器控制台的错误信息
3. 确认请求参数格式是否正确
4. 检查后端服务是否正常运行
5. 参考后端API文档获取更多信息

---

**文档版本**: v1.2 (字段命名统一版本)  
**最后更新**: 2024年8月  
**适用版本**: Realm of Balance App Backend v1.2+ (支持snake_case字段命名和AI服务优化)

---

## 📝 更新日志

### v1.2 (2024年8月) - 字段命名统一版本
- ✅ **字段命名完全统一**: 所有API响应字段统一使用snake_case命名规范
- ✅ **代码示例全面更新**: 所有JavaScript示例代码适配最新的字段命名
- ✅ **组件示例更新**: React和Vue组件示例支持新的字段命名规范
- ✅ **API调用优化**: 更新所有API调用示例以反映实际测试结果
- ✅ **字段引用修复**: 修复blueprint、heart_compass、daily_fortune等模块的字段引用
- ✅ **AI服务配置优化**: Gemini API `maxOutputTokens`提升到8192，支持长提示词
- ✅ **个人蓝图提示词恢复**: 使用原版`blueprint.md`提示词，支持完整八字分析
- ✅ **错误处理增强**: 改进token限制检测和部分响应处理
- ✅ **性能优化**: 支持更复杂的AI生成任务，响应时间优化

### v1.1 (2024年8月) - 数据结构统一版本
- ✅ **统一响应格式**: 所有API使用`BaseResponse[T]`或`ListResponse[T]`统一格式
- ✅ **字段命名规范**: API响应统一使用snake_case命名
- ✅ **错误处理优化**: 统一的错误响应格式和处理机制
- ✅ **代码示例更新**: 所有JavaScript示例代码适配新的响应格式
- ✅ **组件示例优化**: React和Vue组件示例支持新的数据结构
- ✅ **类型安全**: 响应数据结构更加规范和可预测

### v1.0 (2024年) - 初始版本
- 基础API集成指南
- 用户管理、个人蓝图、Heart Compass、Daily Fortune功能
- 基础错误处理和最佳实践
