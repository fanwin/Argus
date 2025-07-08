"""
日志记录工具类
使用loguru库提供统一的日志记录功能
"""

import os
import sys
from pathlib import Path
from loguru import logger
from typing import Optional


class Logger:
    """日志记录器类"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志记录器"""
        if not self._initialized:
            self._setup_logger()
            self._initialized = True
    
    def _setup_logger(self):
        """设置日志记录器"""
        # 移除默认的控制台处理器
        logger.remove()
        
        # 确保reports目录存在
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # 添加文件处理器
        logger.add(
            "reports/test.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            encoding="utf-8"
        )
    
    def configure_from_config(self, config: dict):
        """根据配置文件配置日志"""
        if "logging" not in config:
            return
            
        log_config = config["logging"]
        
        # 移除现有处理器
        logger.remove()
        
        # 重新配置控制台处理器
        logger.add(
            sys.stdout,
            format=log_config.get("format", 
                                 "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                                 "<level>{level: <8}</level> | "
                                 "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                                 "<level>{message}</level>"),
            level=log_config.get("level", "INFO"),
            colorize=True
        )
        
        # 重新配置文件处理器
        log_file = log_config.get("file", "reports/test.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logger.add(
            log_file,
            format=log_config.get("format", 
                                 "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"),
            level="DEBUG",
            rotation=log_config.get("rotation", "10 MB"),
            retention=log_config.get("retention", "7 days"),
            compression="zip",
            encoding="utf-8"
        )
    
    def get_logger(self, name: Optional[str] = None):
        """获取日志记录器实例"""
        if name:
            return logger.bind(name=name)
        return logger
    
    def info(self, message: str, **kwargs):
        """记录信息日志"""
        logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """记录调试日志"""
        logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录警告日志"""
        logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """记录错误日志"""
        logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """记录严重错误日志"""
        logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """记录异常日志"""
        logger.exception(message, **kwargs)


# 创建全局日志实例
log = Logger()

# 导出常用方法
info = log.info
debug = log.debug
warning = log.warning
error = log.error
critical = log.critical
exception = log.exception
