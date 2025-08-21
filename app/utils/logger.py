import logging
import os
from datetime import datetime
from pathlib import Path

class MyLogger:
    """自定义日志管理器"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 创建文件处理器
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(
                f"logs/{name}.log", 
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # 设置日志格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            # 添加处理器
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def error(self, message: str, exc_info=False):
        """记录错误日志"""
        self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """记录严重错误日志"""
        self.logger.critical(message)
