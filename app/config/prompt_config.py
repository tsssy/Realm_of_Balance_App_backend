"""
提示词配置文件
定义所有可用的提示词类型和映射关系
"""

from enum import Enum
from typing import Dict, List, Optional

class PromptType(str, Enum):
    """提示词类型枚举"""
    BLUEPRINT = "blueprint"           # 算命分析
    HEART_COMPASS = "heart_compass"   # Heart Compass 指导
    DAILY_FORTUNE = "daily_fortune"   # 每日运势

class PromptConfig:
    """提示词配置管理类"""
    
    # 提示词类型到文件名的映射
    PROMPT_FILE_MAPPING = {
        PromptType.BLUEPRINT: "blueprint.md",
        PromptType.HEART_COMPASS: "heart_compass.md", 
        PromptType.DAILY_FORTUNE: "daily_fortune.md"
    }
    
    # 提示词类型到解析函数的映射
    PARSER_FUNCTION_MAPPING = {
        PromptType.BLUEPRINT: "_parse_blueprint_response",
        PromptType.HEART_COMPASS: "_parse_heart_compass_response",
        PromptType.DAILY_FORTUNE: "_parse_daily_fortune_response"
    }
    
    # 提示词类型到业务服务的映射
    SERVICE_MAPPING = {
        PromptType.BLUEPRINT: "blueprint_service",
        PromptType.HEART_COMPASS: "heart_compass_service",
        PromptType.DAILY_FORTUNE: "daily_fortune_service"
    }
    
    # 提示词类型到API路由的映射
    API_ROUTE_MAPPING = {
        PromptType.BLUEPRINT: "/blueprint",
        PromptType.HEART_COMPASS: "/heart-compass",
        PromptType.DAILY_FORTUNE: "/daily-fortune"
    }
    
    @classmethod
    def get_prompt_filename(cls, prompt_type: PromptType) -> str:
        """获取提示词文件名"""
        return cls.PROMPT_FILE_MAPPING.get(prompt_type, "")
    
    @classmethod
    def get_parser_function(cls, prompt_type: PromptType) -> str:
        """获取解析函数名"""
        return cls.PARSER_FUNCTION_MAPPING.get(prompt_type, "")
    
    @classmethod
    def get_service_name(cls, prompt_type: PromptType) -> str:
        """获取业务服务名"""
        return cls.SERVICE_MAPPING.get(prompt_type, "")
    
    @classmethod
    def get_api_route(cls, prompt_type: PromptType) -> str:
        """获取API路由"""
        return cls.API_ROUTE_MAPPING.get(prompt_type, "")
    
    @classmethod
    def get_all_prompt_types(cls) -> List[PromptType]:
        """获取所有提示词类型"""
        return list(PromptType)
    
    @classmethod
    def is_valid_prompt_type(cls, prompt_type: str) -> bool:
        """检查提示词类型是否有效"""
        try:
            PromptType(prompt_type)
            return True
        except ValueError:
            return False
    
    @classmethod
    def get_prompt_info(cls, prompt_type: PromptType) -> Dict[str, str]:
        """获取提示词完整信息"""
        return {
            "type": prompt_type.value,
            "filename": cls.get_prompt_filename(prompt_type),
            "parser_function": cls.get_parser_function(prompt_type),
            "service": cls.get_service_name(prompt_type),
            "api_route": cls.get_api_route(prompt_type)
        }

# 提示词类型描述
PROMPT_DESCRIPTIONS = {
    PromptType.BLUEPRINT: {
        "name": "算命分析",
        "description": "基于用户出生信息生成八字排盘、五行分析和内在蓝图",
        "output_format": "结构化的算命结果，包含八字、五行、性格分析等"
    },
    PromptType.HEART_COMPASS: {
        "name": "Heart Compass 指导", 
        "description": "基于易经64卦为用户提供决策指导和人生建议",
        "output_format": "包含卦象信息、对话流和决策协议的结构化指导"
    },
    PromptType.DAILY_FORTUNE: {
        "name": "每日运势",
        "description": "为用户生成个性化的每日运势分析",
        "output_format": "包含卦象、时段建议、幸运元素和个性化建议"
    }
}

# 提示词配置验证
def validate_prompt_config():
    """验证提示词配置的完整性"""
    errors = []
    
    for prompt_type in PromptType:
        # 检查文件名映射
        if not PromptConfig.get_prompt_filename(prompt_type):
            errors.append(f"缺少 {prompt_type.value} 的文件名映射")
        
        # 检查解析函数映射
        if not PromptConfig.get_parser_function(prompt_type):
            errors.append(f"缺少 {prompt_type.value} 的解析函数映射")
        
        # 检查服务映射
        if not PromptConfig.get_service_name(prompt_type):
            errors.append(f"缺少 {prompt_type.value} 的服务映射")
    
    if errors:
        raise ValueError(f"提示词配置验证失败: {'; '.join(errors)}")
    
    return True

# 初始化时验证配置
try:
    validate_prompt_config()
except ValueError as e:
    print(f"警告: {e}")
