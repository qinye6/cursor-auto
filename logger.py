import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style, init
import sys

# 初始化colorama
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """自定义彩色日志格式器"""
    
    COLORS = {
        'DEBUG': Fore.GREEN + '🟢',
        'INFO': Fore.BLUE + '🔵',
        'WARNING': Fore.YELLOW + '🟡',
        'ERROR': Fore.RED + '🔴',
        'CRITICAL': Fore.RED + '💀'
    }

    def format(self, record):
        # 为不同级别添加颜色和表情
        if record.levelname in self.COLORS:
            # 移除重复的 cursor_auto: 前缀
            if record.name == 'cursor_auto':
                record.msg = record.msg.replace('cursor_auto:', '')
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}"
        return super().format(record)

def setup_logger(name='cursor_auto'):
    """设置日志系统"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # 清除现有的处理器
    logger.handlers = []
    
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 设置运行日志
    runtime_log_path = os.path.join(log_dir, f"runtime_{timestamp}.log")
    try:
        runtime_handler = RotatingFileHandler(
            filename=runtime_log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8',
            mode='a'  # 追加模式
        )
        runtime_handler.setLevel(logging.DEBUG)
        runtime_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        runtime_handler.setFormatter(runtime_formatter)
        logger.addHandler(runtime_handler)
        
    except Exception as e:
        print(f"设置运行日志时出错: {str(e)}")
    
    # 设置构建日志
    build_log_path = os.path.join(log_dir, f"build_{timestamp}.log")
    try:
        build_handler = RotatingFileHandler(
            filename=build_log_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8',
            mode='a'  # 追加模式
        )
        build_handler.setLevel(logging.INFO)
        build_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        build_handler.setFormatter(build_formatter)
        logger.addHandler(build_handler)
        
    except Exception as e:
        print(f"设置构建日志时出错: {str(e)}")
    
    # 设置控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_formatter = ColoredFormatter('%(levelname)s %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 防止日志向上传播
    logger.propagate = False
    
    return logger

# 创建全局logger实例
logger = setup_logger()

def log_function_call(func):
    """函数调用日志装饰器"""
    def wrapper(*args, **kwargs):
        logger.debug(f"进入函数: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"退出函数: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行出错: {str(e)}", exc_info=True)
            raise
    return wrapper

@log_function_call
def main_task():
    """
    Main task execution function. Simulates a workflow and handles errors.
    """
    try:
        logger.info("Starting the main task...")

        # Simulated task and error condition
        if some_condition():
            raise ValueError("Simulated error occurred.")

        logger.info("Main task completed successfully.")

    except ValueError as ve:
        logger.error(f"ValueError occurred: {ve}", exc_info=True)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Task execution finished.")

def some_condition():
    """
    Simulates an error condition. Returns True to trigger an error.
    Replace this logic with actual task conditions.
    """
    return True

if __name__ == "__main__":
    # 测试日志功能
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
