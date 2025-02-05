from DrissionPage import ChromiumPage, ChromiumOptions
import os
import sys
import time
from colorama import Fore, Style
from config import Config
import logging

logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.BROWSERS = {
            'chrome': {
                'name': 'Chrome',
                'paths': [
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                ]
            },
            'edge': {
                'name': 'Microsoft Edge',
                'paths': [
                    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
                ]
            },
            'brave': {
                'name': 'Brave',
                'paths': [
                    r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe',
                ]
            },
        }

    def detect_browsers(self):
        """检测已安装的浏览器"""
        available_browsers = {}
        for browser_id, browser_info in self.BROWSERS.items():
            for path in browser_info['paths']:
                if os.path.exists(path):
                    available_browsers[browser_id] = {
                        'name': browser_info['name'],
                        'path': path
                    }
                    break
        return available_browsers

    def select_browser(self):
        """让用户选择浏览器"""
        available_browsers = self.detect_browsers()
        
        if not available_browsers:
            print(f"{Fore.RED}❌ 未检测到支持的浏览器{Style.RESET_ALL}")
            return None
            
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[可用浏览器]{Style.RESET_ALL}")
        
        browsers_list = list(available_browsers.items())
        for i, (browser_id, browser_info) in enumerate(browsers_list, 1):
            print(f"{i}. {Fore.GREEN}{browser_info['name']}{Style.RESET_ALL}")
            
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}请选择浏览器 (1-{len(browsers_list)}): {Style.RESET_ALL}")
                index = int(choice) - 1
                if 0 <= index < len(browsers_list):
                    return browsers_list[index][1]['path']
            except ValueError:
                pass
            print(f"{Fore.RED}❌ 无效的选择，请重试{Style.RESET_ALL}")

    def init_browser(self):
        """初始化浏览器"""
        try:
            print(f"\n{Fore.CYAN}🚀 正在启动浏览器...{Style.RESET_ALL}")
            
            # 创建配置对象
            co = ChromiumOptions()
            
            # 设置基本配置
            co.set_argument('--disable-gpu')
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-dev-shm-usage')
            co.set_argument('--disable-blink-features=AutomationControlled')
            
            # 设置用户代理
            co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 设置窗口大小
            co.set_argument('--window-size=1920,1080')
            
            # 创建浏览器实例
            self.browser = ChromiumPage()  # 不传递任何参数
            
            # 等待浏览器初始化
            time.sleep(2)
            
            print(f"{Fore.GREEN}✅ 浏览器启动成功{Style.RESET_ALL}")
            return self.browser
            
        except Exception as e:
            print(f"{Fore.RED}❌ 浏览器启动失败: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Browser initialization failed: {e}")
            return None

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
                print(f"\n{Fore.GREEN}✅ 浏览器已关闭{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ 浏览器关闭失败: {str(e)}{Style.RESET_ALL}")
                logger.error(f"Browser quit failed: {e}")