# Realm of Balance App 前端API集成指南

## 概述

本文档指导前端如何调用后端API实现新用户流程，包括用户信息收集、五行计算、个人蓝图生成等核心功能。

## 新用户流程概览

```
欢迎页面 → 出生时间收集 → 出生地点和性别收集 → 五行计算 → 个人特质分析 → 人生指导
   ↓              ↓              ↓              ↓          ↓          ↓
Begin Journey → 出生时间表单 → 地点性别表单 → 五行结果 → 性格洞察 → 生活指导
```

## API基础信息

- **Base URL**: `http://localhost:8000` (开发环境)
- **API Version**: `/api/v1`
- **Content-Type**: `application/json`
- **认证方式**: 基于设备ID的用户识别

## 1. 用户状态检查

### 接口信息
- **URL**: `GET /api/v1/user/status`
- **用途**: 检查用户是否为新用户，决定流程走向
- **参数**: `device_id` (查询参数或请求头)

### 请求示例

#### 方式1: 查询参数
```javascript
// 检查用户状态
const checkUserStatus = async (deviceId) => {
  try {
    const response = await fetch(`/api/v1/user/status?device_id=${deviceId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('检查用户状态失败:', error);
    throw error;
  }
};
```

#### 方式2: 请求头
```javascript
// 检查用户状态（使用请求头）
const checkUserStatusWithHeader = async (deviceId) => {
  try {
    const response = await fetch('/api/v1/user/status', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Device-ID': deviceId
      }
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('检查用户状态失败:', error);
    throw error;
  }
};
```

### 响应格式
```json
{
  "success": true,
  "data": {
    "is_new_user": true,
    "user_profile": null,
    "has_blueprint": false
  },
  "message": null,
  "timestamp": "2024-12-19T10:30:00"
}
```

### 前端处理逻辑
```javascript
// 处理用户状态检查结果
const handleUserStatusCheck = (result) => {
  if (result.success) {
    const { is_new_user, user_profile, has_blueprint } = result.data;
    
    if (is_new_user) {
      // 新用户：显示出生时间收集页面
      showBirthTimeForm();
    } else {
      // 老用户：直接进入主应用
      // 无论是否有算命结果，老用户都直接进入主应用
      // 如果没有算命结果，可以在主应用中提示重新生成
      enterApp();
    }
  }
};
```

## 2. 创建新用户

### 接口信息
- **URL**: `POST /api/v1/user/create`
- **用途**: 创建新用户，收集出生时间、地点、性别等信息
- **参数**: 用户基本信息

### 请求示例
```javascript
// 创建新用户
const createUser = async (deviceId, userProfile) => {
  try {
    const response = await fetch('/api/v1/user/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        device_id: deviceId,
        profile: {
          gender: userProfile.gender,           // 'male', 'female', 'other'
          birth_date: userProfile.birthDate,   // 'YYYY-MM-DD'
          birth_time: userProfile.birthTime,   // 'HH:MM'
          birth_location: userProfile.birthLocation
        }
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('创建用户失败:', error);
    throw error;
  }
};
```

### 请求数据格式
```json
{
  "device_id": "device_123456",
  "profile": {
    "gender": "male",
    "birth_date": "1990-01-01",
    "birth_time": "12:00",
    "birth_location": "北京, 北京, 中国"
  }
}
```

### 响应格式
```json
{
  "success": true,
  "data": {
    "user_id": "user_123456",
    "device_id": "device_123456",
    "gender": "male",
    "birth_date": "1990-01-01",
    "birth_time": "12:00",
    "birth_location": "北京, 北京, 中国",
    "is_new_user": true,
    "created_at": "2024-12-19T10:30:00",
    "updated_at": "2024-12-19T10:30:00",
    "last_login_at": null
  },
  "message": null,
  "timestamp": "2024-12-19T10:30:00"
}
```

## 3. 快速生成五行结果

### 接口信息
- **URL**: `POST /api/v1/blueprint/quick`
- **用途**: 快速计算用户五行分布（5-8秒内返回）
- **参数**: 用户ID和用户信息

### 请求示例
```javascript
// 快速生成五行结果
const generateQuickBlueprint = async (userId, userProfile) => {
  try {
    const response = await fetch('/api/v1/blueprint/quick', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        user_profile: userProfile
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('快速生成五行结果失败:', error);
    throw error;
  }
};
```

### 请求数据格式
```json
{
  "user_id": "user_123456",
  "user_profile": {
    "gender": "male",
    "birth_date": "1990-01-01",
    "birth_time": "12:00",
    "birth_location": "北京, 北京, 中国"
  }
}
```

### 响应格式
```json
{
  "success": true,
  "data": {
    "user_id": "user_123456",
    "generation_status": "partial",
    "quick_data": {
      "elemental_profile": {
        "metal": {
          "strength": 17,
          "characteristics": ["Precision", "Logic"]
        },
        "wood": {
          "strength": 16,
          "characteristics": ["Growth", "Creativity"]
        },
        "water": {
          "strength": 22,
          "characteristics": ["Intuition", "Adaptability"]
        },
        "fire": {
          "strength": 22,
          "characteristics": ["Passion", "Leadership"]
        },
        "earth": {
          "strength": 23,
          "characteristics": ["Stability", "Nurturing"]
        }
      },
      "dominant_element": "Earth",
      "dominant_percentage": 23
    },
    "created_at": "2024-12-19T10:30:00",
    "updated_at": "2024-12-19T10:30:00"
  },
  "message": "五行结果快速生成成功",
  "timestamp": "2024-12-19T10:30:00"
}
```

## 4. 生成完整蓝图

### 接口信息
- **URL**: `POST /api/v1/blueprint/complete`
- **用途**: 基于五行结果生成完整的个人特质分析报告
- **参数**: 用户ID和用户信息

### 请求示例
```javascript
// 生成完整蓝图
const generateCompleteBlueprint = async (userId, userProfile) => {
  try {
    const response = await fetch('/api/v1/blueprint/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        user_profile: userProfile
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('生成完整蓝图失败:', error);
    throw error;
  }
};
```

### 响应格式（完整蓝图）
```json
{
  "success": true,
  "data": {
    "user_id": "user_123456",
    "generation_status": "complete",
    "elemental_profile": {
      "metal": {
        "strength": 17,
        "characteristics": ["Precision", "Logic"]
      },
      "wood": {
        "strength": 16,
        "characteristics": ["Growth", "Creativity"]
      },
      "water": {
        "strength": 22,
        "characteristics": ["Intuition", "Adaptability"]
      },
      "fire": {
        "strength": 22,
        "characteristics": ["Passion", "Leadership"]
      },
      "earth": {
        "strength": 23,
        "characteristics": ["Stability", "Nurturing"]
      }
    },
    "inner_blueprint": {
      "core_essence": {
        "title": "Core Essence",
        "description": "You are stable and reliable like the earth itself, serving as a solid foundation for others. You possess an inclusive nature and the perseverance to achieve your dreams."
      },
      "natural_strengths": {
        "title": "Natural Strengths",
        "strengths": [
          "Strong sense of responsibility",
          "Stable and reliable",
          "Great at caring for others",
          "Strong practical execution"
        ]
      },
      "growth_areas": {
        "title": "Growth Areas",
        "analysis": "Your Earth element is dominant, but you may need to balance it with other elements.",
        "balance_path": {
          "title": "Balance Path",
          "suggestions": [
            "Sometimes too conservative",
            "Need more adventurous spirit",
            "May take on too much responsibility"
          ]
        }
      },
      "life_journey_curve": {
        "title": "Life Journey Curve",
        "description": "Your life path combines the Stability of Earth with the Passion of Fire, creating unique life value.",
        "chart_data": [
          {
            "year": 2024,
            "energy_level": 85,
            "is_turning_point": true,
            "icon_id": "mountain",
            "event_description": "Year of foundation building"
          }
        ]
      }
    },
    "created_at": "2024-12-19T10:30:00",
    "updated_at": "2024-12-19T10:30:00"
  },
  "message": "完整蓝图生成成功",
  "timestamp": "2024-12-19T10:30:00"
}
```

## 5. 完整的新用户流程实现

### 前端流程控制
```javascript
class NewUserFlow {
  constructor() {
    this.deviceId = this.generateDeviceId();
    this.currentStep = 'welcome';
    this.userData = {};
  }

  // 生成设备ID
  generateDeviceId() {
    let deviceId = localStorage.getItem('device_id');
    if (!deviceId) {
      deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('device_id', deviceId);
    }
    return deviceId;
  }

  // 开始新用户流程
  async startFlow() {
    try {
      // 1. 检查用户状态
      const statusResult = await this.checkUserStatus();
      
      if (statusResult.data.is_new_user) {
        // 新用户：显示出生时间收集页面
        this.showBirthTimeForm();
      } else {
        // 老用户：直接进入主应用
        // 无论是否有算命结果，老用户都直接进入主应用
        this.enterApp();
      }
    } catch (error) {
      console.error('启动流程失败:', error);
      this.showError('启动失败，请重试');
    }
  }

  // 步骤1: 收集出生时间
  async handleBirthTimeSubmit(birthTimeData) {
    try {
      this.userData.birthTime = birthTimeData;
      this.currentStep = 'location_gender';
      this.showLocationGenderForm();
  } catch (error) {
      console.error('处理出生时间失败:', error);
      this.showError('保存出生时间失败，请重试');
    }
  }

  // 步骤2: 收集出生地点和性别
  async handleLocationGenderSubmit(locationGenderData) {
    try {
      // 合并用户数据
      const userProfile = {
        ...this.userData.birthTime,
        ...locationGenderData
      };

      // 创建用户
      const createResult = await createUser(this.deviceId, userProfile);
      
      if (createResult.success) {
        this.userData.userId = createResult.data.user_id;
        this.userData.userProfile = userProfile;
        
        // 进入五行计算步骤
        this.currentStep = 'calculating';
        this.showCalculatingScreen();
        
        // 开始计算五行
        await this.calculateElements();
      } else {
        throw new Error(createResult.message || '创建用户失败');
      }
    } catch (error) {
      console.error('处理地点性别信息失败:', error);
      this.showError('保存用户信息失败，请重试');
    }
  }

  // 步骤3: 计算五行
  async calculateElements() {
    try {
      // 快速生成五行结果
      const quickResult = await generateQuickBlueprint(
        this.userData.userId, 
        this.userData.userProfile
      );

      if (quickResult.success) {
        this.userData.quickBlueprint = quickResult.data;
        
        // 显示五行结果页面
        this.currentStep = 'elements_result';
        this.showElementsResult(quickResult.data);
    } else {
        throw new Error(quickResult.message || '计算五行失败');
    }
  } catch (error) {
      console.error('计算五行失败:', error);
      this.showError('计算失败，请重试');
    }
  }

  // 步骤4: 生成完整蓝图
  async generateCompleteBlueprint() {
    try {
      this.currentStep = 'generating';
      this.showGeneratingScreen();

      // 生成完整蓝图
      const completeResult = await generateCompleteBlueprint(
        this.userData.userId, 
        this.userData.userProfile
      );

      if (completeResult.success) {
        this.userData.completeBlueprint = completeResult.data;
        
        // 显示个人特质分析页面
        this.currentStep = 'personality_insights';
        this.showPersonalityInsights(completeResult.data);
    } else {
        throw new Error(completeResult.message || '生成完整蓝图失败');
    }
  } catch (error) {
      console.error('生成完整蓝图失败:', error);
      this.showError('生成失败，请重试');
    }
  }

  // 步骤5: 显示人生指导
  showLifeGuidance() {
    this.currentStep = 'life_guidance';
    const blueprint = this.userData.completeBlueprint;
    
    // 显示人生指导页面
    this.showLifeGuidancePage(blueprint);
  }

  // 进入应用
  enterApp() {
    this.currentStep = 'app';
    // 跳转到主应用页面
    window.location.href = '/app';
  }

  // 显示错误信息
  showError(message) {
    // 实现错误提示UI
    console.error(message);
  }
}
```

### 页面组件示例

#### 出生时间收集页面
```javascript
// BirthTimeForm.js
class BirthTimeForm {
  constructor(onSubmit) {
    this.onSubmit = onSubmit;
    this.init();
  }

  init() {
    this.render();
    this.bindEvents();
  }

  render() {
    const container = document.getElementById('birth-time-form');
    container.innerHTML = `
      <div class="form-card">
        <h2>When were you born?</h2>
        
        <div class="form-group">
          <label>Birth Date</label>
          <div class="date-inputs">
            <input type="text" placeholder="MONTH" id="month" maxlength="2">
            <span>/</span>
            <input type="text" placeholder="DAY" id="day" maxlength="2">
            <span>/</span>
            <input type="text" placeholder="YEAR" id="year" maxlength="4">
          </div>
        </div>

        <div class="form-group">
          <label>Time of Birth (Optional)</label>
          <input type="time" id="birth-time">
          <a href="#" class="help-link">what if i don't know my birth time?</a>
        </div>

        <div class="time-periods">
          <h3>Or select a time period:</h3>
          <div class="period-grid">
            <div class="period-card" data-period="morning">
              <div class="period-icon">🌅</div>
              <div class="period-name">Morning</div>
              <div class="period-time">5:00 AM - 12:00 PM</div>
            </div>
            <div class="period-card" data-period="afternoon">
              <div class="period-icon">☀️</div>
              <div class="period-name">Afternoon</div>
              <div class="period-time">12:00 PM - 5:00 PM</div>
            </div>
            <div class="period-card" data-period="evening">
              <div class="period-icon">🌄</div>
              <div class="period-name">Evening</div>
              <div class="period-time">5:00 PM - 9:00 PM</div>
            </div>
            <div class="period-card" data-period="night">
              <div class="period-icon">🌙</div>
              <div class="period-name">Night</div>
              <div class="period-time">9:00 PM - 5:00 AM</div>
            </div>
          </div>
        </div>

        <button class="continue-btn" id="continue-btn">Continue Journey</button>
        
        <div class="progress-dots">
          <span class="dot active"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    `;
  }

  bindEvents() {
    // 时间周期选择
    document.querySelectorAll('.period-card').forEach(card => {
      card.addEventListener('click', (e) => {
        document.querySelectorAll('.period-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        
        // 设置时间范围
        const period = card.dataset.period;
        this.setTimePeriod(period);
      });
    });

    // 继续按钮
    document.getElementById('continue-btn').addEventListener('click', () => {
      this.handleSubmit();
    });
  }

  setTimePeriod(period) {
    const timeMap = {
      morning: '08:00',
      afternoon: '14:00',
      evening: '19:00',
      night: '23:00'
    };
    
    document.getElementById('birth-time').value = timeMap[period];
  }

  handleSubmit() {
    const month = document.getElementById('month').value;
    const day = document.getElementById('day').value;
    const year = document.getElementById('year').value;
    const birthTime = document.getElementById('birth-time').value;

    if (!month || !day || !year) {
      this.showError('请填写完整的出生日期');
      return;
    }

    const birthDate = `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    
    const birthTimeData = {
      birth_date: birthDate,
      birth_time: birthTime || '12:00' // 如果没有选择时间，默认中午12点
    };

    this.onSubmit(birthTimeData);
  }

  showError(message) {
    // 显示错误提示
    console.error(message);
  }
}
```

#### 出生地点和性别收集页面
```javascript
// LocationGenderForm.js
class LocationGenderForm {
  constructor(onSubmit) {
    this.onSubmit = onSubmit;
    this.init();
  }

  init() {
    this.render();
    this.bindEvents();
  }

  render() {
    const container = document.getElementById('location-gender-form');
    container.innerHTML = `
      <div class="form-card">
        <h2>Where were you born?</h2>
        
        <div class="form-group">
          <label>Birth Location</label>
          <input type="text" id="birth-location" placeholder="e.g., New York, NY, USA">
          <p class="help-text">Enter city, state/province, and country. The more specific, the more precise your celestial coordinates.</p>
        </div>

        <div class="form-group">
          <label>Gender</label>
          <select id="gender">
            <option value="">Select your gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>

        <button class="complete-btn" id="complete-btn">Complete Blueprint</button>
        
        <div class="progress-dots">
          <span class="dot"></span>
          <span class="dot active"></span>
          <span class="dot"></span>
        </div>
      </div>
    `;
  }

  bindEvents() {
    document.getElementById('complete-btn').addEventListener('click', () => {
      this.handleSubmit();
    });
  }

  handleSubmit() {
    const birthLocation = document.getElementById('birth-location').value;
    const gender = document.getElementById('gender').value;

    if (!birthLocation || !gender) {
      this.showError('请填写完整信息');
      return;
    }

    const locationGenderData = {
      birth_location: birthLocation,
      gender: gender
    };

    this.onSubmit(locationGenderData);
  }

  showError(message) {
    console.error(message);
  }
}
```

#### 五行结果展示页面
```javascript
// ElementsResultPage.js
class ElementsResultPage {
  constructor(blueprintData, onNext) {
    this.blueprintData = blueprintData;
    this.onNext = onNext;
    this.init();
  }

  init() {
    this.render();
    this.bindEvents();
  }

  render() {
    const container = document.getElementById('elements-result');
    const { elemental_profile, dominant_element } = this.blueprintData.quick_data;
    
    container.innerHTML = `
      <div class="result-card">
        <h2>Your Elemental Essence</h2>
        
        <div class="elements-breakdown">
          ${Object.entries(elemental_profile).map(([element, data]) => `
            <div class="element-row">
              <div class="element-info">
                <div class="element-icon ${element}">${this.getElementSymbol(element)}</div>
                <div class="element-name">${this.getElementName(element)} ${this.getElementChinese(element)}</div>
              </div>
              <div class="element-percentage">${data.strength}%</div>
              <div class="element-bar">
                <div class="bar-fill ${element}" style="width: ${data.strength}%"></div>
              </div>
              <div class="element-characteristics">
                ${data.characteristics.map(char => `<span class="characteristic-tag">${char}</span>`).join('')}
              </div>
            </div>
          `).join('')}
        </div>

        <div class="summary-section">
          <div class="dominant-element">
            ✨ Dominant Element: ${dominant_element} (${elemental_profile[dominant_element.toLowerCase()].strength}%)
          </div>
          <div class="total">Total: 100%</div>
        </div>

        <button class="next-btn" id="next-btn">Next</button>
        
        <div class="progress-dots">
          <span class="dot active"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    `;
  }

  getElementSymbol(element) {
    const symbols = {
      earth: '土',
      fire: '火',
      water: '水',
      metal: '金',
      wood: '木'
    };
    return symbols[element] || element;
  }

  getElementName(element) {
    return element.charAt(0).toUpperCase() + element.slice(1);
  }

  getElementChinese(element) {
    const chinese = {
      earth: '土',
      fire: '火',
      water: '水',
      metal: '金',
      wood: '木'
    };
    return chinese[element] || '';
  }

  bindEvents() {
    document.getElementById('next-btn').addEventListener('click', () => {
      this.onNext();
    });
  }
}
```

## 6. 错误处理和重试机制

### 错误处理策略
```javascript
class ErrorHandler {
  static async handleApiError(error, retryCount = 0, maxRetries = 3) {
    if (retryCount >= maxRetries) {
      throw new Error(`请求失败，已重试${maxRetries}次: ${error.message}`);
    }

    // 网络错误或5xx错误，尝试重试
    if (error.status >= 500 || error.name === 'TypeError') {
      console.warn(`API请求失败，${retryCount + 1}/${maxRetries}次重试:`, error);
      
      // 指数退避重试
      const delay = Math.pow(2, retryCount) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
      
      return retryCount + 1;
    }

    // 4xx错误，不重试
    throw error;
  }

  static showUserFriendlyError(error) {
    let message = '操作失败，请重试';
    
    if (error.status === 400) {
      message = '请求参数错误，请检查输入';
    } else if (error.status === 404) {
      message = '请求的资源不存在';
    } else if (error.status === 500) {
      message = '服务器内部错误，请稍后重试';
    } else if (error.status === 0) {
      message = '网络连接失败，请检查网络';
    }

    // 显示错误提示UI
    this.showErrorToast(message);
  }

  static showErrorToast(message) {
    // 实现错误提示UI
    console.error(message);
  }
}
```

### 重试机制示例
```javascript
// 带重试的API调用
const apiCallWithRetry = async (apiFunction, ...args) => {
  let retryCount = 0;
  const maxRetries = 3;

  while (retryCount <= maxRetries) {
    try {
      return await apiFunction(...args);
  } catch (error) {
      retryCount = await ErrorHandler.handleApiError(error, retryCount, maxRetries);
      
      if (retryCount > maxRetries) {
        ErrorHandler.showUserFriendlyError(error);
    throw error;
  }
}
  }
};

// 使用重试机制
const createUserWithRetry = async (deviceId, userProfile) => {
  return await apiCallWithRetry(createUser, deviceId, userProfile);
};
```

## 7. 性能优化建议

### 1. 缓存策略
```javascript
class CacheManager {
  constructor() {
    this.cache = new Map();
    this.maxSize = 100;
  }

  set(key, value, ttl = 3600000) { // 默认1小时
    if (this.cache.size >= this.maxSize) {
      // 删除最旧的缓存
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl
    });
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key);
      return null;
    }

    return item.value;
  }

  clear() {
    this.cache.clear();
  }
}

// 使用缓存
const cacheManager = new CacheManager();

const getUserProfileWithCache = async (userId) => {
  const cacheKey = `user_profile_${userId}`;
  let userProfile = cacheManager.get(cacheKey);
  
  if (!userProfile) {
    userProfile = await getUserProfile(userId);
    cacheManager.set(cacheKey, userProfile);
  }
  
  return userProfile;
};
```

### 2. 请求去重
```javascript
class RequestDeduplicator {
  constructor() {
    this.pendingRequests = new Map();
  }

  async deduplicate(key, requestFunction) {
    if (this.pendingRequests.has(key)) {
      // 如果请求正在进行中，返回现有的Promise
      return this.pendingRequests.get(key);
    }

    // 创建新的请求
    const requestPromise = requestFunction().finally(() => {
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, requestPromise);
    return requestPromise;
  }
}

// 使用请求去重
const requestDeduplicator = new RequestDeduplicator();

const generateBlueprintWithDeduplication = async (userId, userProfile) => {
  const key = `blueprint_${userId}`;
  return await requestDeduplicator.deduplicate(key, () => 
    generateQuickBlueprint(userId, userProfile)
  );
};
```

## 8. 测试和调试

### 测试数据
```javascript
// 测试用的模拟数据
const mockUserProfile = {
  gender: 'male',
  birth_date: '1990-01-01',
  birth_time: '12:00',
  birth_location: '北京, 北京, 中国'
};

const mockDeviceId = 'test_device_123';

// 测试新用户流程
const testNewUserFlow = async () => {
  try {
    console.log('开始测试新用户流程...');
    
    // 1. 检查用户状态
    const status = await checkUserStatus(mockDeviceId);
    console.log('用户状态:', status);
    
    // 2. 创建用户
    const user = await createUser(mockDeviceId, mockUserProfile);
    console.log('创建用户:', user);
    
    // 3. 生成五行结果
    const quickBlueprint = await generateQuickBlueprint(
      user.data.user_id, 
      mockUserProfile
    );
    console.log('五行结果:', quickBlueprint);
    
    // 4. 生成完整蓝图
    const completeBlueprint = await generateCompleteBlueprint(
      user.data.user_id, 
      mockUserProfile
    );
    console.log('完整蓝图:', completeBlueprint);
    
    console.log('新用户流程测试完成！');
  } catch (error) {
    console.error('测试失败:', error);
  }
};
```

### 调试工具
```javascript
// API调用日志记录
const apiLogger = {
  log: (endpoint, request, response, duration) => {
    console.log(`[API] ${endpoint}`, {
      request,
      response,
      duration: `${duration}ms`,
      timestamp: new Date().toISOString()
    });
  },

  error: (endpoint, request, error) => {
    console.error(`[API Error] ${endpoint}`, {
      request,
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  }
};

// 包装fetch以添加日志
const fetchWithLogging = async (url, options) => {
  const startTime = Date.now();
  const endpoint = url.split('/').pop();
  
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    const duration = Date.now() - startTime;
    apiLogger.log(endpoint, { url, options }, data, duration);
    
    return data;
  } catch (error) {
    const duration = Date.now() - startTime;
    apiLogger.error(endpoint, { url, options }, error);
    throw error;
  }
};
```

## 9. 主应用流程 - 进入应用后的功能

### 9.1 主应用导航结构

```
主应用
├── Heart Compass (心之罗盘) - 用户提问获取个性化指导
├── Daily Fortune (每日运势) - 基于用户信息和当前日期生成运势
└── Personal Blueprint (个人蓝图) - 展示用户的算命结果和详细分析
```

### 9.2 Heart Compass 功能

#### 接口信息
- **URL**: `POST /api/v1/heart-compass/ask`
- **用途**: 用户输入问题，获取个性化指导
- **参数**: 用户ID和问题内容

#### 请求示例
```javascript
// 获取Heart Compass指导
const getHeartCompassGuidance = async (userId, question) => {
  try {
    const response = await fetch('/api/v1/heart-compass/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
      user_id: userId,
        question: question
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取Heart Compass指导失败:', error);
    throw error;
  }
};
```

#### 请求数据格式
```json
{
  "user_id": "user_123456",
  "question": "How can I find true happiness in love?"
}
```

#### 响应格式
```json
{
  "success": true,
  "data": {
    "user_id": "user_123456",
    "question": "How can I find true happiness in love?",
    "hexagram": {
      "code": "1",
      "name": "乾卦",
      "english_name": "The Creative, Heaven",
      "title": "乾卦 - The Creative, Heaven",
      "hexagram_text": "乾：元，亨，利，贞。",
      "image_text": "天行健，君子以自强不息。",
      "focus_yao": {
        "yao_number": 1,
        "yao_text": "潜龙，勿用。"
      }
    },
    "dialogue_flow": {
      "revelation": "Heaven moves with strength, and the wise person strives constantly for self-improvement",
      "analysis": "The Qián hexagram symbolizes the power of Heaven — pure yang, strength, and eternal movement.",
      "guidance": "Trust in your inner creativity and leadership abilities",
      "encouragement": "Your persistence and efforts will bring unexpected results"
    },
    "deep_wisdom": {
      "title": "Deep Wisdom",
      "explanation": "The Qián hexagram symbolizes the power of Heaven — pure yang, strength, and eternal movement. This is the most powerful hexagram among the 64, representing creativity, leadership, and infinite possibilities.",
      "philosophical_meaning": "When Qián appears, the universe is telling you that now is the time to manifest your inner strength and creative gifts.",
      "personal_interpretation": "Just as the sky never ceases its movement, you are called to continue growing and progressing."
    },
    "action_guide": {
      "title": "Action Guide",
      "main_actions": [
        "Trust in your inner creativity and leadership abilities",
        "Take initiative and become a catalyst for positive change"
      ],
      "supporting_actions": [
        "Maintain strong will while leading with virtue and compassion",
        "Transform your vision into concrete action plans"
      ],
      "inspirational_message": "The energy of Qián flows through you, meaning you have the power to change your current situation."
    },
    "decision_protocol": {
      "title": "Decision Protocol",
      "situation_code": "QIÁN_LEADERSHIP",
      "core_strategy": "Embrace your creative power and lead with confidence",
      "action_guide": [
        "Recognize your natural leadership abilities",
        "Take bold action towards your goals",
        "Inspire others through your example"
      ]
    },
    "created_at": "2024-12-19T10:30:00"
  },
  "message": null,
  "timestamp": "2024-12-19T10:30:00"
}
```

#### 重新提问功能
```javascript
// 基于之前指导的深入探讨
const askAgain = async (userId, previousQuestionId, followUpQuestion) => {
  try {
    const response = await fetch('/api/v1/heart-compass/ask-again', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        previous_question_id: previousQuestionId,
        follow_up_question: followUpQuestion
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('重新提问失败:', error);
    throw error;
  }
};
```

#### Heart Compass 页面组件
```javascript
// HeartCompassPage.js
class HeartCompassPage {
  constructor(userId) {
    this.userId = userId;
    this.currentQuestion = null;
    this.init();
  }

  init() {
    this.render();
    this.bindEvents();
  }

  render() {
    const container = document.getElementById('heart-compass-page');
    container.innerHTML = `
      <div class="heart-compass-container">
        <h1>Heart Compass</h1>
        
        <div class="compass-visual">
          <!-- 阴阳罗盘图形 -->
          <div class="yin-yang-symbol">
            <div class="yin"></div>
            <div class="yang"></div>
          </div>
          <div class="hexagram-rings">
            <!-- 卦象环 -->
          </div>
        </div>

        <div class="question-card">
          <h3>What guidance do you seek?</h3>
          <textarea 
            id="question-input" 
            placeholder='e.g., "How can I find true happiness in love?"'
            rows="4"
          ></textarea>
          <p class="help-text">Speak from your heart - the more sincere your question, the clearer the guidance</p>
          <button class="seek-guidance-btn" id="seek-guidance-btn">
            <span class="icon">✈️</span>
            Seek Guidance
          </button>
        </div>
      </div>
    `;
  }

  bindEvents() {
    document.getElementById('seek-guidance-btn').addEventListener('click', () => {
      this.handleSeekGuidance();
    });
  }

  async handleSeekGuidance() {
    const question = document.getElementById('question-input').value.trim();
    
    if (!question) {
      this.showError('请输入您的问题');
      return;
    }

    try {
      this.showLoading();
      
      const result = await getHeartCompassGuidance(this.userId, question);
      
      if (result.success) {
        this.currentQuestion = result.data;
        this.showGuidanceResult(result.data);
    } else {
        throw new Error(result.message || '获取指导失败');
    }
  } catch (error) {
      console.error('获取Heart Compass指导失败:', error);
      this.showError('获取指导失败，请重试');
    } finally {
      this.hideLoading();
    }
  }

  showGuidanceResult(guidanceData) {
    const container = document.getElementById('heart-compass-page');
    container.innerHTML = `
      <div class="guidance-result">
        <h2>Your Guidance</h2>
        
        <!-- 卦象显示 -->
        <div class="hexagram-card">
          <div class="hexagram-symbol">${guidanceData.hexagram.name}</div>
          <div class="hexagram-english">(${guidanceData.hexagram.english_name})</div>
          <div class="hexagram-title">${guidanceData.hexagram.title}</div>
          <div class="hexagram-quote">"${guidanceData.dialogue_flow.revelation}"</div>
        </div>

        <!-- 深层智慧 -->
        <div class="deep-wisdom-card">
          <h3>💖 Deep Wisdom</h3>
          <p>${guidanceData.deep_wisdom.explanation}</p>
        </div>

        <!-- 行动指南 -->
        <div class="action-guide-card">
          <h3>✨ Action Guide</h3>
          <ul>
            ${guidanceData.action_guide.main_actions.map(action => 
              `<li><span class="bullet">●</span>${action}</li>`
            ).join('')}
          </ul>
        </div>

        <!-- 重新提问按钮 -->
        <button class="ask-again-btn" id="ask-again-btn">Ask Again</button>
      </div>
    `;

    // 绑定重新提问事件
    document.getElementById('ask-again-btn').addEventListener('click', () => {
      this.showAskAgainForm();
    });
  }

  showAskAgainForm() {
    const container = document.getElementById('heart-compass-page');
    container.innerHTML = `
      <div class="ask-again-form">
        <h3>Ask a Follow-up Question</h3>
        <textarea 
          id="follow-up-question" 
          placeholder="What would you like to explore further?"
          rows="4"
        ></textarea>
        <button class="submit-follow-up-btn" id="submit-follow-up-btn">Submit Question</button>
        <button class="back-to-guidance-btn" id="back-to-guidance-btn">Back to Guidance</button>
      </div>
    `;

    // 绑定事件
    document.getElementById('submit-follow-up-btn').addEventListener('click', () => {
      this.handleFollowUpQuestion();
    });

    document.getElementById('back-to-guidance-btn').addEventListener('click', () => {
      this.showGuidanceResult(this.currentQuestion);
    });
  }

  async handleFollowUpQuestion() {
    const followUpQuestion = document.getElementById('follow-up-question').value.trim();
    
    if (!followUpQuestion) {
      this.showError('请输入您的问题');
      return;
    }

    try {
      this.showLoading();
      
      const result = await askAgain(
        this.userId, 
        this.currentQuestion.id, 
        followUpQuestion
      );
      
      if (result.success) {
        this.currentQuestion = result.data;
        this.showGuidanceResult(result.data);
    } else {
        throw new Error(result.message || '重新提问失败');
    }
  } catch (error) {
      console.error('重新提问失败:', error);
      this.showError('重新提问失败，请重试');
    } finally {
      this.hideLoading();
    }
  }

  showLoading() {
    // 显示加载状态
  }

  hideLoading() {
    // 隐藏加载状态
  }

  showError(message) {
    // 显示错误信息
    console.error(message);
  }
}
```

### 9.3 Daily Fortune 功能

#### 接口信息
- **URL**: `POST /api/v1/daily-fortune/generate`
- **用途**: 基于用户信息和当前日期生成每日运势
- **参数**: 用户ID

#### 请求示例
```javascript
// 生成每日运势
const generateDailyFortune = async (userId) => {
  try {
    const response = await fetch('/api/v1/daily-fortune/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId
      })
    });
    
    const result = await response.json();
  return result;
} catch (error) {
    console.error('生成每日运势失败:', error);
    throw error;
  }
};
```

#### 响应格式
```json
{
  "success": true,
  "data": {
    "user_id": "user_123456",
    "date": "2024-12-19",
    "hexagram": {
      "name": "乾",
      "pinyin": "Qián",
      "english_name": "The Creative, Heaven",
      "title": "乾卦 - The Creative, Heaven",
      "energy": "Strong and creative energy",
      "luck": 85,
      "hexagram_text": "乾：元，亨，利，贞。",
      "image_text": "天行健，君子以自强不息。"
    },
    "time_advice": [
      {
        "period": "Morning",
        "start_time": "05:00",
        "end_time": "11:00",
        "activity": "Meditation & Mindfulness",
        "description": "Dawn breaks with fresh energy, perfect for meditation and infusing positive energy into your new day.",
        "energy": "High",
        "priority": "High"
      },
      {
        "period": "Afternoon",
        "start_time": "11:00",
        "end_time": "17:00",
        "activity": "Creative Work",
        "description": "Your creative energy peaks during this time, ideal for artistic projects and innovative thinking.",
        "energy": "Medium",
        "priority": "Medium"
      }
    ],
    "lucky_elements": {
      "color": "Green",
      "direction": "North",
      "number": 2,
      "element": "Wood",
      "gemstone": "Jade"
    },
    "personal_advice": "Today is ideal for acquiring new knowledge and skills. Maintain inner peace and respond to all situations with wisdom.",
    "created_at": "2024-12-19T10:30:00"
  },
  "message": null,
  "timestamp": "2024-12-19T10:30:00"
}
```

#### 获取运势历史
```javascript
// 获取用户的运势历史
const getDailyFortuneHistory = async (userId, page = 1, limit = 10) => {
  try {
    const response = await fetch(`/api/v1/daily-fortune/${userId}/history?page=${page}&limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取运势历史失败:', error);
    throw error;
  }
};
```

#### Daily Fortune 页面组件
```javascript
// DailyFortunePage.js
class DailyFortunePage {
  constructor(userId) {
    this.userId = userId;
    this.currentFortune = null;
    this.init();
  }

  init() {
    this.render();
    this.loadDailyFortune();
  }

  render() {
    const container = document.getElementById('daily-fortune-page');
    container.innerHTML = `
      <div class="daily-fortune-container">
        <h1>Today's Fortune</h1>
        
        <div class="fortune-content">
          <!-- 运势内容将在这里动态加载 -->
        </div>
      </div>
    `;
  }

  async loadDailyFortune() {
    try {
      this.showLoading();
      
      const result = await generateDailyFortune(this.userId);
      
      if (result.success) {
        this.currentFortune = result.data;
        this.displayFortune(result.data);
      } else {
        throw new Error(result.message || '生成运势失败');
      }
    } catch (error) {
      console.error('加载每日运势失败:', error);
      this.showError('加载运势失败，请重试');
  } finally {
      this.hideLoading();
    }
  }

  displayFortune(fortuneData) {
    const container = document.querySelector('.fortune-content');
    
    container.innerHTML = `
      <!-- 卦象插图 -->
      <div class="hexagram-illustration">
        <div class="illustration-frame">
          <img src="/images/hexagrams/${fortuneData.hexagram.name}.png" alt="${fortuneData.hexagram.english_name}">
        </div>
      </div>

      <!-- 卦象信息 -->
      <div class="hexagram-info-card">
        <h2>The Creative</h2>
        <div class="hexagram-symbol">${fortuneData.hexagram.name}</div>
        <div class="overall-fortune">
          <span>Overall Fortune</span>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${fortuneData.hexagram.luck}%"></div>
          </div>
          <span class="fortune-percentage">${fortuneData.hexagram.luck}%</span>
        </div>
      </div>

      <!-- 时段建议 -->
      <div class="time-advice-section">
        <h3>Daily Recommendations</h3>
        ${fortuneData.time_advice.map(advice => `
          <div class="time-advice-card ${advice.period.toLowerCase()}">
            <div class="time-header">
              <span class="time-period">${advice.period} (${advice.start_time}-${advice.end_time})</span>
              <span class="time-rating">${advice.priority === 'High' ? 'Good' : 'Fair'}</span>
            </div>
            <div class="advice-content">
              <div class="advice-activity">${advice.activity}</div>
              <div class="advice-description">${advice.description}</div>
            </div>
          </div>
        `).join('')}
      </div>

      <!-- 幸运元素 -->
      <div class="lucky-elements-card">
        <h3>🍀 Today's Lucky Elements</h3>
        <div class="elements-grid">
          <div class="element-item">
            <div class="element-icon">🎨</div>
            <div class="element-label">Lucky Color</div>
            <div class="element-value">${fortuneData.lucky_elements.color}</div>
          </div>
          <div class="element-item">
            <div class="element-icon">🧭</div>
            <div class="element-label">Lucky Direction</div>
            <div class="element-value">${fortuneData.lucky_elements.direction}</div>
          </div>
          <div class="element-item">
            <div class="element-icon">📅</div>
            <div class="element-label">Lucky Number</div>
            <div class="element-value">${fortuneData.lucky_elements.number}</div>
          </div>
          <div class="element-item">
            <div class="element-icon">📆</div>
            <div class="element-label">Today's Hexagram</div>
            <div class="element-value">${fortuneData.lucky_elements.element}</div>
          </div>
        </div>
      </div>

      <!-- 每日箴言 -->
      <div class="daily-mantra-card">
        <h3>💖 Daily Mantra</h3>
        <div class="mantra-text">"${fortuneData.hexagram.image_text}"</div>
      </div>

      <!-- 个人指导 -->
      <div class="personal-guidance-card">
        <h3>🌟 Personal Guidance</h3>
        <div class="guidance-text">${fortuneData.personal_advice}</div>
      </div>
    `;
  }

  showLoading() {
    // 显示加载状态
  }

  hideLoading() {
    // 隐藏加载状态
  }

  showError(message) {
    // 显示错误信息
    console.error(message);
  }
}
```

### 9.4 Personal Blueprint 功能

#### 接口信息
- **URL**: `GET /api/v1/blueprint/{user_id}`
- **用途**: 获取用户的完整算命结果和个人蓝图
- **参数**: 用户ID

#### 请求示例
```javascript
// 获取用户蓝图
const getUserBlueprint = async (userId) => {
  try {
    const response = await fetch(`/api/v1/blueprint/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const result = await response.json();
  return result;
} catch (error) {
    console.error('获取用户蓝图失败:', error);
    throw error;
  }
};
```

#### Personal Blueprint 页面组件
```javascript
// PersonalBlueprintPage.js
class PersonalBlueprintPage {
  constructor(userId) {
    this.userId = userId;
    this.blueprintData = null;
    this.init();
  }

  init() {
    this.render();
    this.loadBlueprint();
  }

  render() {
    const container = document.getElementById('personal-blueprint-page');
    container.innerHTML = `
      <div class="personal-blueprint-container">
        <h1>Your Personal Blueprint</h1>
        
        <div class="blueprint-content">
          <!-- 蓝图内容将在这里动态加载 -->
        </div>
      </div>
    `;
  }

  async loadBlueprint() {
    try {
      this.showLoading();
      
      const result = await getUserBlueprint(this.userId);
      
      if (result.success) {
        this.blueprintData = result.data;
        this.displayBlueprint(result.data);
      } else {
        throw new Error(result.message || '获取蓝图失败');
      }
    } catch (error) {
      console.error('加载个人蓝图失败:', error);
      this.showError('加载蓝图失败，请重试');
    } finally {
      this.hideLoading();
    }
  }

  displayBlueprint(blueprintData) {
    const container = document.querySelector('.blueprint-content');
    
    container.innerHTML = `
      <!-- 用户基本信息 -->
      <div class="user-info-card">
        <div class="beautiful-soul-tag">
          <span class="icon">🌸</span>
          Beautiful Soul
        </div>
        <div class="user-details">
          <div class="detail-item">
            <span class="icon">📅</span>
            <span>Birth Date: ${this.formatDate(blueprintData.user_profile.birth_date)}</span>
          </div>
          <div class="detail-item">
            <span class="icon">🕐</span>
            <span>Birth Time: ${blueprintData.user_profile.birth_time}</span>
          </div>
          <div class="detail-item">
            <span class="icon">📍</span>
            <span>Birth Location: ${blueprintData.user_profile.birth_location}</span>
          </div>
        </div>
      </div>

      <!-- 主导元素 -->
      <div class="dominant-element-card">
        <h3>Dominant Element</h3>
        <div class="element-display">
          <div class="element-circle ${blueprintData.elemental_profile.dominant_element.toLowerCase()}">
            ${this.getElementSymbol(blueprintData.elemental_profile.dominant_element)}
          </div>
          <button class="strength-btn">${blueprintData.elemental_profile[blueprintData.elemental_profile.dominant_element.toLowerCase()].strength}% Strength</button>
        </div>
        <div class="element-description">
          ${this.getElementDescription(blueprintData.elemental_profile.dominant_element)}
        </div>
      </div>

      <!-- 五行分布 -->
      <div class="five-elements-card">
        <h3>Five Elements Distribution</h3>
        ${Object.entries(blueprintData.elemental_profile).map(([element, data]) => `
          <div class="element-row">
            <div class="element-info">
              <span class="element-symbol">${this.getElementSymbol(element)}</span>
              <span class="element-name">${this.getElementName(element)}</span>
      </div>
            <div class="element-percentage">${data.strength}%</div>
            <div class="element-bar">
              <div class="bar-fill ${element}" style="width: ${data.strength}%"></div>
            </div>
          </div>
        `).join('')}
      </div>

      <!-- 生命洞察 -->
      <div class="life-insights-card">
        <h3>🌟 Life Insights</h3>
        
        <div class="insight-section">
          <h4>Core Gifts</h4>
          <p>${blueprintData.inner_blueprint.core_essence.description}</p>
        </div>

        <div class="insight-section">
          <h4>Growth Challenges</h4>
          <p>${blueprintData.inner_blueprint.growth_areas.analysis}</p>
        </div>

        <div class="insight-section">
          <h4>Life Mission</h4>
          <p>${blueprintData.inner_blueprint.life_journey_curve.description}</p>
        </div>
      </div>

      <!-- 查看完整蓝图按钮 -->
      <button class="view-complete-btn" id="view-complete-btn">
        View Complete Blueprint Analysis →
      </button>
    `;

    // 绑定查看完整蓝图事件
    document.getElementById('view-complete-btn').addEventListener('click', () => {
      this.showCompleteBlueprint();
    });
  }

  showCompleteBlueprint() {
    const container = document.querySelector('.blueprint-content');
    
    container.innerHTML = `
      <h2>Your Inner Blueprint</h2>
      
      <!-- 五行和谐 -->
      <div class="five-elements-harmony-card">
        <h3>Five Elements Harmony</h3>
        <div class="radar-chart">
          <!-- 这里应该渲染雷达图 -->
          <canvas id="radar-chart" width="300" height="300"></canvas>
            </div>
        <div class="element-breakdown">
          ${Object.entries(this.blueprintData.elemental_profile).slice(0, 3).map(([element, data]) => `
            <div class="element-progress">
              <span>${this.getElementName(element)}</span>
              <div class="progress-bar">
                <div class="progress-fill" style="width: ${data.strength}%"></div>
        </div>
              <span class="percentage">${data.strength}%</span>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- 生命能量流 -->
      <div class="life-energy-flow-card">
        <h3>Life Energy Flow</h3>
        <div class="line-chart">
          <!-- 这里应该渲染生命曲线图 -->
          <canvas id="life-energy-chart" width="300" height="200"></canvas>
    </div>
      </div>

      <!-- 核心能量场 -->
      <div class="core-energy-field-card">
        <h3>✨ Core Energy Field</h3>
        <p>${this.blueprintData.inner_blueprint.core_essence.description}</p>
        <div class="primary-strengths">
          <strong>Primary strengths:</strong> ${this.blueprintData.inner_blueprint.natural_strengths.strengths.slice(0, 3).join(', ')}
    </div>
      </div>

      <!-- 成长挑战 -->
      <div class="growth-challenges-card">
        <h3>🌱 Growth Challenges</h3>
        <p>${this.blueprintData.inner_blueprint.growth_areas.analysis}</p>
        <div class="focus-areas">
          <strong>Focus areas:</strong> ${this.blueprintData.inner_blueprint.growth_areas.balance_path.suggestions.slice(0, 3).join(', ')}
        </div>
      </div>

      <!-- 行动指南 -->
      <div class="action-guide-card">
        <h3>✨ Action Guide</h3>
        <ul>
          <li><span class="bullet green">●</span>Practice daily grounding meditation for 10 minutes</li>
          <li><span class="bullet pink">●</span>Channel your Fire energy into creative projects</li>
          <li><span class="bullet gray">●</span>Establish consistent sleep and meal routines</li>
        </ul>
    </div>

      <!-- 导航按钮 -->
      <div class="navigation-buttons">
        <button class="back-btn" id="back-btn">Back</button>
        <button class="explore-btn" id="explore-btn">Explore Heart Compass</button>
  </div>
    `;

    // 绑定事件
    document.getElementById('back-btn').addEventListener('click', () => {
      this.displayBlueprint(this.blueprintData);
    });

    document.getElementById('explore-btn').addEventListener('click', () => {
      // 跳转到Heart Compass页面
      this.navigateToHeartCompass();
    });

    // 渲染图表
    this.renderCharts();
  }

  renderCharts() {
    // 渲染雷达图
    this.renderRadarChart();
    
    // 渲染生命能量流图
    this.renderLifeEnergyChart();
  }

  renderRadarChart() {
    const canvas = document.getElementById('radar-chart');
    const ctx = canvas.getContext('2d');
    
    // 这里实现雷达图的绘制逻辑
    // 使用this.blueprintData.elemental_profile数据
  }

  renderLifeEnergyChart() {
    const canvas = document.getElementById('life-energy-chart');
    const ctx = canvas.getContext('2d');
    
    // 这里实现生命能量流图的绘制逻辑
    // 使用this.blueprintData.inner_blueprint.life_journey_curve.chart_data数据
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  }

  getElementSymbol(element) {
    const symbols = {
      earth: '土',
      fire: '火',
      water: '水',
      metal: '金',
      wood: '木'
    };
    return symbols[element.toLowerCase()] || element;
  }

  getElementName(element) {
    return element.charAt(0).toUpperCase() + element.slice(1);
  }

  getElementDescription(element) {
    const descriptions = {
      earth: 'Your Earth element provides stability and nurturing qualities. You are reliable and caring.',
      fire: 'Your Fire element burns brightest, representing passion, intuition, and transformative power. You possess natural leadership abilities and the gift to inspire others.',
      water: 'Your Water element flows with intuition and adaptability. You are deeply empathetic and flexible.',
      metal: 'Your Metal element brings precision and logic. You are analytical and focused.',
      wood: 'Your Wood element represents growth and creativity. You are innovative and expanding.'
    };
    return descriptions[element.toLowerCase()] || 'This element represents your unique qualities.';
  }

  navigateToHeartCompass() {
    // 实现页面跳转逻辑
    console.log('Navigating to Heart Compass...');
  }

  showLoading() {
    // 显示加载状态
  }

  hideLoading() {
    // 隐藏加载状态
  }

  showError(message) {
    // 显示错误信息
    console.error(message);
  }
}
```

### 9.5 主应用导航管理

#### 主应用容器
```javascript
// MainApp.js
class MainApp {
  constructor() {
    this.userId = null;
    this.currentPage = 'heart-compass';
    this.pages = {};
    this.init();
  }

  async init() {
    // 获取用户ID（从localStorage或URL参数）
    this.userId = this.getUserId();
    
    if (!this.userId) {
      // 如果没有用户ID，重定向到新用户流程
      window.location.href = '/onboarding';
      return;
    }

    // 检查用户是否有算命结果，如果没有则提示重新生成
    await this.checkBlueprintStatus();

    this.initPages();
    this.render();
    this.bindEvents();
  }

  async checkBlueprintStatus() {
    try {
      const result = await getUserBlueprint(this.userId);
      
      if (!result.success || !result.data) {
        // 没有算命结果，显示提示
        this.showBlueprintMissingNotice();
      }
    } catch (error) {
      console.warn('检查算命结果状态失败:', error);
      // 静默处理，不影响主应用使用
    }
  }

  showBlueprintMissingNotice() {
    // 在主应用顶部显示提示，用户可以点击重新生成
    const notice = document.createElement('div');
    notice.className = 'blueprint-missing-notice';
    notice.innerHTML = `
      <div class="notice-content">
        <span>您还没有个人蓝图，</span>
        <button class="regenerate-btn" id="regenerate-blueprint-btn">点击生成</button>
      </div>
    `;
    
    document.body.insertBefore(notice, document.body.firstChild);
    
    // 绑定重新生成事件
    document.getElementById('regenerate-blueprint-btn').addEventListener('click', () => {
      this.regenerateBlueprint();
    });
  }

  async regenerateBlueprint() {
    try {
      // 显示重新生成页面
      this.showRegeneratingPage();
      
      // 调用重新生成API
      const result = await regenerateBlueprint(this.userId, this.userProfile);
      
      if (result.success) {
        // 重新生成成功，隐藏提示
        this.hideBlueprintMissingNotice();
        this.showSuccessMessage('个人蓝图重新生成成功！');
        
        // 刷新Personal Blueprint页面
        if (this.currentPage === 'personal-blueprint') {
          this.pages['personal-blueprint'].loadBlueprint();
        }
      } else {
        throw new Error(result.message || '重新生成失败');
    }
  } catch (error) {
      console.error('重新生成个人蓝图失败:', error);
      this.showError('重新生成失败，请重试');
    } finally {
      this.hideRegeneratingPage();
    }
  }

  showRegeneratingPage() {
    // 显示重新生成中的页面
    const container = document.getElementById('page-content');
  container.innerHTML = `
      <div class="regenerating-page">
        <div class="loading-spinner"></div>
        <h3>正在重新生成您的个人蓝图...</h3>
        <p>这可能需要几分钟时间，请耐心等待</p>
    </div>
    `;
  }

  hideRegeneratingPage() {
    // 隐藏重新生成页面，恢复当前页面
    this.showPage(this.currentPage);
  }

  hideBlueprintMissingNotice() {
    const notice = document.querySelector('.blueprint-missing-notice');
    if (notice) {
      notice.remove();
    }
  }

  showSuccessMessage(message) {
    // 显示成功消息
    const toast = document.createElement('div');
    toast.className = 'success-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  showError(message) {
    // 显示错误消息
    console.error(message);
  }

  getUserId() {
    // 从localStorage获取用户ID
    return localStorage.getItem('user_id');
  }

  initPages() {
    this.pages = {
      'heart-compass': new HeartCompassPage(this.userId),
      'daily-fortune': new DailyFortunePage(this.userId),
      'personal-blueprint': new PersonalBlueprintPage(this.userId)
    };
  }

  render() {
    const container = document.getElementById('main-app');
    container.innerHTML = `
      <div class="main-app-container">
        <!-- 页面内容区域 -->
        <div class="page-content" id="page-content">
          <!-- 页面内容将在这里动态加载 -->
        </div>

        <!-- 底部导航栏 -->
        <nav class="bottom-navigation">
          <div class="nav-item ${this.currentPage === 'heart-compass' ? 'active' : ''}" data-page="heart-compass">
            <div class="nav-icon">🧭</div>
            <div class="nav-label">Heart Compass</div>
          </div>
          <div class="nav-item ${this.currentPage === 'daily-fortune' ? 'active' : ''}" data-page="daily-fortune">
            <div class="nav-icon">⭐</div>
            <div class="nav-label">Daily Fortune</div>
          </div>
          <div class="nav-item ${this.currentPage === 'personal-blueprint' ? 'active' : ''}" data-page="personal-blueprint">
            <div class="nav-icon">👤</div>
            <div class="nav-label">Personal Blueprint</div>
          </div>
        </nav>
      </div>
    `;

    // 显示当前页面
    this.showPage(this.currentPage);
  }

  bindEvents() {
    // 绑定导航事件
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const page = e.currentTarget.dataset.page;
        this.navigateToPage(page);
      });
    });
  }

  navigateToPage(pageName) {
    if (this.currentPage === pageName) return;

    this.currentPage = pageName;
    
    // 更新导航状态
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
      if (item.dataset.page === pageName) {
        item.classList.add('active');
      }
    });

    // 显示页面
    this.showPage(pageName);
  }

  showPage(pageName) {
    const pageContent = document.getElementById('page-content');
    
    // 隐藏所有页面
    Object.keys(this.pages).forEach(page => {
      const pageElement = document.getElementById(`${page}-page`);
      if (pageElement) {
        pageElement.style.display = 'none';
      }
    });

    // 显示目标页面
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
      targetPage.style.display = 'block';
    } else {
      // 如果页面不存在，创建页面容器
      pageContent.innerHTML = `<div id="${pageName}-page"></div>`;
      this.pages[pageName].init();
    }
  }
}

