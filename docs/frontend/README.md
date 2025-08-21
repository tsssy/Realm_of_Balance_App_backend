# 前端集成和API调用指南

## 📋 概述

本目录包含 Realm of Balance App 前端开发指南、API 集成说明和前端技术实现相关的所有文档。

## 📁 目录结构

```
frontend/
├── README.md                           # 本文件 - 前端集成说明
└── FRONTEND_API_INTEGRATION_GUIDE.md  # 详细的前端API集成指南
```

## 🚀 快速开始

### 技术栈推荐

- **框架**: React 18+ / Vue 3+ / Next.js / Nuxt.js
- **状态管理**: Redux Toolkit / Zustand / Pinia
- **HTTP 客户端**: Axios / Fetch API / React Query
- **UI 组件库**: Ant Design / Element Plus / Material-UI
- **构建工具**: Vite / Webpack / Create React App

### 项目初始化

```bash
# React 项目
npx create-react-app realm-balance-frontend
cd realm-balance-frontend

# Vue 项目
npm create vue@latest realm-balance-frontend
cd realm-balance-frontend

# 安装依赖
npm install axios
npm install @tanstack/react-query  # React Query
npm install pinia                  # Vue 状态管理
```

## 🔌 API 集成

### 基础配置

```javascript
// api/config.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
};
```

### HTTP 客户端设置

```javascript
// api/client.js
import axios from 'axios';
import { API_CONFIG } from './config';

const apiClient = axios.create(API_CONFIG);

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 统一错误处理
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // 处理未授权错误
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

## 📱 核心功能集成

### 1. 用户管理

#### 用户状态检查

```javascript
// hooks/useUser.js
import { useState, useEffect } from 'react';
import apiClient from '../api/client';

export const useUser = (deviceId) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkUserStatus = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/user/status?device_id=${deviceId}`);
      setUser(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (deviceId) {
      checkUserStatus();
    }
  }, [deviceId]);

  return { user, loading, error, refetch: checkUserStatus };
};
```

#### 用户创建

```javascript
// services/userService.js
import apiClient from '../api/client';

export const createUser = async (userData) => {
  try {
    const response = await apiClient.post('/user/create', userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '创建用户失败');
  }
};

export const updateUser = async (userId, userData) => {
  try {
    const response = await apiClient.put(`/user/${userId}`, userData);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '更新用户失败');
  }
};
```

### 2. 算命分析

#### 生成个人蓝图

```javascript
// services/blueprintService.js
import apiClient from '../api/client';

export const generateBlueprint = async (userId, birthInfo) => {
  try {
    const response = await apiClient.post('/blueprint/generate', {
      user_id: userId,
      birth_info: birthInfo,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '生成蓝图失败');
  }
};

export const getBlueprint = async (userId) => {
  try {
    const response = await apiClient.get(`/blueprint/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '获取蓝图失败');
  }
};
```

#### 蓝图展示组件

```jsx
// components/BlueprintDisplay.jsx
import React, { useState, useEffect } from 'react';
import { getBlueprint } from '../services/blueprintService';

const BlueprintDisplay = ({ userId }) => {
  const [blueprint, setBlueprint] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBlueprint = async () => {
      try {
        const data = await getBlueprint(userId);
        setBlueprint(data);
      } catch (error) {
        console.error('获取蓝图失败:', error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchBlueprint();
    }
  }, [userId]);

  if (loading) return <div>加载中...</div>;
  if (!blueprint) return <div>暂无蓝图数据</div>;

  return (
    <div className="blueprint-display">
      <h2>个人蓝图</h2>
      <div className="birth-info">
        <h3>出生信息</h3>
        <p>出生日期: {blueprint.birth_info.date}</p>
        <p>出生时间: {blueprint.birth_info.time}</p>
      </div>
      <div className="analysis-result">
        <h3>分析结果</h3>
        <div dangerouslySetInnerHTML={{ __html: blueprint.analysis_result.html }} />
      </div>
    </div>
  );
};

export default BlueprintDisplay;
```

### 3. Heart Compass 指导

#### 寻求指导

```javascript
// services/heartCompassService.js
import apiClient from '../api/client';

