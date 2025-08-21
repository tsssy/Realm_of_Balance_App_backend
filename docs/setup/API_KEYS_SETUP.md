# API Keys 配置说明

## 🔑 概述

本项目主要使用Google Gemini API作为AI服务提供商，支持长提示词和复杂生成任务。为了快速开始，我们已经在配置中提供了默认的API key，但建议你使用自己的API key以获得更好的性能和稳定性。

**当前配置状态**: 已优化Gemini API配置，支持8192 tokens输出，完全支持个人蓝图、Heart Compass和每日运势的AI生成任务。

## 🚀 快速开始

### 1. 使用默认配置（推荐用于测试）

项目已经配置了可用的API key，你可以直接运行：

```bash
# 复制环境变量文件
cp env.example .env

# 安装依赖
pip install -r requirements.txt

# 运行项目
python run.py
```

### 2. 配置自己的API Key

#### Google Gemini API
1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的API key
3. 在 `.env` 文件中更新：
```bash
GEMINI_API_KEY=your_actual_gemini_api_key
```

#### Moonshot Kimi API
1. 访问 [Moonshot AI](https://www.moonshot.cn/)
2. 注册账号并获取API key
3. 在 `.env` 文件中更新：
```bash
KIMI_API_KEY=your_actual_kimi_api_key
```

#### 豆包API
1. 访问 [豆包官网](https://www.doubao.com/)
2. 注册账号并获取API key
3. 在 `.env` 文件中更新：
```bash
DOUBAO_API_KEY=your_actual_doubao_api_key
```

## ⚙️ 配置选项

### 当前AI服务配置

项目当前主要使用Google Gemini API，配置已优化：

```bash
# 主要AI服务 (已优化配置)
CURRENT_AI_SERVICE=gemini

# Gemini API配置优化
GEMINI_MODEL_NAME=gemini-2.5-flash
GEMINI_MAX_OUTPUT_TOKENS=8192
GEMINI_TIMEOUT=60
```

### 模型配置

每个AI服务都支持不同的模型：

#### Gemini (主要使用)
- `gemini-2.5-flash` (推荐，快速且经济，支持8192 tokens)
- `gemini-2.5-pro` (更强大，但较慢，支持8192 tokens)
- `gemini-1.5-pro` (平衡性能和速度，支持8192 tokens)

**注意**: 项目已优化配置，主要使用 `gemini-2.5-flash` 模型，支持长提示词和复杂AI生成任务。

## 🔒 安全注意事项

### 1. 不要提交API Key到版本控制
```bash
# 确保 .env 文件在 .gitignore 中
echo ".env" >> .gitignore
```

### 2. 生产环境安全
- 使用环境变量而不是配置文件
- 定期轮换API key
- 监控API使用量

### 3. 本地开发
- 使用 `.env` 文件进行本地配置
- 不要将真实的API key分享给他人

## 📊 API使用统计

### 免费额度
- **Gemini**: 每分钟15次请求，每月1500次
- **Kimi**: 每月1000次请求
- **豆包**: 每月1000次请求

### 付费计划
- **Gemini**: $0.50/1M tokens
- **Kimi**: ¥0.12/1K tokens
- **豆包**: ¥0.12/1K tokens

## 🚨 故障排除

### 1. API Key无效
```bash
# 检查环境变量是否正确加载
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

### 2. 请求超时
```bash
# 增加超时时间
AI_REQUEST_TIMEOUT=120
AI_MAX_RETRIES=5
```

### 3. 模型不可用
```bash
# 尝试其他模型
GEMINI_MODEL_NAME=gemini-1.5-pro
```

## 📞 技术支持

如果遇到API相关的问题：

1. 检查API key是否有效
2. 确认网络连接正常
3. 查看API服务商的状态页面
4. 检查请求频率是否超限

## 🔄 更新日志

- **v1.2.0** (2024年8月): Gemini API配置优化，支持8192 tokens输出
  - 优化个人蓝图、Heart Compass、每日运势的AI生成
  - 支持长提示词和复杂生成任务
  - 改进错误处理和重试机制
- **v1.0.0**: 初始配置，支持Gemini、Kimi、豆包API
  - 默认配置可直接使用
  - 支持环境变量覆盖
  - 完整的错误处理和重试机制