// 初始化主应用
document.addEventListener('DOMContentLoaded', () => {
  new MainApp();
});
```

## 总结

这个前端API集成指南提供了：

1. **完整的API接口说明** - 覆盖新用户流程和主应用的所有功能
2. **详细的代码示例** - 包含错误处理、重试机制、性能优化
3. **前端组件实现** - 提供完整的页面组件代码
4. **主应用流程** - Heart Compass、Daily Fortune、Personal Blueprint的完整实现
5. **最佳实践建议** - 缓存策略、请求去重、错误处理等

后端已经完全支持所有功能，前端只需要按照这个指南调用相应的API接口即可实现完整的用户体验。

### 关键功能点：

#### 用户流程
- ✅ **新用户**: 用户状态检查 → 出生时间收集 → 出生地点性别收集 → 五行计算 → 个人特质分析 → 人生指导 → Enter App
- ✅ **老用户**: 用户状态检查 → 直接进入主应用（无需重新收集信息）

#### 主应用功能
- ✅ **Heart Compass**: 用户提问获取个性化指导，支持重新提问
- ✅ **Daily Fortune**: 基于用户信息和当前日期生成运势，包含时段建议和幸运元素
- ✅ **Personal Blueprint**: 展示用户算命结果，支持查看完整蓝图分析

#### 老用户特殊处理
- ✅ **智能识别**: 老用户通过设备ID识别，直接进入主应用
- ✅ **蓝图状态检查**: 自动检查是否有算命结果，无结果时显示友好提示
- ✅ **重新生成**: 在主应用中提供重新生成个人蓝图的选项
- ✅ **无缝体验**: 老用户无需重复填写信息，保持流畅的用户体验

#### 技术特点
- 分层架构算命系统（快速五行 + 完整蓝图）
- 统一的错误处理和重试机制
- 性能优化和用户体验提升
- 完整的页面组件和导航管理
- 智能的用户状态管理和流程控制
