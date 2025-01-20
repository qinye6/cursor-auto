import os
import sys
import requests
import platform
import subprocess
from packaging import version
from logger import logger
from colorama import Fore, Style

class AutoUpdater:
    def __init__(self):
        self.current_version = "1.0.1"  # 当前版本号
        self.github_api = "https://api.github.com/repos/qinye6/cursor-auto/releases/latest"
        self.update_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "updates")
        self.system = platform.system().lower()
        
    def get_latest_version(self):
        """获取最新版本信息"""
        try:
            response = requests.get(
                self.github_api,
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10
            )
            response.raise_for_status()
            
            release_info = response.json()
            latest_version = release_info["tag_name"].lstrip("v")
            download_url = None
            
            # 根据系统选择对应的下载文件
            for asset in release_info["assets"]:
                if self.system in asset["name"].lower():
                    download_url = asset["browser_download_url"]
                    break
            
            return {
                "version": latest_version,
                "download_url": download_url
            }
            
        except Exception as e:
            logger.error(f"获取最新版本信息失败: {str(e)}")
            return None
            
    def needs_update(self, latest_version):
        """检查是否需要更新"""
        try:
            return version.parse(latest_version) > version.parse(self.current_version)
        except Exception as e:
            logger.error(f"版本比较失败: {str(e)}")
            return False
            
    def download_update(self, download_url):
        """下载更新文件"""
        try:
            # 创建更新目录
            os.makedirs(self.update_dir, exist_ok=True)
            
            # 下载文件
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            file_name = os.path.basename(download_url)
            file_path = os.path.join(self.update_dir, file_name)
            
            # 显示下载进度
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded = 0
            
            print(f"\n{Fore.CYAN}正在下载更新...{Style.RESET_ALL}")
            
            with open(file_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    
                    # 更新进度条
                    if total_size > 0:
                        percentage = int((downloaded / total_size) * 100)
                        bar_length = 50
                        filled = int(bar_length * downloaded / total_size)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f'\r进度: |{bar}| {percentage}%', end='')
            
            print("\n")
            return file_path
            
        except Exception as e:
            logger.error(f"下载更新失败: {str(e)}")
            return None
            
    def install_update(self, file_path):
        """安装更新"""
        try:
            if self.system == "windows":
                # Windows下使用start命令启动新进程
                subprocess.Popen(
                    f'start "" "{file_path}"',
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Unix系统使用chmod添加执行权限
                os.chmod(file_path, 0o755)
                subprocess.Popen([file_path])
                
            # 退出当前进程
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"安装更新失败: {str(e)}")
            return False
            
    def check_and_update(self):
        """检查并执行更新"""
        try:
            print(f"\n{Fore.CYAN}检查更新...{Style.RESET_ALL}")
            
            # 获取最新版本信息
            latest_info = self.get_latest_version()
            if not latest_info:
                print(f"{Fore.YELLOW}无法获取更新信息{Style.RESET_ALL}")
                return False
                
            # 检查是否需要更新
            if not self.needs_update(latest_info["version"]):
                print(f"{Fore.GREEN}当前已是最新版本{Style.RESET_ALL}")
                return False
                
            print(f"\n{Fore.YELLOW}发现新版本: {latest_info['version']}{Style.RESET_ALL}")
            
            # 询问用户是否更新
            if input("\n是否现在更新? (y/n): ").lower() != 'y':
                return False
                
            # 下载更新
            update_file = self.download_update(latest_info["download_url"])
            
            if not update_file:
                print(f"\n{Fore.RED}更新下载失败{Style.RESET_ALL}")
                return False
                
            print(f"\n{Fore.GREEN}更新下载完成{Style.RESET_ALL}")
            
            # 安装更新
            print(f"\n{Fore.YELLOW}正在安装更新...{Style.RESET_ALL}")
            if self.install_update(update_file):
                print(f"\n{Fore.GREEN}更新安装成功{Style.RESET_ALL}")
                return True
            else:
                print(f"\n{Fore.RED}更新安装失败{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            logger.error(f"更新过程失败: {str(e)}")
            print(f"\n{Fore.RED}更新过程出错: {str(e)}{Style.RESET_ALL}")
            return False 