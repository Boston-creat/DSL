"""
日志模块
作用：提供统一的日志记录功能，记录系统运行过程中的关键信息
在全项目中的作用：记录系统运行日志，便于调试和问题追踪
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "DSL_Agent", log_level: int = logging.INFO) -> logging.Logger:
    """
    设置并返回日志记录器
    
    :param name: 日志记录器名称
    :param log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    :return: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建logs目录
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # 日志文件路径（按日期命名）
    log_date = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"dsl_agent_{log_date}.log"
    
    # 文件处理器（带轮转，每个文件最大10MB，保留5个备份）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 日志格式
    # 格式：时间戳 | 级别 | 模块名 | 行号 | 消息
    log_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# 创建默认日志记录器
logger = setup_logger()

