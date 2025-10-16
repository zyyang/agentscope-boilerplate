# -*- coding: utf-8 -*-
"""Logging configuration."""
import logging
import os
import sys


def setup_logging():
    """设置日志配置."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 可选：添加文件处理器
    log_file = os.getenv("LOG_FILE")
    if log_file:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Logging configured with level: {log_level}")