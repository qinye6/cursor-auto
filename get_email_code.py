from DrissionPage.common import Keys
import time
import re
from email_api import EmailAPI


class EmailVerificationHandler:
    def __init__(self):
        self.email_api = EmailAPI()

    def get_verification_code(self, email):
        """获取验证码"""
        try:
            username = email.split("@")[0]
            
            if not self.email_api.create_email(username):
                print(f"\n⚠️ 创建邮箱失败，尝试直接获取邮件...")
            
            max_attempts = 5
            for attempt in range(max_attempts):
                print(f"\n📧 正在检查邮件 ({attempt + 1}/{max_attempts})...")
                mail = self.email_api.get_latest_mail()
                
                if mail and mail.get("raw_data"):
                    # 从原始邮件数据中提取验证码
                    raw_content = mail["raw_data"].get("raw", "")
                    
                    # 首先尝试匹配纯文本部分的验证码
                    patterns = [
                        r"verification code is (\d{6})",
                        r"code below.*?(\d{6})",
                        r"[\n\r](\d{6})[\n\r]",  # 匹配独立行的6位数字
                        r"(\d{6})"  # 最后尝试匹配任何6位数字
                    ]
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, raw_content, re.IGNORECASE | re.DOTALL)
                        for match in matches:
                            code = match.group(1)
                            if len(code) == 6 and code.isdigit():
                                print(f"\n✅ 成功获取验证码: {code}")
                                return code
                
                time.sleep(2)
                
            print("\n❌ 未能在邮件中找到验证码")
            return None
            
        except Exception as e:
            print(f"\n❌ 获取验证码失败: {str(e)}")
            return None
