import json
import os
from colorama import Fore, Style

DEFAULT_CONFIG = {
    "email": {
        "domain": "xxx.xxx", #@后缀
        "mail_domain": "xxx.xxx", #临时邮箱域名
        "prefix_enabled": True, #是否启用随机前缀
        "prefix_length": 8, #随机前缀长度
        "custom_prefix": "", #固定前缀
        "api": {
            "base_url": "https://xxx.xxx",  # 邮箱后端API地址
            "admin_password": "xxxxxx",                   # 管理员密码
            "web_url": "https://xxx.xxx"           # 邮箱Web界面地址
        }
    },
    "browser": {
        "default": "chrome",  # chrome, edge, brave
        "incognito": True,    # 无痕模式
        "headless": True,    # 无头模式
    },
    "account": {
        "first_name": "qin", #名字
        "last_name": "ye", #姓氏
        "password_length": 12, #随机密码长度
    },
    "cursor": {
        "path": "",  # Cursor 可执行文件路径
        "auto_start": True,  # 是否在重置后自动启动
    }
}

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.create_default_config()
        except Exception as e:
            print(f"{Fore.RED}❌ 加载配置文件失败: {str(e)}{Style.RESET_ALL}")
            return self.create_default_config()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"{Fore.GREEN}✅ 配置已保存{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ 保存配置失败: {str(e)}{Style.RESET_ALL}")
    
    def create_default_config(self):
        """创建默认配置"""
        self.config = DEFAULT_CONFIG.copy()
        self.save_config()
        return self.config
    
    def setup_wizard(self):
        """配置向导"""
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[配置向导]{Style.RESET_ALL}")
        
        # 邮箱配置
        print(f"\n{Fore.CYAN}[邮箱设置]{Style.RESET_ALL}")
        
        # 邮箱域名配置
        self.config['email']['domain'] = input(
            f"请输入邮箱域名 (默认: {DEFAULT_CONFIG['email']['domain']}): "
        ).strip() or DEFAULT_CONFIG['email']['domain']
        
        # 临时邮箱服务域名配置
        self.config['email']['mail_domain'] = input(
            f"请输入临时邮箱服务域名 (默认: {DEFAULT_CONFIG['email']['mail_domain']}): "
        ).strip() or DEFAULT_CONFIG['email']['mail_domain']
        
        # 邮箱API配置
        print(f"\n{Fore.CYAN}[邮箱API设置]{Style.RESET_ALL}")
        self.config['email']['api']['base_url'] = input(
            f"请输入邮箱API地址 (默认: {DEFAULT_CONFIG['email']['api']['base_url']}): "
        ).strip() or DEFAULT_CONFIG['email']['api']['base_url']
        
        self.config['email']['api']['web_url'] = input(
            f"请输入邮箱Web地址 (默认: {DEFAULT_CONFIG['email']['api']['web_url']}): "
        ).strip() or DEFAULT_CONFIG['email']['api']['web_url']
        
        self.config['email']['api']['admin_password'] = input(
            f"请输入管理员密码 (默认: {DEFAULT_CONFIG['email']['api']['admin_password']}): "
        ).strip() or DEFAULT_CONFIG['email']['api']['admin_password']
        
        # 前缀设置
        prefix_enabled = input(
            "是否启用随机前缀? (y/n, 默认: y): "
        ).lower().strip() != 'n'
        self.config['email']['prefix_enabled'] = prefix_enabled
        
        if prefix_enabled:
            self.config['email']['prefix_length'] = int(input(
                f"请输入前缀长度 (默认: {DEFAULT_CONFIG['email']['prefix_length']}): "
            ) or DEFAULT_CONFIG['email']['prefix_length'])
        else:
            self.config['email']['custom_prefix'] = input(
                "请输入固定前缀: "
            ).strip()
        
        # 浏览器配置
        print(f"\n{Fore.CYAN}[浏览器设置]{Style.RESET_ALL}")
        print("可选浏览器: chrome, edge, brave")
        self.config['browser']['default'] = input(
            f"请选择默认浏览器 (默认: {DEFAULT_CONFIG['browser']['default']}): "
        ).strip() or DEFAULT_CONFIG['browser']['default']
        
        self.config['browser']['incognito'] = input(
            "是否启用无痕模式? (y/n, 默认: y): "
        ).lower().strip() != 'n'
        
        self.config['browser']['headless'] = input(
            "是否启用无头模式? (y/n, 默认: n): "
        ).lower().strip() == 'y'
        
        # 账号配置
        print(f"\n{Fore.CYAN}[账号设置]{Style.RESET_ALL}")
        self.config['account']['first_name'] = input(
            f"请输入名字 (默认: {DEFAULT_CONFIG['account']['first_name']}): "
        ).strip() or DEFAULT_CONFIG['account']['first_name']
        
        self.config['account']['last_name'] = input(
            f"请输入姓氏 (默认: {DEFAULT_CONFIG['account']['last_name']}): "
        ).strip() or DEFAULT_CONFIG['account']['last_name']
        
        self.config['account']['password_length'] = int(input(
            f"请输入密码长度 (默认: {DEFAULT_CONFIG['account']['password_length']}): "
        ) or DEFAULT_CONFIG['account']['password_length'])
        
        # Cursor配置
        print(f"\n{Fore.CYAN}[Cursor设置]{Style.RESET_ALL}")
        
        if os.name == "nt":  # Windows
            default_path = os.path.join(os.getenv("LOCALAPPDATA"), "Programs", "Cursor", "Cursor.exe")
        else:  # macOS
            default_path = "/Applications/Cursor.app"
        
        self.config['cursor']['path'] = input(
            f"请输入Cursor程序路径 (默认: {default_path}): "
        ).strip() or default_path
        
        self.config['cursor']['auto_start'] = input(
            "是否在重置后自动启动Cursor? (y/n, 默认: y): "
        ).lower().strip() != 'n'
        
        self.save_config()
        print(f"\n{Fore.GREEN}✅ 配置完成！{Style.RESET_ALL}")
    
    def get(self, key, default=None):
        """获取配置项"""
        value = self.config
        for k in key.split('.'):
            try:
                value = value[k]
            except (KeyError, TypeError):
                return default
        return value
    
    def set(self, key, value):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value
        self.save_config() 