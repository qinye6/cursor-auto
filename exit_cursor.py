import psutil
from logger import logger
import time
import os
import subprocess
import signal
import sys
import ctypes
from ctypes import wintypes
import win32con
import win32process
import win32gui

def get_cursor_windows():
    """获取所有 Cursor 窗口句柄"""
    result = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'cursor' in title.lower():
                result.append(hwnd)
    win32gui.EnumWindows(callback, None)
    return result

def close_window_gracefully(hwnd):
    """优雅地关闭窗口"""
    try:
        # 发送关闭消息
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        time.sleep(0.5)  # 等待窗口响应
        
        # 检查窗口是否还存在
        if win32gui.IsWindow(hwnd):
            # 如果窗口还在，强制结束
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid:
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.debug(f"关闭窗口时出错: {str(e)}")

def ExitCursor():
    """退出所有 Cursor 进程"""
    try:
        # 首先尝试优雅地关闭窗口
        cursor_windows = get_cursor_windows()
        for hwnd in cursor_windows:
            close_window_gracefully(hwnd)
        
        # 然后确保所有进程都被终止
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name'].lower()
                if 'cursor' in process_name:
                    # 使用 taskkill 强制结束进程，但重定向输出
                    subprocess.run(
                        ['taskkill', '/F', '/PID', str(proc.pid)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(0.5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"结束进程时出错: {str(e)}")
        
        time.sleep(1)  # 等待所有进程完全退出
        return True
        
    except Exception as e:
        logger.error(f"退出 Cursor 时出错: {str(e)}")
        return False

def StartCursor(cursor_path=None):
    """启动 Cursor
    
    Args:
        cursor_path (str, optional): Cursor 可执行文件的路径. 
            如果未提供，将使用默认路径.
    """
    try:
        # 如果未提供路径，使用默认路径
        if not cursor_path:
            if os.name == "nt":  # Windows
                cursor_path = os.path.join(os.getenv("LOCALAPPDATA"), "Programs", "Cursor", "Cursor.exe")
            else:  # macOS
                cursor_path = "/Applications/Cursor.app"
        
        # 检查文件是否存在
        if not os.path.exists(cursor_path):
            logger.error(f"Cursor 可执行文件不存在: {cursor_path}")
            return False
            
        # 启动 Cursor（使用新的方式启动以避免显示错误信息）
        if os.name == "nt":  # Windows
            # 使用 CREATE_NO_WINDOW 标志来隐藏控制台窗口
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                [cursor_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:  # macOS
            process = subprocess.Popen(
                ['open', cursor_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
        time.sleep(2)  # 等待启动
        return True
        
    except Exception as e:
        logger.error(f"启动 Cursor 时出错: {str(e)}")
        return False

if __name__ == "__main__":
    ExitCursor()
