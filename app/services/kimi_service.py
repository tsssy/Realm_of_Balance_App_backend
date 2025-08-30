#!/usr/bin/env python3
"""
Kimi AI服务
完全按照Gemini服务的架构，只是换个模型
"""

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

logger = MyLogger("kimi_service")

class KimiInteractionAPI:
    """与 Kimi 模型进行交互的 API 封装 - 完全按照Gemini的架构"""
    
    def __init__(self):
        self.api_key = settings.KIMI_API_KEY  # 从配置中读取 Kimi API 密钥
        self.api_url = "https://api.moonshot.cn/v1/chat/completions"
        self.model_name = "moonshot-v1-8k"  # 使用Kimi的8k上下文模型
        self.max_retries = 3  # 最大重试次数
        self.timeout = 60  # 请求超时时间（秒）
        
        if not self.api_key:
            logger.error("Kimi API KEY 未设置")
            raise ValueError("Kimi API KEY 未设置")
    
    async def send_message_to_ai(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """向 Kimi API 发送消息并获取响应 - 完全按照Gemini的架构"""
        try:
            # 构建请求数据
            request_data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 1000  # 修正：合理的输出token限制
            }
            
            # 记录发送给Kimi的完整数据
            logger.info(f"=== 向Kimi发送数据开始 ===")
            logger.info(f"完整提示词内容: {prompt}")
            logger.info(f"请求数据: {request_data}")
            logger.info(f"=== 向Kimi发送数据结束 ===")
            
            # 发送 API 请求（包含重试机制）
            response_json = await self._make_api_request(request_data)
            
            # 记录Kimi的完整响应
            logger.info(f"=== Kimi完整响应开始 ===")
            logger.info(f"原始响应JSON: {response_json}")
            logger.info(f"=== Kimi完整响应结束 ===")
            
            # 解析响应
            if 'choices' in response_json and len(response_json['choices']) > 0:
                choice = response_json['choices'][0]
                
                logger.info(f"=== Kimi响应候选者信息 ===")
                logger.info(f"候选者数据: {choice}")
                logger.info(f"完成原因: {choice.get('finish_reason')}")
                logger.info(f"=== Kimi响应候选者信息结束 ===")
                
                if 'message' in choice and 'content' in choice['message']:
                    ai_content = choice['message']['content']
                    
                    logger.info(f"=== 提取的AI响应文本 ===")
                    logger.info(f"AI响应内容: {ai_content}")
                    logger.info(f"=== 提取的AI响应文本结束 ===")
                    
                    return {
                        'success': True,
                        'message': ai_content
                    }
            
            # 如果没有找到预期的响应格式，记录响应内容并返回错误
            logger.error(f"=== Kimi响应格式异常 ===")
            logger.error(f"响应格式异常详情: {response_json}")
            logger.error(f"=== Kimi响应格式异常结束 ===")
            raise Exception(f"API 响应格式错误: {response_json}")
            
        except Exception as e:
            logger.error(f'=== Kimi API 调用失败 ===')
            logger.error(f'错误详情: {e}')
            logger.error(f'=== Kimi API 调用失败结束 ===')
            return await self.get_fallback_response()
    
    async def _make_api_request(self, request_data: dict) -> dict:
        """向 Kimi API 发送请求（包含重试机制） - 完全按照Gemini的架构"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 记录API请求详情
        logger.info(f"=== Kimi API请求详情 ===")
        logger.info(f"请求URL: {self.api_url}")
        logger.info(f"请求头: {headers}")
        logger.info(f"超时设置: {self.timeout}秒")
        logger.info(f"=== Kimi API请求详情结束 ===")
        
        # 重试机制
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                logger.info(f"=== 第{retry_count + 1}次API请求 ===")
                response = requests.post(
                    self.api_url, 
                    json=request_data, 
                    headers=headers, 
                    timeout=self.timeout
                )
                
                logger.info(f"HTTP状态码: {response.status_code}")
                logger.info(f"响应头: {dict(response.headers)}")
                logger.info(f"=== 第{retry_count + 1}次API请求结束 ===")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # API配额不足
                    error_detail = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                    logger.error(f"Kimi API配额不足: {error_detail}")
                    raise Exception(f"Kimi API配额不足，请检查账户余额")
                else:
                    # 获取详细错误信息
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        logger.error(f"Kimi API错误详情: {error_json}")
                        if 'error' in error_json:
                            raise Exception(f"Kimi API错误: {error_json['error']}")
                    except:
                        pass
                    logger.error(f"Kimi API HTTP错误: {response.status_code} - {error_detail}")
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                retry_count += 1
                logger.warning(f"第 {retry_count} 次请求超时，重试中...")
                if retry_count >= self.max_retries:
                    raise Exception(f"请求超时，已重试 {self.max_retries} 次")
                await asyncio.sleep(2 ** retry_count)  # 指数退避
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.warning(f"第 {retry_count} 次请求失败: {e}")
                if retry_count >= self.max_retries:
                    raise Exception(f"请求失败，已重试 {self.max_retries} 次: {e}")
                await asyncio.sleep(2 ** retry_count)  # 指数退避
                
            except Exception as e:
                retry_count += 1
                logger.error(f"第 {retry_count} 次请求异常: {e}")
                if retry_count >= self.max_retries:
                    raise Exception(f"请求异常，已重试 {self.max_retries} 次: {e}")
                await asyncio.sleep(2 ** retry_count)  # 指数退避
    
    async def get_fallback_response(self) -> Dict[str, Any]:
        """获取兜底响应 - 完全按照Gemini的架构"""
        logger.info("=== 使用Kimi兜底响应 ===")
        return {
            'success': False,
            'message': 'Kimi API 调用失败，请稍后重试'
        }


class KimiService:
    """Kimi AI服务类 - 完全按照AIService的架构"""
    
    def __init__(self):
        self.kimi_api = KimiInteractionAPI()
    
    async def cleanup(self):
        """清理资源"""
        # Kimi API使用requests，无需特殊清理
        pass
    
    async def generate_with_prompt(
        self, 
        prompt_type: PromptType, 
        context: Dict[str, Any],
        parse_response_func: callable = None
    ) -> Dict[str, Any]:
        """
        通用Kimi生成方法，支持动态提示词选择 - 完全按照AIService的架构
        
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
            logger.info(f"=== Kimi提示词准备完成 ===")
            logger.info(f"提示词类型: {prompt_type.value}")
            logger.info(f"提示词文件: {PromptConfig.get_prompt_filename(prompt_type)}")
            logger.info(f"最终提示词内容: {prompt[:500]}..." if len(prompt) > 500 else f"最终提示词内容: {prompt}")
            logger.info(f"=== Kimi提示词准备完成结束 ===")
            
            # 调用 Kimi 服务
            response = await self.kimi_api.send_message_to_ai(prompt, context)
            
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
            logger.error(f"Kimi 生成失败 ({prompt_type.value}): {e}")
            return {
                "success": False,
                "message": f"Kimi 生成失败: {str(e)}"
            }
    
    async def generate_blueprint_quick(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """快速生成五行蓝图 - 完全按照AIService的架构"""
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
            logger.error(f"Kimi快速生成五行结果失败: {e}")
            return {
                "success": False,
                "message": f"Kimi快速生成五行结果失败: {str(e)}"
            }

    async def generate_blueprint_complete(self, user_profile: Dict[str, Any], quick_result: Dict[str, Any]) -> Dict[str, Any]:
        """基于五行结果生成完整蓝图 - 完全按照AIService的架构"""
        try:
            # 构建上下文信息，包含五行结果
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
            logger.error(f"Kimi完整蓝图生成失败: {e}")
            return {
                "success": False,
                "message": f"Kimi完整蓝图生成失败: {str(e)}"
            }

    async def seek_heart_compass_guidance(self, question: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """获取 Heart Compass 指导 - 完全按照AIService的架构"""
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
        """生成每日运势 - 完全按照AIService的架构"""
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
        """获取所有可用的提示词类型 - 与AIService保持一致"""
        return PromptConfig.get_all_prompt_types()
    
    def get_prompt_info(self, prompt_type: PromptType) -> Dict[str, str]:
        """获取提示词信息 - 与AIService保持一致"""
        return PromptConfig.get_prompt_info(prompt_type)
    
    def _parse_blueprint_quick_response(self, ai_content: str) -> Dict[str, Any]:
        """解析快速五行计算结果响应 - 与AIService保持一致"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回原始内容
        return {
            "raw_content": ai_content,
            "parsed_at": datetime.now().isoformat()
        }
    
    def _parse_blueprint_complete_response(self, ai_content: str) -> Dict[str, Any]:
        """解析完整蓝图响应 - 与AIService保持一致"""
        # 这里应该实现具体的解析逻辑
        # 简化实现，返回原始内容
        return {
            "raw_content": ai_content,
            "parsed_at": datetime.now().isoformat()
        }
    
    def _parse_heart_compass_response(self, ai_content: str) -> Dict[str, Any]:
        """解析 Heart Compass 响应 - 与AIService保持一致"""
        # 直接返回AI内容，让业务服务进行解析
        return ai_content
    
    def _parse_daily_fortune_response(self, ai_content: str) -> Dict[str, Any]:
        """解析每日运势响应 - 与AIService保持一致"""
        # 直接返回AI内容，让业务服务进行解析
        return ai_content


# 单例模式
_kimi_service_instance: Optional[KimiService] = None

async def get_kimi_service() -> KimiService:
    global _kimi_service_instance
    if _kimi_service_instance is None:
        _kimi_service_instance = KimiService()
    return _kimi_service_instance
