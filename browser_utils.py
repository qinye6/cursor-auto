from DrissionPage import ChromiumPage, ChromiumOptions
import os
import sys
import time
from colorama import Fore, Style
from config import Config

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
        config = Config()
        
        # 获取配置的浏览器设置
        default_browser = config.get('browser.default')
        incognito_mode = config.get('browser.incognito', True)
        headless_mode = config.get('browser.headless', False)
        
        # 获取浏览器路径
        browser_path = None
        if default_browser in self.BROWSERS:
            for path in self.BROWSERS[default_browser]['paths']:
                if os.path.exists(path):
                    browser_path = path
                    break
        
        if not browser_path:
            browser_path = self.select_browser()
        
        if not browser_path:
            sys.exit(1)
            
        try:
            print(f"\n{Fore.CYAN}🚀 正在启动浏览器...{Style.RESET_ALL}")
            
            options = ChromiumOptions()
            options.set_browser_path(browser_path)
            
            # 应用配置的浏览器选项
            if incognito_mode:
                options.set_argument('--incognito')
            
            if headless_mode:
                options.set_argument('--headless')
            
            # 添加网络相关配置
            options.set_argument('--disable-gpu')  # 禁用GPU加速
            options.set_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
            options.set_argument('--disable-web-security')  # 禁用网络安全限制
            options.set_argument('--disable-features=NetworkService')  # 禁用网络服务
            options.set_argument('--disable-site-isolation-trials')  # 禁用站点隔离
            
            # 其他优化选项
            options.set_argument('--disable-blink-features=AutomationControlled')
            options.set_argument('--disable-infobars')
            options.set_argument('--disable-notifications')
            options.set_argument('--disable-popup-blocking')
            options.set_argument('--disable-extensions')
            options.set_argument('--ignore-certificate-errors')
            options.set_argument('--ignore-ssl-errors')
            
            self.browser = ChromiumPage(options)
            time.sleep(2)
            print(f"{Fore.GREEN}✅ 浏览器启动成功{Style.RESET_ALL}")
            return self.browser
            
        except Exception as e:
            print(f"{Fore.RED}❌ 浏览器启动失败: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
                print(f"\n{Fore.GREEN}✅ 浏览器已关闭{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ 关闭浏览器失败: {str(e)}{Style.RESET_ALL}")
