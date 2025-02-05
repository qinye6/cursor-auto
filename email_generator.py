import random
import time
from config import Config

class EmailGenerator:
    def __init__(self):
        self.config = Config()
        
    def generate_email(self):
        """根据配置生成邮箱地址"""
        domain = self.config.get('email.domain')        # 用于实际邮箱地址
        mail_domain = self.config.get('email.mail_domain')  # 用于显示服务商
        prefix_enabled = self.config.get('email.prefix_enabled')
        
        if prefix_enabled:
            # 检查是否有自定义前缀
            custom_prefix = self.config.get('email.custom_prefix')
            if custom_prefix:
                # 如果有自定义前缀，使用自定义前缀加时间戳
                timestamp = str(int(time.time()))[-6:]
                prefix = f"{custom_prefix}{timestamp}"
            else:
                # 如果没有自定义前缀，使用随机前缀
                length = self.config.get('email.prefix_length', 8)
                random_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
                timestamp = str(int(time.time()))[-6:]
                prefix = f"{random_str}{timestamp}"
        else:
            # 如果禁用前缀，直接使用自定义前缀
            prefix = self.config.get('email.custom_prefix', 'default')
        
        # 生成完整邮箱地址，使用 domain 作为域名
        return f"{prefix}@{domain}"

    def get_account_info(self):
        """获取完整的账号信息"""
        return {
            "email": self.generate_email(),
            "password": "".join(
                random.choices(
                    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*",
                    k=self.config.get('account.password_length', 12)
                )
            ),
            "first_name": self.config.get('account.first_name', 'qin'),
            "last_name": self.config.get('account.last_name', 'ye'),
        } 