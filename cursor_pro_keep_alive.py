from config import Config

import os
import sys
from colorama import init, Fore, Style, AnsiToWin32

from exit_cursor import ExitCursor, StartCursor

# 修改初始化方式
init(wrap=False)
sys.stdout = AnsiToWin32(sys.stdout).stream

# 定义emoji和颜色常量
EMOJI = {
    'START': '🚀',
    'FORM': '📝',
    'VERIFY': '🔄',
    'PASSWORD': '🔑',
    'CODE': '📱',
    'DONE': '✨',
    'ERROR': '❌',
    'WAIT': '⏳',
    'SUCCESS': '✅',
    'MAIL': '📧',
    'INFO': 'ℹ️',
    'WARNING': '⚠️',
    'LOADING': '🔄',
    'CLOCK': '🕐',
    'CHECK': '☑️',
    'GEAR': '⚙️',
    'LOCK': '🔒',
    'KEY': '🔑',
    'MAIL_NEW': '📨',
    'REFRESH': '🔁',
    'SPARKLES': '✨',
    'ROCKET': '🚀',
    'SHIELD': '🛡️',
    'TOOLS': '🛠️',
}

os.environ["PYTHONVERBOSE"] = "0"
os.environ["PYINSTALLER_VERBOSE"] = "0"

import time
import random
import asyncio
import traceback
from cursor_auth_manager import CursorAuthManager
import os
from logger import logging, logger, log_function_call
from browser_utils import BrowserManager
from get_email_code import EmailVerificationHandler
from logo import print_logo
from reset_machine import MachineIDResetter
import psutil
from auto_updater import AutoUpdater
from email_generator import EmailGenerator

# 在文件开头设置日志
class ColoredFormatter(logging.Formatter):
    """自定义彩色日志格式器"""
    
    def format(self, record):
        if record.levelno == logging.INFO:
            record.msg = f"{Fore.CYAN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}{EMOJI['ERROR']} {record.msg}{Style.RESET_ALL}"
        return super().format(record)

# 为控制台处理器设置彩色格式器
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setFormatter(ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s"))

# 在程序开始时记录启动信息
logger.info("Cursor Pro 程序已启动")

def show_progress(progress, total, prefix='Progress:', suffix='Complete', length=50):
    """显示进度条"""
    filled_length = int(length * progress / total)
    empty_length = length - filled_length
    
    # 使用方块字符
    bar = '█' * filled_length + '░' * empty_length
    
    # 计算百分比
    percent = f"{100.0 * progress / total:>3.1f}"
    
    # 格式化输出
    print(
        f'\r{Fore.WHITE}{prefix} {Fore.CYAN}|{bar}| {percent}% {suffix}',
        end='',
        flush=True
    )
    
    # 完成时换行
    if progress == total:
        print(Style.RESET_ALL)


def handle_turnstile(tab):
    print(f"{Fore.CYAN}{EMOJI['VERIFY']} 开始突破 Turnstile 验证{Style.RESET_ALL}")
    max_attempts = 3
    attempt = 0
    
    try:
        while attempt < max_attempts:
            try:
                # 检查错误消息
                error_msg = tab.ele('.text-red-500', timeout=1)
                if error_msg and "Can't verify the user is human" in error_msg.text:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} 检测到验证失败，重试中...{Style.RESET_ALL}")
                    # 刷新页面并等待
                    tab.refresh()
                    time.sleep(3)
                    continue
                
                # 等待 iframe 加载
                time.sleep(2)
                
                # 尝试找到并点击验证框
                challengeCheck = (
                    tab.ele("@id=cf-turnstile", timeout=5)
                    .child()
                    .shadow_root.ele("tag:iframe")
                    .ele("tag:body")
                    .sr("tag:input")
                )

                if challengeCheck:
                    print(f"{Fore.YELLOW}{EMOJI['WAIT']} 检测到验证请求，开始处理...{Style.RESET_ALL}")
                    
                    # 模拟人类行为
                    time.sleep(random.uniform(1, 2))
                    
                    # 模拟鼠标移动
                    tab.run_js("""
                        const event = new MouseEvent('mousemove', {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: Math.random() * window.innerWidth,
                            clientY: Math.random() * window.innerHeight
                        });
                        document.dispatchEvent(event);
                    """)
                    
                    time.sleep(random.uniform(0.5, 1))
                    
                    # 点击验证框
                    challengeCheck.click()
                    
                    # 等待验证结果
                    time.sleep(5)
                    
                    # 检查验证是否成功
                    error_msg = tab.ele('.text-red-500', timeout=1)
                    if not error_msg:
                        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 验证突破成功！{Style.RESET_ALL}")
                        time.sleep(2)  # 额外等待以确保验证完成
                        return True
                
                # 检查是否已通过验证
                if tab.ele("@name=password") or tab.ele("@data-index=0") or tab.ele("Account Settings"):
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 验证通过{Style.RESET_ALL}")
                    return True
                    
            except Exception as e:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} 验证处理异常: {str(e)}{Style.RESET_ALL}")
            
            attempt += 1
            if attempt < max_attempts:
                print(f"{Fore.YELLOW}{EMOJI['WAIT']} 第 {attempt}/{max_attempts} 次尝试{Style.RESET_ALL}")
                time.sleep(random.uniform(2, 3))
                
        print(f"{Fore.RED}{EMOJI['ERROR']} 验证失败，已达到最大重试次数{Style.RESET_ALL}")
        return False
        
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 验证过程出错: {str(e)}{Style.RESET_ALL}")
        return False


