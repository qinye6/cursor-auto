import requests
import time
import json
from config import Config

class EmailAPI:
    def __init__(self, base_url=None, admin_password=None):
        config = Config()
        self.base_url = base_url or config.get('email.api.base_url')
        self.admin_password = admin_password or config.get('email.api.admin_password')
        self.jwt = None
        
    def create_email(self, name, domain="qinye.asia"):
        """创建新的邮箱地址"""
        try:
            # 首先通过管理员API创建邮箱
            if self.admin_password:
                admin_res = requests.post(
                    f"{self.base_url}/admin/new_address",
                    json={
                        "enablePrefix": False,
                        "name": name,
                        "domain": domain
                    },
                    headers={
                        'x-admin-auth': self.admin_password,
                        "Content-Type": "application/json"
                    }
                )
                
                print(f"\n📧 API响应: {admin_res.text}")
                
                if admin_res.status_code != 200:
                    print(f"管理员API创建邮箱失败: {admin_res.text}")
                    return None
                    
                # 从管理员API响应中获取JWT
                response_data = admin_res.json()
                self.jwt = response_data.get("jwt")
                if not self.jwt:
                    print("未能从管理员API响应中获取JWT")
                    return None
                    
                print(f"\n✅ 成功创建邮箱并获取JWT: {self.jwt[:20]}...")
                return f"{name}@{domain}"
            
        except Exception as e:
            print(f"创建邮箱失败: {str(e)}")
            return None
            
    def get_latest_mail(self, limit=1):
        """获取最新邮件"""
        if not self.jwt:
            print("\n⚠️ 无法获取邮件：JWT token 不存在")
            return None
            
        try:
            res = requests.get(
                f"{self.base_url}/api/mails",
                params={"limit": limit, "offset": 0},
                headers={
                    "Authorization": f"Bearer {self.jwt}",
                    "Content-Type": "application/json"
                }
            )
            
            print(f"\n📧 获取邮件响应: {res.status_code}")
            
            if res.status_code == 200:
                response_data = res.json()
                mails = response_data.get("results", [])
                if mails and len(mails) > 0:
                    print("\n✅ 成功获取到邮件")
                    mail_data = mails[0]
                    
                    # 构建返回数据
                    return {
                        "text": mail_data.get("raw", ""),  # 使用raw字段作为文本内容
                        "raw_data": mail_data  # 保存原始数据以备需要
                    }
                print("\n⚠️ 邮箱中暂无邮件")
            else:
                print(f"\n❌ 获取邮件失败: HTTP {res.status_code}")
                print(f"错误信息: {res.text}")
            return None
            
        except Exception as e:
            print(f"\n❌ 获取邮件失败: {str(e)}")
            return None 