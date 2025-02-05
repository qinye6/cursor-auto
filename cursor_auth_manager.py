import sqlite3
import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from anti_detection import AntiDetection
from human_simulator import HumanSimulator
from proxy_manager import ProxyManager
import random


class CursorAuthManager:
    """Cursor认证信息管理器"""

    def __init__(self):
        # 判断操作系统
        if os.name == "nt":  # Windows
            self.db_path = os.path.join(
                os.getenv("APPDATA"), "Cursor", "User", "globalStorage", "state.vscdb"
            )
        else:  # macOS
            self.db_path = os.path.expanduser(
                "~/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
            )
        # 添加多账号支持
        self.accounts = {}
        # 添加会话管理
        self.sessions = {}
        self.browser = None  # 需要在使用前设置
        self.human_simulator = None

    def set_browser(self, browser):
        """设置浏览器实例"""
        self.browser = browser
        self.human_simulator = HumanSimulator(browser)

    def update_auth(self, email=None, access_token=None, refresh_token=None):
        """
        更新Cursor的认证信息
        :param email: 新的邮箱地址
        :param access_token: 新的访问令牌
        :param refresh_token: 新的刷新令牌
        :return: bool 是否成功更新
        """
        updates = []
        # 登录状态
        updates.append(("cursorAuth/cachedSignUpType", "Auth_0"))

        if email is not None:
            updates.append(("cursorAuth/cachedEmail", email))
        if access_token is not None:
            updates.append(("cursorAuth/accessToken", access_token))
        if refresh_token is not None:
            updates.append(("cursorAuth/refreshToken", refresh_token))

        if not updates:
            print("没有提供任何要更新的值")
            return False

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for key, value in updates:

                # 如果没有更新任何行,说明key不存在,执行插入
                # 检查 accessToken 是否存在
                check_query = f"SELECT COUNT(*) FROM itemTable WHERE key = ?"
                cursor.execute(check_query, (key,))
                if cursor.fetchone()[0] == 0:
                    insert_query = "INSERT INTO itemTable (key, value) VALUES (?, ?)"
                    cursor.execute(insert_query, (key, value))
                else:
                    update_query = "UPDATE itemTable SET value = ? WHERE key = ?"
                    cursor.execute(update_query, (value, key))

                if cursor.rowcount > 0:
                    print(f"成功更新 {key.split('/')[-1]}")
                else:
                    print(f"未找到 {key.split('/')[-1]} 或值未变化")

            conn.commit()
            return True

        except sqlite3.Error as e:
            print("数据库错误:", str(e))
            return False
        except Exception as e:
            print("发生错误:", str(e))
            return False
        finally:
            if conn:
                conn.close()

    def add_account(self, email, password):
        """添加账号"""
        self.accounts[email] = {
            'password': password,
            'last_used': None,
            'status': 'active'
        }
        
    def rotate_account(self):
        """智能账号轮换"""
        # 实现账号轮换逻辑

    async def register_account(self, email, password):
        """注册新账号"""
        try:
            # 初始化模拟器和代理
            anti_detection = AntiDetection()
            human_simulator = HumanSimulator(self.browser)
            
            # 设置浏览器指纹和行为
            await self.setup_browser_environment(anti_detection)
            
            # 访问注册页面前先访问主页
            await self.browser.goto('https://cursor.sh/')
            await human_simulator.add_random_delays()
            
            # 访问注册页面
            await self.browser.goto('https://cursor.sh/register')
            await human_simulator.add_random_delays()
            
            # 注入绕过检测的脚本
            await self.inject_bypass_scripts()
            
            # 执行注册操作
            success = await self.perform_registration(email, password, human_simulator)
            
            if not success:
                print("首次注册尝试失败，准备重试...")
                await asyncio.sleep(random.uniform(2, 4))
                return await self.retry_registration(email, password)
                
            return success
            
        except Exception as e:
            print(f"注册过程出错: {str(e)}")
            return False

    async def setup_browser_environment(self, anti_detection):
        """设置浏览器环境"""
        fingerprint = anti_detection.randomize_fingerprint()
        
        # 注入更多的浏览器特征
        await self.browser.evaluate('''() => {
            // 修改 navigator 属性
            Object.defineProperties(navigator, {
                webdriver: {get: () => false},
                hardwareConcurrency: {get: () => 8},
                deviceMemory: {get: () => 8},
                platform: {get: () => "Win32"},
                languages: {get: () => ["en-US", "en"]},
                plugins: {get: () => [
                    {name: "Chrome PDF Plugin"},
                    {name: "Chrome PDF Viewer"},
                    {name: "Native Client"}
                ]}
            });
            
            // 添加 Chrome 运行时
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // 模拟 WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return "Intel Inc."
                }
                if (parameter === 37446) {
                    return "Intel Iris OpenGL Engine"
                }
                return getParameter.apply(this, [parameter]);
            };
        }''')
        
        # 设置更多的请求头
        await self.browser.set_extra_http_headers({
            'User-Agent': fingerprint['userAgent'],
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1'
        })

    async def inject_bypass_scripts(self):
        """注入绕过检测的脚本"""
        # 注入绕过检测的JS代码
        await self.browser.evaluate('''() => {
            // 修改 navigator 属性
            const originalNavigator = window.navigator;
            const navigatorProxy = new Proxy(originalNavigator, {
                get: function(target, key) {
                    switch (key) {
                        case 'webdriver':
                            return false;
                        case 'plugins':
                            return [
                                {
                                    name: "Chrome PDF Plugin",
                                    filename: "internal-pdf-viewer",
                                    description: "Portable Document Format"
                                },
                                {
                                    name: "Chrome PDF Viewer",
                                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                    description: "Portable Document Format"
                                }
                            ];
                        case 'languages':
                            return ['en-US', 'en'];
                        case 'permissions':
                            return {
                                query: async () => ({ state: 'granted' })
                            };
                        default:
                            return target[key];
                    }
                }
            });
            
            // 替换 navigator
            Object.defineProperty(window, 'navigator', {
                value: navigatorProxy,
                writable: false,
                configurable: false
            });
            
            // 添加 Chrome 运行时
            if (!window.chrome) {
                window.chrome = {
                    runtime: {
                        connect: () => {},
                        sendMessage: () => {}
                    },
                    app: {
                        isInstalled: false
                    },
                    webstore: {
                        onInstallStageChanged: {},
                        onDownloadProgress: {}
                    }
                };
            }
            
            // 修改 WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // 模拟常见的 WebGL 参数
                const fakeParams = {
                    37445: 'Intel Inc.',
                    37446: 'Intel Iris OpenGL Engine',
                    7937: 'WebKit',
                    35724: 'WebGL 1.0'
                };
                return fakeParams[parameter] || getParameter.apply(this, [parameter]);
            };
            
            // 添加 Notification API
            if (!window.Notification) {
                window.Notification = {
                    permission: 'granted',
                    requestPermission: async () => 'granted'
                };
            }
        }''')

    async def perform_registration(self, email, password, human_simulator):
        """执行注册操作"""
        try:
            # 等待页面加载完成
            await self.browser.wait_for_load_state('networkidle')
            
            # 找到输入框
            email_input = await self.browser.wait_for_selector('input[type="email"]')
            password_input = await self.browser.wait_for_selector('input[type="password"]')
            
            # 模拟输入前的行为
            await human_simulator.move_mouse_naturally(email_input)
            await email_input.click()
            await human_simulator.add_random_delays()
            
            # 输入邮箱
            await human_simulator.natural_typing(email_input, email)
            await human_simulator.add_random_delays()
            
            # 移动到密码框
            await human_simulator.move_mouse_naturally(password_input)
            await password_input.click()
            await human_simulator.add_random_delays()
            
            # 输入密码
            await human_simulator.natural_typing(password_input, password)
            await human_simulator.add_random_delays()
            
            # 处理 Turnstile 验证
            await self.handle_turnstile_verification()
            
            # 提交注册
            submit_button = await self.browser.wait_for_selector('button[type="submit"]')
            await human_simulator.move_mouse_naturally(submit_button)
            await human_simulator.add_random_delays()
            await submit_button.click()
            
            # 等待结果
            await self.browser.wait_for_load_state('networkidle')
            
            # 检查是否需要处理额外验证
            await self.handle_additional_verification()
            
            return await self.verify_registration()
            
        except Exception as e:
            print(f"注册操作失败: {str(e)}")
            return False

    async def handle_turnstile_verification(self):
        """处理 Turnstile 验证"""
        try:
            # 等待 Turnstile iframe 加载
            turnstile_frame = await self.browser.wait_for_selector(
                'iframe[src*="challenges.cloudflare.com"]',
                timeout=10000
            )
            
            if turnstile_frame:
                # 切换到 Turnstile iframe
                frame = await turnstile_frame.content_frame()
                
                # 等待验证按钮出现
                checkbox = await frame.wait_for_selector('[class*="turnstile-checkbox"]')
                if checkbox:
                    # 模拟点击验证按钮
                    await checkbox.click()
                    
                    # 等待验证完成
                    await asyncio.sleep(random.uniform(1, 2))
                
        except Exception as e:
            print(f"Turnstile 验证处理失败: {str(e)}")

    async def handle_additional_verification(self):
        """处理额外的验证"""
        try:
            # 等待可能出现的额外验证元素
            verification_selectors = [
                '.verification-container',
                '[class*="captcha"]',
                '[class*="verify"]',
                '[class*="challenge"]'
            ]
            
            for selector in verification_selectors:
                try:
                    element = await self.browser.wait_for_selector(selector, timeout=5000)
                    if element and await element.is_visible():
                        await self.handle_verification_element(element)
                except:
                    continue
                
        except Exception as e:
            print(f"额外验证处理失败: {str(e)}")

    async def handle_verification_element(self, element):
        """处理验证元素"""
        try:
            # 获取元素类型
            element_html = await element.inner_html()
            
            if 'turnstile' in element_html.lower():
                await self.handle_turnstile_verification()
            elif 'captcha' in element_html.lower():
                print("需要手动处理验证码")
                # 等待用户手动处理
                await asyncio.sleep(30)
            else:
                # 默认处理方式
                await element.click()
                await asyncio.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"验证元素处理失败: {str(e)}")

    async def retry_registration(self, email, password):
        """重试注册"""
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            print(f"正在进行第 {current_retry + 1} 次重试...")
            await asyncio.sleep(random.uniform(3, 5))
            
            # 刷新页面
            await self.browser.reload()
            await asyncio.sleep(random.uniform(2, 3))
            
            # 重新尝试注册
            success = await self.perform_registration(email, password, self.human_simulator)
            if success:
                return True
                
            current_retry += 1
        
        return False

    async def verify_registration(self):
        """验证注册是否成功"""
        try:
            # 检查URL是否跳转到成功页面
            current_url = self.browser.url
            if 'dashboard' in current_url:
                return True
                
            # 检查是否有错误消息
            error_message = await self.browser.query_selector('.error-message')
            if error_message:
                error_text = await error_message.text_content()
                print(f"注册失败: {error_text}")
                return False
                
            return True
            
        except Exception as e:
            print(f"验证注册状态时出错: {str(e)}")
            return False
