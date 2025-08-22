import os
import asyncio
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from app.config import settings
from app.config.prompt_config import PromptType, PromptConfig
from app.utils.logger import MyLogger
from app.utils.prompt_manager import prompt_manager

logger = MyLogger("ai_service")

class GeminiInteractionAPI:
    """与 Gemini AI 模型进行交互的 API 封装"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.api_url = settings.GEMINI_API_URL
        self.model_name = settings.GEMINI_MODEL_NAME
        self.max_retries = 3  # 最大重试次数
        self.timeout = 60  # 请求超时时间（秒）
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY 未设置")
            raise ValueError("GEMINI_API_KEY 未设置")
    
    async def send_message_to_ai(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """向 Gemini API 发送消息并获取响应"""
        try:
            # 构建请求数据
            request_data = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.5,
                    "maxOutputTokens": 8192
                }
            }
            
            # 发送 API 请求（包含重试机制）
            response_json = await self._make_api_request(request_data)
            
            # 解析响应
            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                candidate = response_json['candidates'][0]
                
                # 检查是否有内容
                if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                    # 检查是否有文本内容
                    if 'text' in candidate['content']['parts'][0]:
                        ai_response = candidate['content']['parts'][0]['text'].strip()
                        if ai_response:  # 确保文本不为空
                            return {
                                "success": True,
                                "message": ai_response,
                                "timestamp": datetime.now().isoformat()
                            }
                
                # 检查是否因为token限制而提前结束
                if candidate.get('finishReason') == 'MAX_TOKENS':
                    logger.warning("Gemini API 因token限制提前结束，尝试获取部分响应")
                    # 尝试获取部分响应
                    if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                        if 'text' in candidate['content']['parts'][0]:
                            ai_response = candidate['content']['parts'][0]['text'].strip()
                            if ai_response:
                                return {
                                    "success": True,
                                    "message": ai_response,
                                    "timestamp": datetime.now().isoformat()
                                }
                    
                    # 如果没有部分响应，返回错误
                    raise Exception("API 响应因token限制提前结束，请简化提示词")
                
                # 检查是否是Think Mode响应（没有实际内容）
                if candidate.get('finishReason') == 'STOP' and 'content' in candidate:
                    content = candidate['content']
                    # 检查是否有parts字段，如果没有就是Think Mode响应
                    if 'parts' not in content or not content.get('parts'):
                        # 这是Think Mode响应，没有实际内容
                        logger.warning("Gemini API 返回Think Mode响应，没有实际内容")
                        raise Exception("AI返回了思考过程但没有实际内容，请重试或检查提示词")
            
            # 如果没有找到预期的响应格式，记录响应内容并返回错误
            logger.error(f"Gemini API 响应格式异常: {response_json}")
            raise Exception(f"API 响应格式错误: {response_json}")
            
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
                logger.info(f"等待 {sleep_time}秒后重试...")
                await asyncio.sleep(sleep_time)
        
        raise Exception("Gemini API 调用最终失败")
    
    async def get_fallback_response(self) -> Dict[str, Any]:
        """获取备用响应（当 API 调用失败时使用）"""
        return {
            "success": False,
            "message": "抱歉，AI 服务暂时不可用，请稍后再试。",
            "timestamp": datetime.now().isoformat()
        }

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

class AIService:
    """AI 服务主类 - 支持动态提示词选择"""
    
    def __init__(self):
        self.gemini_api = GeminiInteractionAPI()
        self.response_processor = AIResponseProcessor()
    
    async def generate_with_prompt(
        self, 
        prompt_type: PromptType, 
        context: Dict[str, Any],
        parse_response_func: callable = None
    ) -> Dict[str, Any]:
        """
        通用AI生成方法，支持动态提示词选择
        
        Args:
            prompt_type: 提示词类型（PromptType 枚举）
            context: 上下文信息
            parse_response_func: 响应解析函数（可选）
        """
        try:
            # 验证提示词类型
            if not PromptConfig.is_valid_prompt_type(prompt_type.value):
                raise ValueError(f"无效的提示词类型: {prompt_type.value}")
            
            # 获取提示词文件名
            filename = PromptConfig.get_prompt_filename(prompt_type)
            
            # 根据文件名获取提示词
            prompt = prompt_manager.get_prompt_by_filename(filename, context)
            
            if not prompt:
                raise Exception(f"无法获取 {prompt_type.value} 提示词")
            
            # 记录日志
            logger.info(f"使用提示词类型: {prompt_type.value}, 文件: {PromptConfig.get_prompt_filename(prompt_type)}")
            
            # 调用 AI 服务
            response = await self.gemini_api.send_message_to_ai(prompt, context)
            
            if response.get("success"):
                ai_content = response.get("message", "")
                
                # 如果提供了解析函数，则解析响应
                if parse_response_func:
                    parsed_result = parse_response_func(ai_content)
                    # 如果解析函数返回字符串，直接作为ai_content
                    if isinstance(parsed_result, str):
                        ai_content = parsed_result
                        parsed_result = None
                else:
                    parsed_result = {"raw_content": ai_content}
                
                return {
                    "success": True,
                    "data": parsed_result,
                    "ai_content": ai_content
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"AI 生成失败 ({prompt_type.value}): {e}")
            return {
                "success": False,
                "message": f"AI 生成失败: {str(e)}"
            }
    
    async def generate_blueprint(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成算命结果（内在蓝图）"""
        try:
            # 构建上下文
            context = {
                "gender": user_profile.get("gender"),
                "birth_date": user_profile.get("birth_date"),
                "birth_time": user_profile.get("birth_time"),
                "birth_location": user_profile.get("birth_location")
            }
            
            return await self.generate_with_prompt(
                PromptType.BLUEPRINT, 
                context, 
                self._parse_blueprint_response
            )
        except Exception as e:
            logger.error(f"生成算命结果失败: {e}")
            return {
                "success": False,
                "message": f"生成算命结果失败: {str(e)}"
            }
    
    async def generate_blueprint_quick(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """快速生成五行计算结果"""
        try:
            # 构建上下文
            context = {
                "gender": user_profile.get("gender"),
                "birth_date": user_profile.get("birth_date"),
                "birth_time": user_profile.get("birth_time"),
                "birth_location": user_profile.get("birth_location")
            }
            
            return await self.generate_with_prompt(
                PromptType.BLUEPRINT_QUICK, 
                context, 
                self._parse_blueprint_quick_response
            )
        except Exception as e:
            logger.error(f"快速生成五行结果失败: {e}")
            return {
                "success": False,
                "message": f"快速生成五行结果失败: {str(e)}"
            }
    
    async def generate_blueprint_complete(self, user_profile: Dict[str, Any], quick_result: Dict[str, Any]) -> Dict[str, Any]:
        """基于五行结果生成完整蓝图"""
        try:
            # 构建上下文，包含五行结果
            context = {
                "gender": user_profile.get("gender"),
                "birth_date": user_profile.get("birth_date"),
                "birth_time": user_profile.get("birth_time"),
                "birth_location": user_profile.get("birth_location"),
                "quick_result": quick_result  # 添加五行结果
            }
            
            return await self.generate_with_prompt(
                PromptType.BLUEPRINT_COMPLETE, 
                context, 
                self._parse_blueprint_complete_response
            )
        except Exception as e:
            logger.error(f"生成完整蓝图失败: {e}")
            return {
                "success": False,
                "message": f"生成完整蓝图失败: {str(e)}"
            }
    
    async def seek_heart_compass_guidance(self, question: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """获取 Heart Compass 指导"""
        # 构建上下文
        context = {
            "question": question,
            **user_profile
        }
        
        return await self.generate_with_prompt(
            PromptType.HEART_COMPASS, 
            context, 
            self._parse_heart_compass_response
        )
    
    async def generate_daily_fortune(self, user_profile: Dict[str, Any], date: str = None) -> Dict[str, Any]:
        """生成每日运势"""
        # 构建上下文
        context = {
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            **user_profile
        }
        
        return await self.generate_with_prompt(
            PromptType.DAILY_FORTUNE, 
            context, 
            self._parse_daily_fortune_response
        )
    
    def get_available_prompt_types(self) -> List[PromptType]:
        """获取所有可用的提示词类型"""
        return PromptConfig.get_all_prompt_types()
    
    def get_prompt_info(self, prompt_type: PromptType) -> Dict[str, str]:
        """获取提示词信息"""
        return PromptConfig.get_prompt_info(prompt_type)
    
    def _parse_blueprint_response(self, ai_content: str) -> Dict[str, Any]:
        """解析算命结果响应"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回原始内容
        return {
            "raw_content": ai_content,
            "parsed_at": datetime.now().isoformat()
        }
    
    def _parse_blueprint_quick_response(self, ai_content: str) -> Dict[str, Any]:
        """解析快速五行计算结果响应"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回原始内容
        return {
            "raw_content": ai_content,
            "parsed_at": datetime.now().isoformat()
        }
    
    def _parse_blueprint_complete_response(self, ai_content: str) -> Dict[str, Any]:
        """解析完整蓝图响应"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回原始内容
        return {
            "raw_content": ai_content,
            "parsed_at": datetime.now().isoformat()
        }
    
    def _parse_heart_compass_response(self, ai_content: str) -> Dict[str, Any]:
        """解析 Heart Compass 响应"""
        # 直接返回AI内容，让业务服务进行解析
        return ai_content
    
    def _parse_daily_fortune_response(self, ai_content: str) -> Dict[str, Any]:
        """解析每日运势响应"""
        # 直接返回AI内容，让业务服务进行解析
        return ai_content