def get_cursor_session_token(tab, max_attempts=3, retry_interval=2):
    """
    获取Cursor会话token，带有重试机制
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{EMOJI['WAIT']} 开始获取 Cursor Session Token...{Style.RESET_ALL}")
    attempts = 0

    while attempts < max_attempts:
        try:
            cookies = tab.cookies()
            for cookie in cookies:
                if cookie.get("name") == "WorkosCursorSessionToken":
                    token = cookie["value"].split("%3A%3A")[1]
                    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Token 获取成功{Style.RESET_ALL}")
                    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}[Token 信息]{Style.RESET_ALL}")
                    print(f"{EMOJI['KEY']} Token: {Fore.GREEN}{token}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                    return token

            attempts += 1
            if attempts < max_attempts:
                print(
                    f"{Fore.YELLOW}{EMOJI['WAIT']} 第 {attempts} 次尝试未获取到 Token，{retry_interval}秒后重试...{Style.RESET_ALL}"
                )
                time.sleep(retry_interval)
            else:
                print(f"{Fore.RED}{EMOJI['ERROR']} 已达到最大尝试次数({max_attempts})，获取 Token 失败{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 获取 Token 失败: {str(e)}{Style.RESET_ALL}")
            attempts += 1
            if attempts < max_attempts:
                print(f"{Fore.YELLOW}{EMOJI['WAIT']} 将在 {retry_interval} 秒后重试...{Style.RESET_ALL}")
                time.sleep(retry_interval)

    return None


def update_cursor_auth(email=None, access_token=None, refresh_token=None):
    """
    更新Cursor的认证信息
    """
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{EMOJI['WAIT']} 正在更新 Cursor 认证信息...{Style.RESET_ALL}")
    
    auth_manager = CursorAuthManager()
    result = auth_manager.update_auth(email, access_token, refresh_token)
    
    if result:
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[认证信息]{Style.RESET_ALL}")
        print(f"{EMOJI['MAIL']} 邮箱: {Fore.GREEN}{email}{Style.RESET_ALL}")
        print(f"{EMOJI['KEY']} Access Token: {Fore.GREEN}{access_token}{Style.RESET_ALL}")
        print(f"{EMOJI['KEY']} Refresh Token: {Fore.GREEN}{refresh_token}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 认证信息更新完成{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{EMOJI['ERROR']} 认证信息更新失败{Style.RESET_ALL}")
    
    return result


def simulate_human_typing(tab, selector, text, min_delay=0.1, max_delay=0.3):
    """模拟人类输入文字"""
    try:
        element = tab.ele(selector)
        element.click()  # 先点击激活输入框
        time.sleep(random.uniform(0.3, 0.8))  # 点击后短暂停顿
        
        for char in text:
            element.input(char)  # 逐字输入
            # 为每个字符添加随机延迟
            time.sleep(random.uniform(min_delay, max_delay))
            
        # 输入完成后的短暂停顿
        time.sleep(random.uniform(0.5, 1.0))
        return True
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 输入失败: {str(e)}{Style.RESET_ALL}")
        return False


def sign_up_account(browser, tab):
    # 添加 URL 常量
    sign_up_url = "https://authenticator.cursor.sh/sign-up"
    settings_url = "https://www.cursor.com/settings"
    
    # 获取配置的邮箱域名
    config = Config()
    domain = config.get('email.domain')          # 实际邮箱域名
    mail_domain = config.get('email.mail_domain')  # 邮箱服务商域名
    
    # 初始化邮箱验证处理器
    email_handler = EmailVerificationHandler()
    
    # 生成账号信息
    email_generator = EmailGenerator()
    account_info = email_generator.get_account_info()
    
    # 从 account_info 中获取账号信息
    account = account_info['email']
    password = account_info['password']
    first_name = account_info['first_name']
    last_name = account_info['last_name']
    
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['START']} 开始 Cursor Pro 注册流程{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[信息]{Style.RESET_ALL}")
    print(f"{EMOJI['FORM']} 邮箱服务商: {Fore.GREEN}{mail_domain}{Style.RESET_ALL}")
    print(f"{EMOJI['FORM']} 临时邮箱地址: {Fore.GREEN}{account}{Style.RESET_ALL}")
    print(f"{EMOJI['FORM']} 注册名称: {Fore.GREEN}{first_name} {last_name}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
    
    total_steps = 5
    show_progress(0, total_steps)
    tab.get(sign_up_url)

    try:
        if tab.ele("@name=first_name"):
            print(f"\n{Fore.YELLOW}{EMOJI['FORM']} [1/5] 填写注册信息...{Style.RESET_ALL}")
            
            # 模拟人类输入名字
            print(f"{Fore.CYAN}{EMOJI['WAIT']} 输入名字...{Style.RESET_ALL}")
            simulate_human_typing(tab, "@name=first_name", first_name)
            time.sleep(random.uniform(0.8, 1.5))  # 字段之间的停顿
            
            # 模拟人类输入姓氏
            print(f"{Fore.CYAN}{EMOJI['WAIT']} 输入姓氏...{Style.RESET_ALL}")
            simulate_human_typing(tab, "@name=last_name", last_name)
            time.sleep(random.uniform(0.8, 1.5))
            
            # 模拟人类输入邮箱
            print(f"{Fore.CYAN}{EMOJI['WAIT']} 输入邮箱...{Style.RESET_ALL}")
            simulate_human_typing(tab, "@name=email", account)
            time.sleep(random.uniform(1.0, 2.0))
            
            # 提交表单
            print(f"{Fore.CYAN}{EMOJI['WAIT']} 提交表单...{Style.RESET_ALL}")
            tab.ele("@type=submit").click()
            show_progress(1, total_steps)

    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} 填写注册信息失败: {str(e)}{Style.RESET_ALL}")
        return False

    print(f"\n{Fore.YELLOW}{EMOJI['VERIFY']} [2/5] 处理验证...{Style.RESET_ALL}")
    handle_turnstile(tab)
    show_progress(2, total_steps)

    try:
        if tab.ele("@name=password"):
            print(f"\n{Fore.YELLOW}{EMOJI['PASSWORD']} [3/5] 设置密码...{Style.RESET_ALL}")
            # 模拟人类输入密码
            simulate_human_typing(tab, "@name=password", password, min_delay=0.15, max_delay=0.35)
            time.sleep(random.uniform(1.0, 2.0))

            tab.ele("@type=submit").click()
            print(f"{Fore.CYAN}{EMOJI['WAIT']} 请稍等...{Style.RESET_ALL}")
            show_progress(3, total_steps)

    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} 设置密码失败: {str(e)}{Style.RESET_ALL}")
        return False

    time.sleep(random.uniform(1, 3))
    if tab.ele("This email is not available."):
        print(f"\n{Fore.RED}{EMOJI['ERROR']} 执行失败{Style.RESET_ALL}")
        return False

    print(f"\n{Fore.YELLOW}{EMOJI['CODE']} [4/5] 处理验证码...{Style.RESET_ALL}")
    handle_turnstile(tab)
    show_progress(4, total_steps)

    while True:
        try:
            if tab.ele("Account Settings"):
                break
            if tab.ele("@data-index=0"):
                code = email_handler.get_verification_code(account)
                if not code:
                    return False

                print(f"{Fore.CYAN}{EMOJI['WAIT']} 输入验证码...{Style.RESET_ALL}")
                # 模拟人类输入验证码
                for i, digit in enumerate(code):
                    # 为每个数字框添加输入延迟
                    time.sleep(random.uniform(0.3, 0.6))
                    simulate_human_typing(tab, f"@data-index={i}", digit, min_delay=0.1, max_delay=0.25)
                break
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 输入验证码失败: {str(e)}{Style.RESET_ALL}")

    print(f"\n{Fore.YELLOW}{EMOJI['DONE']} [5/5] 完成注册...{Style.RESET_ALL}")
    handle_turnstile(tab)
    wait_time = random.randint(3, 6)
    for i in range(wait_time):
        print(f"{Fore.CYAN}{EMOJI['WAIT']} 等待中... {wait_time-i}秒{Style.RESET_ALL}")
        time.sleep(1)
    
    # 获取可用额度
    total_usage = "未知"
    tab.get(settings_url)
    try:
        usage_selector = (
            "css:div.col-span-2 > div > div > div > div > "
            "div:nth-child(1) > div.flex.items-center.justify-between.gap-2 > "
            "span.font-mono.text-sm\\/\\[0\\.875rem\\]"
        )
        usage_ele = tab.ele(usage_selector)
        if usage_ele:
            usage_info = usage_ele.text
            total_usage = usage_info.split("/")[-1].strip()
    except Exception as e:
        print(f"\n{Fore.RED}{EMOJI['ERROR']} 获取可用额度失败: {str(e)}{Style.RESET_ALL}")

    # 显示最终信息
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Cursor Pro 注册成功！{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}[账号信息]{Style.RESET_ALL}")
    print(f"{EMOJI['SUCCESS']} 邮箱: {Fore.GREEN}{account}{Style.RESET_ALL}")
    print(f"{EMOJI['SUCCESS']} 密码: {Fore.GREEN}{password}{Style.RESET_ALL}")
    print(f"{EMOJI['SUCCESS']} 可用额度: {Fore.GREEN}{total_usage}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    # 记录到日志
    account_info = (
        f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}Cursor Pro 账号信息{Style.RESET_ALL}\n"
        f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n"
        f"{EMOJI['FORM']} 邮箱服务商: {Fore.GREEN}{mail_domain}{Style.RESET_ALL}\n"
        f"{EMOJI['MAIL']} 邮箱: {Fore.GREEN}{account}{Style.RESET_ALL}\n"
        f"{EMOJI['PASSWORD']} 密码: {Fore.GREEN}{password}{Style.RESET_ALL}\n"
        f"{EMOJI['SUCCESS']} 可用额度: {Fore.GREEN}{total_usage}{Style.RESET_ALL}\n"
        f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}"
    )
    logging.info(account_info)
    time.sleep(5)
    return True


def print_header(title, width=50):
    """打印带有样式的标题"""
    print(f"\n{Fore.CYAN}{'═' * width}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{title.center(width)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * width}{Style.RESET_ALL}")

def print_section(title):
    """打印带有样式的分节标题"""
    print(f"\n{Fore.YELLOW}[{title}]{Style.RESET_ALL}")

def format_info(label, value, emoji=''):
    """格式化信息显示"""
    return f"{emoji} {label}: {Fore.GREEN}{value}{Style.RESET_ALL}"

def print_status(message, status='info'):
    """打印状态信息"""
    colors = {
        'info': Fore.CYAN,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'error': Fore.RED
    }
    emojis = {
        'info': EMOJI['INFO'],
        'success': EMOJI['SUCCESS'],
        'warning': EMOJI['WARNING'],
        'error': EMOJI['ERROR']
    }
    color = colors.get(status, Fore.WHITE)
    emoji = emojis.get(status, '')
    print(f"{color}{emoji} {message}{Style.RESET_ALL}")


async def main():
    browser_manager = None
    try:
        print_logo()
        
        # 检查更新
        print(f"{Fore.CYAN}{EMOJI['INFO']} 检查更新...{Style.RESET_ALL}")
        try:
            updater = AutoUpdater()
            updater.check_and_update()
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 当前已是最新版本{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} 更新检查失败: {str(e)}{Style.RESET_ALL}")
            logger.error(f"更新检查失败: {str(e)}")
            logger.error(traceback.format_exc())
        
        # 添加延迟和提示
        print(f"\n{Fore.CYAN}{EMOJI['INFO']} 正在初始化...{Style.RESET_ALL}")
        await asyncio.sleep(2)
        
        # 初始化配置
        try:
            config = Config()
            logger.info("配置加载成功")
        except Exception as e:
            logger.error(f"配置加载失败: {str(e)}")
            raise
            
        # 检查并关闭已运行的 Cursor
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} 检查并关闭已运行的 Cursor...{Style.RESET_ALL}")
            ExitCursor()
            await asyncio.sleep(2)
            logger.info("Cursor 进程检查完成")
        except Exception as e:
            logger.error(f"Cursor 进程检查失败: {str(e)}")
            # 继续执行，不抛出异常
            
        # 初始化浏览器
        print(f"{Fore.CYAN}{EMOJI['INFO']} 初始化浏览器...{Style.RESET_ALL}")
        browser_manager = BrowserManager()
        browser = browser_manager.init_browser()
        
        if not browser:
            print(f"{Fore.RED}{EMOJI['ERROR']} 浏览器初始化失败{Style.RESET_ALL}")
            return

        # 使用 browser 进行操作
        tab = browser  # DrissionPage 不需要获取 latest_tab
        
        # 初始化邮箱验证处理器
        email_handler = EmailVerificationHandler()

        # 固定的 URL 配置
        login_url = "https://authenticator.cursor.sh"
        sign_up_url = "https://authenticator.cursor.sh/sign-up"
        settings_url = "https://www.cursor.com/settings"
        mail_url = config.get('email.api.web_url')  # 使用配置的Web地址

        # 生成账号信息
        email_generator = EmailGenerator()
        account_info = email_generator.get_account_info()
        
        account = account_info['email']
        password = account_info['password']
        first_name = account_info['first_name']
        last_name = account_info['last_name']
        
        auto_update_cursor_auth = True

        tab.run_js("try { turnstile.reset() } catch(e) { }")

        tab.get(login_url)

        # 在重要操作前后添加日志
        logger.debug("开始执行主要操作...")
        try:
            if sign_up_account(browser, tab):
                token = get_cursor_session_token(tab)
                if token:
                    update_cursor_auth(
                        email=account, access_token=token, refresh_token=token
                    )           
                    # 在认证更新成功后重置机器ID
                    print(f"\n{Fore.CYAN}{EMOJI['WAIT']} 开始重置机器标识...{Style.RESET_ALL}")
                    resetter = MachineIDResetter()
                    if resetter.reset_machine_ids():
                        logger.info("机器标识重置成功")
                        
                        # 检查是否需要自动启动 Cursor
                        cursor_path = config.get('cursor.path')
                        if cursor_path and os.path.exists(cursor_path):
                            logger.info(f"正在启动 Cursor: {cursor_path}")
                            StartCursor(cursor_path)
                        else:
                            logger.warning("Cursor 路径未配置或不存在，但将尝试使用默认路径启动")
                            # 尝试使用默认路径
                            if os.name == "nt":  # Windows
                                default_path = os.path.join(os.getenv("LOCALAPPDATA"), "Programs", "Cursor", "Cursor.exe")
                            else:  # macOS
                                default_path = "/Applications/Cursor.app"
                            
                            if os.path.exists(default_path):
                                logger.info(f"使用默认路径启动 Cursor: {default_path}")
                                StartCursor(default_path)
                            else:
                                logger.error("无法找到 Cursor 可执行文件")
                else:
                    logger.error("账户注册失败")

            logger.info("所有操作已完成")
        except Exception as e:
            logger.error(f"操作执行失败: {str(e)}", exc_info=True)

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 程序执行出错: {str(e)}{Style.RESET_ALL}")
        logger.error(f"程序执行出错: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        if browser_manager:
            browser_manager.quit()
        
        print(f"\n{Fore.CYAN}{EMOJI['INFO']} 程序执行完成{Style.RESET_ALL}")
        input(f"{Fore.CYAN}{EMOJI['WAIT']} 按回车键退出...{Style.RESET_ALL}")


if __name__ == "__main__":
    # 使用 asyncio 运行主函数
    try:
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} 程序启动失败: {str(e)}{Style.RESET_ALL}")
        logger.error(f"程序启动失败: {str(e)}")
        logger.error(traceback.format_exc())
        input("\n按回车键退出...")
