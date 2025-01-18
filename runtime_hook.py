import sys
import os
import ctypes
from colorama import init

def setup_terminal():
    """配置终端显示"""
    # 启用 ANSI 转义序列
    init(wrap=False)
    
    # 获取标准输出句柄
    handle = ctypes.windll.kernel32.GetStdHandle(-11)
    
    try:
        # 设置终端模式
        mode = ctypes.c_ulong()
        ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        ctypes.windll.kernel32.SetConsoleMode(handle, mode)
        
        # 设置窗口标题
        ctypes.windll.kernel32.SetConsoleTitleW("Cursor Pro Keep Alive")
        
        # 配置终端编码和字体
        os.system('chcp 65001 >nul 2>nul')
        os.system('REG ADD "HKEY_CURRENT_USER\\Console" /v "FaceName" /t REG_SZ /d "Cascadia Code" /f >nul 2>nul')
        
        # 设置窗口大小和缓冲区大小
        window_width = 120
        window_height = 30
        buffer_height = 3000  # 增加缓冲区高度以支持滚动
        
        # 先设置缓冲区大小
        os.system(f'mode con: cols={window_width} lines={buffer_height}')
        
        # 然后设置窗口大小
        kernel32 = ctypes.windll.kernel32
        coord = ctypes.wintypes._COORD(window_width, window_height)
        kernel32.SetConsoleScreenBufferSize(handle, coord)
        
        # 配置输出流
        sys.stdout.reconfigure(encoding='utf-8')
        
        # 设置背景色和清屏
        os.system('cls')
        sys.stdout.write("\x1b[40m")  # 黑色背景
        sys.stdout.write("\x1b[37m")  # 白色文字
        sys.stdout.write("\x1b[?25h")  # 显示光标
        sys.stdout.flush()
        
    except Exception as e:
        print(f"终端配置失败: {str(e)}")

setup_terminal() 