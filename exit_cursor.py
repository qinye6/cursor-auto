import psutil
from logger import logging
import time
import os
from config import Config
from colorama import Fore, Style

def StartCursor():
    """启动 Cursor"""
    try:
        config = Config()
        if not config.get('cursor.auto_start', True):
            return False

        cursor_path = config.get('cursor.path', '')
        # 替换环境变量
        cursor_path = os.path.expandvars(cursor_path)
        
        if not os.path.exists(cursor_path):
            logging.error(f"Cursor 路径不存在: {cursor_path}")
            return False

        print(f"\n{Fore.CYAN}🚀 正在启动 Cursor...{Style.RESET_ALL}")
        os.startfile(cursor_path)
        
        # 等待进程启动
        max_wait = 30  # 最大等待时间（秒）
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == 'cursor.exe':
                    print(f"{Fore.GREEN}✅ Cursor 已成功启动{Style.RESET_ALL}")
                    return True
            time.sleep(1)
            
        logging.error("Cursor 启动超时")
        return False
        
    except Exception as e:
        logging.error(f"启动 Cursor 失败: {str(e)}")
        return False

def ExitCursor(timeout=5):
    """退出 Cursor"""
    try:
        print(f"\n{Fore.CYAN}正在退出Cursor...{Style.RESET_ALL}")
        cursor_processes = []
        
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == 'cursor.exe':
                cursor_processes.append(proc)
                
        if not cursor_processes:
            print(f"{Fore.CYAN}未发现运行中的 Cursor 进程{Style.RESET_ALL}")
            return True
            
        # 尝试正常关闭进程
        for proc in cursor_processes:
            proc.terminate()
            
        # 等待进程结束
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not any(proc.is_running() for proc in cursor_processes):
                print(f"{Fore.GREEN}所有 Cursor 进程已正常关闭{Style.RESET_ALL}")
                return True
            time.sleep(0.5)
            
        # 强制结束未响应的进程
        for proc in cursor_processes:
            if proc.is_running():
                proc.kill()
                
        print(f"{Fore.GREEN}所有 Cursor 进程已强制关闭{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        logging.error(f"退出 Cursor 失败: {str(e)}")
        return False

if __name__ == "__main__":
    ExitCursor()
