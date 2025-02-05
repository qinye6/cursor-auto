import os
import sys
import psutil
import time
import subprocess
from colorama import Fore, Style
import logging

logger = logging.getLogger(__name__)

def ExitCursor():
    """关闭所有 Cursor 进程"""
    try:
        cursor_killed = False
        killed_count = 0
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 检查进程名称
                if proc.info['name'].lower() in ['cursor.exe', 'cursor']:
                    proc.kill()
                    cursor_killed = True
                    killed_count += 1
                    # 使用 debug 级别记录详细信息
                    logger.debug(f"已终止 Cursor 进程: PID {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            
        if cursor_killed:
            # 只在终端显示简单信息，详细信息记录到日志
            print(f"{Fore.GREEN}✅ 已关闭 Cursor 进程{Style.RESET_ALL}")
            logger.debug(f"成功关闭 {killed_count} 个 Cursor 进程")
            time.sleep(1)  # 给进程一些时间完全关闭
        else:
            print(f"{Fore.YELLOW}ℹ️ 未发现运行中的 Cursor 进程{Style.RESET_ALL}")
            logger.debug("未发现运行中的 Cursor 进程")
            
    except Exception as e:
        print(f"{Fore.RED}❌ 关闭 Cursor 进程时出错: {str(e)}{Style.RESET_ALL}")
        logger.error(f"关闭 Cursor 进程失败: {e}")

def StartCursor(cursor_path=None):
    """启动 Cursor"""
    try:
        # 如果没有提供路径，尝试使用默认路径
        if not cursor_path:
            if sys.platform.startswith('win'):
                cursor_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'Cursor', 'Cursor.exe')
            else:  # macOS
                cursor_path = '/Applications/Cursor.app'

        if not os.path.exists(cursor_path):
            error_msg = f"Cursor 可执行文件未找到: {cursor_path}"
            print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
            logger.error(error_msg)
            return False

        # 使用 subprocess 启动 Cursor
        if sys.platform.startswith('win'):
            subprocess.Popen([cursor_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.Popen(['open', cursor_path])

        success_msg = "Cursor 已启动"
        print(f"{Fore.GREEN}✅ {success_msg}{Style.RESET_ALL}")
        logger.debug(success_msg)  # 改用 debug 级别记录
        return True

    except Exception as e:
        error_msg = f"启动 Cursor 失败: {str(e)}"
        print(f"{Fore.RED}❌ {error_msg}{Style.RESET_ALL}")
        logger.error(error_msg)
        return False

if __name__ == "__main__":
    ExitCursor()
