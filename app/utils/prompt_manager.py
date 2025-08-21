import os
from pathlib import Path
from typing import Dict, List, Optional, Any

class PromptManager:
    """提示词管理器，负责读取和组合 prompt 文件"""
    
    def __init__(self):
        """初始化提示词管理器"""
        # 获取 prompts 文件夹路径
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self._cache = {}  # 缓存读取的文件内容
    
    def _read_prompt_file(self, filename: str) -> str:
        """
        读取指定的 prompt 文件
        
        Args:
            filename: 文件名（如 'blueprint.md'）
            
        Returns:
            str: 文件内容
        """
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
            print(f"读取 prompt 文件 {filename} 失败: {e}")
            return ""
    
    def get_complete_prompt(self, prompt_type: str, context: Dict[str, Any] = None) -> str:
        """
        获取完整的系统提示词
        
        Args:
            prompt_type: 提示词类型 ('blueprint', 'heart_compass', 'daily_fortune')
            context: 上下文信息，用于动态替换占位符
            
        Returns:
            str: 完整的系统提示词
        """
        # 根据类型获取对应的提示词模板
        base_prompt = self._read_prompt_file(f"{prompt_type}.md")
        
        # 如果有上下文信息，进行动态替换
        if context and base_prompt:
            base_prompt = self._replace_placeholders(base_prompt, context)
        
        return base_prompt
    
    def get_prompt_by_filename(self, filename: str, context: Dict[str, Any] = None) -> str:
        """
        根据文件名获取提示词
        
        Args:
            filename: 文件名（如 'blueprint_minimal.md'）
            context: 上下文信息，用于动态替换占位符
            
        Returns:
            str: 完整的系统提示词
        """
        base_prompt = self._read_prompt_file(filename)
        
        # 如果有上下文信息，进行动态替换
        if context and base_prompt:
            base_prompt = self._replace_placeholders(base_prompt, context)
        
        return base_prompt
    
    def _replace_placeholders(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        替换提示词中的占位符
        
        Args:
            prompt: 原始提示词
            context: 上下文信息
            
        Returns:
            str: 替换后的提示词
        """
        try:
            for key, value in context.items():
                placeholder = f"${{{key}}}"
                prompt = prompt.replace(placeholder, str(value))
            return prompt
        except Exception as e:
            print(f"替换占位符失败: {e}")
            return prompt
    
    def get_available_prompts(self) -> List[str]:
        """
        获取可用的提示词类型列表
        
        Returns:
            List[str]: 可用的提示词类型
        """
        try:
            prompt_files = list(self.prompts_dir.glob("*.md"))
            return [f.stem for f in prompt_files]
        except Exception as e:
            print(f"获取可用提示词失败: {e}")
            return []
    
    def clear_cache(self):
        """清空提示词缓存"""
        self._cache.clear()
        print("提示词缓存已清空")
    
    def reload_prompt(self, filename: str):
        """
        重新加载指定的提示词文件
        
        Args:
            filename: 文件名
        """
        if filename in self._cache:
            del self._cache[filename]
            print(f"提示词 {filename} 已重新加载")

# 创建全局实例
prompt_manager = PromptManager()
