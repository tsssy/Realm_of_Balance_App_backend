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
        print(f"=== 读取提示词文件 ===")
        print(f"文件名: {filename}")
        print(f"缓存中是否存在: {filename in self._cache}")
        
        if filename in self._cache:
            print(f"从缓存返回: {self._cache[filename][:100]}...")
            return self._cache[filename]
        
        file_path = self.prompts_dir / filename
        print(f"文件路径: {file_path}")
        print(f"文件是否存在: {file_path.exists()}")
        
        if not file_path.exists():
            print(f"文件不存在: {file_path}")
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"文件内容长度: {len(content)}")
                print(f"文件内容前100字符: {content[:100]}")
                self._cache[filename] = content
                print(f"已缓存到: {filename}")
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
        print(f"=== 获取提示词文件 ===")
        print(f"文件名: {filename}")
        print(f"上下文信息: {context}")
        
        base_prompt = self._read_prompt_file(filename)
        
        print(f"原始提示词内容: {base_prompt[:200]}..." if len(base_prompt) > 200 else f"原始提示词内容: {base_prompt}")
        
        # 如果有上下文信息，进行动态替换
        if context and base_prompt:
            base_prompt = self._replace_placeholders(base_prompt, context)
            print(f"替换后的提示词内容: {base_prompt[:200]}..." if len(base_prompt) > 200 else f"替换后的提示词内容: {base_prompt}")
        
        print(f"=== 获取提示词文件结束 ===")
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
        print(f"=== 开始替换占位符 ===")
        print(f"原始提示词长度: {len(prompt)}")
        print(f"上下文信息: {context}")
        
        try:
            for key, value in context.items():
                placeholder = f"${{{key}}}"
                print(f"查找占位符: {placeholder}")
                print(f"替换值: {value}")
                
                if placeholder in prompt:
                    prompt = prompt.replace(placeholder, str(value))
                    print(f"占位符 {placeholder} 替换成功")
                else:
                    print(f"占位符 {placeholder} 在提示词中未找到")
            
            print(f"替换后提示词长度: {len(prompt)}")
            print(f"=== 占位符替换完成 ===")
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
