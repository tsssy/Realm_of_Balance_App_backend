#!/usr/bin/env python3
"""
OpenAI GPT-4o-mini AI服务
完全按照Gemini服务的架构，只是换个模型
"""

import os
import asyncio
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from app.config import settings
from app.utils.logger import MyLogger
from app.utils.prompt_manager import prompt_manager

logger = MyLogger("openai_service")

class OpenAIInteractionAPI:
    """与 OpenAI GPT-4o-mini 模型进行交互的 API 封装 - 完全按照Gemini的架构"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY  # 从配置中读取 OpenAI API 密钥
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model_name = "gpt-4o-mini"
        self.max_retries = 3  # 最大重试次数
        self.timeout = 60  # 请求超时时间（秒）
        
        if not self.api_key:
            logger.error("OpenAI API KEY 未设置")
            raise ValueError("OpenAI API KEY 未设置")
    
    async def send_message_to_ai(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """向 OpenAI API 发送消息并获取响应 - 完全按照Gemini的架构"""
        try:
            # 构建请求数据
            request_data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 8192
            }
            
            # 记录发送给OpenAI的完整数据
            logger.info(f"=== 向OpenAI发送数据开始 ===")
            logger.info(f"完整提示词内容: {prompt}")
            logger.info(f"请求数据: {request_data}")
            logger.info(f"=== 向OpenAI发送数据结束 ===")
            
            # 发送 API 请求（包含重试机制）
            response_json = await self._make_api_request(request_data)
            
            # 记录OpenAI的完整响应
            logger.info(f"=== OpenAI完整响应开始 ===")
            logger.info(f"原始响应JSON: {response_json}")
            logger.info(f"=== OpenAI完整响应结束 ===")
            
            # 解析响应
            if 'choices' in response_json and len(response_json['choices']) > 0:
                choice = response_json['choices'][0]
                
                logger.info(f"=== OpenAI响应候选者信息 ===")
                logger.info(f"候选者数据: {choice}")
                logger.info(f"完成原因: {choice.get('finish_reason')}")
                logger.info(f"=== OpenAI响应候选者信息结束 ===")
                
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
            logger.error(f"=== OpenAI响应格式异常 ===")
            logger.error(f"响应格式异常详情: {response_json}")
            logger.error(f"=== OpenAI响应格式异常结束 ===")
            raise Exception(f"API 响应格式错误: {response_json}")
            
        except Exception as e:
            logger.error(f'=== OpenAI API 调用失败 ===')
            logger.error(f'错误详情: {e}')
            logger.error(f'=== OpenAI API 调用失败结束 ===')
            return await self.get_fallback_response()
    
    async def _make_api_request(self, request_data: dict) -> dict:
        """向 OpenAI API 发送请求（包含重试机制） - 完全按照Gemini的架构"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 记录API请求详情
        logger.info(f"=== OpenAI API请求详情 ===")
        logger.info(f"请求URL: {self.api_url}")
        logger.info(f"请求头: {headers}")
        logger.info(f"超时设置: {self.timeout}秒")
        logger.info(f"=== OpenAI API请求详情结束 ===")
        
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
                    logger.error(f"OpenAI API配额不足: {error_detail}")
                    raise Exception(f"OpenAI API配额不足，请检查账户余额")
                else:
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
        logger.info("=== 使用OpenAI兜底响应 ===")
        return {
            'success': False,
            'message': 'OpenAI API 调用失败，请稍后重试'
        }


class OpenAIService:
    """OpenAI AI服务类 - 完全按照AIService的架构"""
    
    def __init__(self):
        self.openai_api = OpenAIInteractionAPI()
    
    async def generate_with_prompt(self, prompt_file: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用提示词生成AI响应 - 完全按照AIService的架构"""
        try:
            # 获取提示词
            prompt = prompt_manager.get_prompt_by_filename(prompt_file, context)
            
            # 调用OpenAI API
            response = await self.openai_api.send_message_to_ai(prompt, context)
            
            if response.get('success'):
                logger.info(f"OpenAI响应成功")
                return {
                    "success": True,
                    "ai_content": response.get('message', '')
                }
            else:
                logger.error(f"OpenAI响应失败: {response.get('message')}")
                return {
                    "success": False,
                    "message": response.get('message', 'OpenAI生成失败')
                }
                
        except Exception as e:
            logger.error(f"OpenAI服务生成失败: {e}")
            return {
                'success': False,
                'message': f"OpenAI服务错误: {str(e)}"
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
            
            return await self.generate_with_prompt("blueprint_quick_en.md", context)
        except Exception as e:
            logger.error(f"OpenAI快速生成五行结果失败: {e}")
            return {
                "success": False,
                "message": f"OpenAI快速生成五行结果失败: {str(e)}"
            }