export const seekGuidance = async (userId, situation) => {
  try {
    const response = await apiClient.post('/heart-compass/seek-guidance', {
      user_id: userId,
      situation: situation,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '寻求指导失败');
  }
};

export const getGuidanceHistory = async (userId) => {
  try {
    const response = await apiClient.get(`/heart-compass/${userId}/history`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '获取指导历史失败');
  }
};
```

#### 指导界面组件

```jsx
// components/HeartCompass.jsx
import React, { useState } from 'react';
import { seekGuidance } from '../services/heartCompassService';

const HeartCompass = ({ userId }) => {
  const [situation, setSituation] = useState('');
  const [guidance, setGuidance] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSeekGuidance = async () => {
    if (!situation.trim()) {
      alert('请描述您当前的情境');
      return;
    }

    try {
      setLoading(true);
      const data = await seekGuidance(userId, situation);
      setGuidance(data);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="heart-compass">
      <h2>Heart Compass 指导</h2>
      <div className="situation-input">
        <textarea
          value={situation}
          onChange={(e) => setSituation(e.target.value)}
          placeholder="请描述您当前面临的情境或问题..."
          rows={4}
        />
        <button 
          onClick={handleSeekGuidance} 
          disabled={loading}
        >
          {loading ? '寻求指导中...' : '寻求指导'}
        </button>
      </div>

      {guidance && (
        <div className="guidance-result">
          <h3>易经指导</h3>
          <div className="guidance-content">
            <div className="situation-understanding">
              <h4>情境理解</h4>
              <p>{guidance.situation_understanding}</p>
            </div>
            <div className="iching-wisdom">
              <h4>易经智慧</h4>
              <p>{guidance.iching_wisdom}</p>
            </div>
            <div className="decision-guidance">
              <h4>决策指导</h4>
              <p>{guidance.decision_guidance}</p>
            </div>
            <div className="action-protocol">
              <h4>行动协议</h4>
              <p>{guidance.action_protocol}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HeartCompass;
```

### 4. 每日运势

#### 运势生成

```javascript
// services/dailyFortuneService.js
import apiClient from '../api/client';

export const generateDailyFortune = async (userId) => {
  try {
    const response = await apiClient.post('/daily-fortune/generate', {
      user_id: userId,
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '生成运势失败');
  }
};

export const getTodayFortune = async (userId) => {
  try {
    const response = await apiClient.get(`/daily-fortune/${userId}/today`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.error?.message || '获取今日运势失败');
  }
};
```

#### 运势展示组件

```jsx
// components/DailyFortune.jsx
import React, { useState, useEffect } from 'react';
import { getTodayFortune, generateDailyFortune } from '../services/dailyFortuneService';

const DailyFortune = ({ userId }) => {
  const [fortune, setFortune] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchTodayFortune = async () => {
    try {
      const data = await getTodayFortune(userId);
      setFortune(data);
    } catch (error) {
      console.error('获取今日运势失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateFortune = async () => {
    try {
      setLoading(true);
      const data = await generateDailyFortune(userId);
      setFortune(data);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchTodayFortune();
    }
  }, [userId]);

  if (loading) return <div>加载中...</div>;

  return (
    <div className="daily-fortune">
      <h2>今日运势</h2>
      
      {fortune ? (
        <div className="fortune-content">
          <div className="overall-fortune">
            <h3>整体运势</h3>
            <p>{fortune.overall_fortune}</p>
          </div>
          
          <div className="time-advice">
            <h3>时段建议</h3>
            <div className="time-slots">
              <div className="morning">
                <h4>早晨 (6:00-12:00)</h4>
                <p>{fortune.morning_advice}</p>
              </div>
              <div className="afternoon">
                <h4>下午 (12:00-18:00)</h4>
                <p>{fortune.afternoon_advice}</p>
              </div>
              <div className="evening">
                <h4>晚上 (18:00-24:00)</h4>
                <p>{fortune.evening_advice}</p>
              </div>
            </div>
          </div>
          
          <div className="lucky-elements">
            <h3>幸运元素</h3>
            <div className="elements-grid">
              <div className="lucky-color">
                <span>幸运颜色:</span> {fortune.lucky_color}
              </div>
              <div className="lucky-direction">
                <span>幸运方向:</span> {fortune.lucky_direction}
              </div>
              <div className="lucky-number">
                <span>幸运数字:</span> {fortune.lucky_number}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="no-fortune">
          <p>今日还未生成运势</p>
          <button onClick={handleGenerateFortune}>
            生成今日运势
          </button>
        </div>
      )}
    </div>
  );
};

export default DailyFortune;
```

## 🎨 UI/UX 设计

### 设计原则

1. **简洁明了**: 界面简洁，信息层次清晰
2. **响应式设计**: 支持各种设备尺寸
3. **一致性**: 保持设计风格和交互方式的一致性
4. **可访问性**: 考虑不同用户的使用需求

### 组件库集成

```javascript
// 使用 Ant Design (React)
import { Button, Input, Card, Spin, message } from 'antd';

// 使用 Element Plus (Vue)
import { ElButton, ElInput, ElCard, ElLoading, ElMessage } from 'element-plus';
```

### 主题定制

```css
/* 自定义主题变量 */
:root {
  --primary-color: #1890ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #f5222d;
  --font-size-base: 14px;
  --border-radius-base: 6px;
}

/* 响应式断点 */
@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }
}
```

## 📱 移动端适配

### 响应式布局

```css
/* 移动端优先的响应式设计 */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

@media (min-width: 768px) {
  .container {
    padding: 0 24px;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 0 32px;
  }
}
```

### 触摸优化

```css
/* 触摸友好的按钮尺寸 */
.button {
  min-height: 44px;
  min-width: 44px;
  touch-action: manipulation;
}

/* 防止双击缩放 */
* {
  touch-action: manipulation;
}
```

## 🔐 安全考虑

### 数据验证

```javascript
// 前端数据验证
const validateUserInput = (data) => {
  const errors = {};
  
  if (!data.name || data.name.trim().length < 2) {
    errors.name = '姓名至少需要2个字符';
  }
  
  if (!data.birth_date) {
    errors.birth_date = '请选择出生日期';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
```

### XSS 防护

```javascript
// 安全的HTML渲染
const SafeHTML = ({ html }) => {
  // 使用 DOMPurify 等库清理HTML
  const cleanHTML = DOMPurify.sanitize(html);
  
  return (
    <div 
      dangerouslySetInnerHTML={{ __html: cleanHTML }}
      className="safe-html"
    />
  );
};
```

## 🧪 测试策略

### 单元测试

```javascript
// 使用 Jest 和 React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { useUser } from '../hooks/useUser';

test('用户状态检查', async () => {
  render(<UserComponent />);
  
  expect(screen.getByText('加载中...')).toBeInTheDocument();
  
  // 等待异步操作完成
  await screen.findByText('用户信息');
});
```

### 集成测试

```javascript
// API 集成测试
import { createUser } from '../services/userService';

test('创建用户', async () => {
  const userData = {
    device_id: 'test-device-123',
    name: '测试用户',
    birth_date: '1990-01-01',
  };
  
  const result = await createUser(userData);
  expect(result.success).toBe(true);
  expect(result.data.name).toBe('测试用户');
});
```

## 📚 相关文档

- [API 接口文档](../api/README.md)
- [后端实现指南](../backend/BACKEND_IMPLEMENTATION_GUIDE.md)
- [业务流程说明](../business/BUSINESS_FLOW.md)
- [测试指南](../testing/TESTING_GUIDE.md)
- [环境配置指南](../setup/README.md)

## 💡 最佳实践

### 1. 性能优化

- **代码分割**: 使用动态导入减少初始包大小
- **懒加载**: 图片和组件懒加载
- **缓存策略**: 合理使用浏览器缓存和内存缓存
- **虚拟滚动**: 长列表使用虚拟滚动

### 2. 用户体验

- **加载状态**: 提供清晰的加载反馈
- **错误处理**: 友好的错误提示和恢复建议
- **离线支持**: 实现基本的离线功能
- **动画效果**: 适当的动画提升交互体验

### 3. 代码质量

- **类型检查**: 使用 TypeScript 或 PropTypes
- **代码规范**: 遵循 ESLint 和 Prettier 规范
- **组件设计**: 可复用和可维护的组件设计
- **状态管理**: 合理的数据流和状态管理

## 🚨 常见问题

### 1. CORS 错误

```javascript
// 后端需要配置 CORS
// 前端检查请求配置
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // 如果需要发送 cookies
});
```

### 2. 认证问题

```javascript
// 检查 token 格式和过期时间
const token = localStorage.getItem('auth_token');
if (token && isTokenExpired(token)) {
  localStorage.removeItem('auth_token');
  // 重定向到登录页
}
```

### 3. 数据格式问题

```javascript
// 统一数据格式处理
const normalizeResponse = (response) => {
  if (response.success) {
    return response.data;
  } else {
    throw new Error(response.error?.message || '请求失败');
  }
};
```

## 📞 支持

如有前端集成问题，请：
1. 查看 API 接口文档
2. 检查网络请求和响应
3. 查看浏览器控制台错误
4. 联系前端开发团队
