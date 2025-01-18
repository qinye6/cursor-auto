import os
import hashlib
import shutil
import uuid
from colorama import Fore, Style, init
from config import Config

# 初始化colorama
init()

# 定义emoji和颜色常量
EMOJI = {
    'FILE': '📄',
    'BACKUP': '💾',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'INFO': 'ℹ️',
    'RESET': '🔄',
    'ROCKET': '🚀'
}

class MachineIDResetter:
    def __init__(self):
        # 判断操作系统
        if os.name == "nt":  # Windows
            self.db_path = os.path.join(
                os.getenv("APPDATA"), "Cursor", "User", "globalStorage", "storage.json"
            )
        else:  # macOS
            self.db_path = os.path.expanduser(
                "~/Library/Application Support/Cursor/User/globalStorage/storage.json"
            )

    def generate_new_ids(self):
        """生成新的机器ID"""
        # 生成新的UUID
        dev_device_id = str(uuid.uuid4())
        
        # 生成新的machineId (64个字符的十六进制)
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()
        
        # 生成新的macMachineId (128个字符的十六进制)
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()
        
        # 生成新的sqmId
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"
        
        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id
        }

    def reset_machine_ids(self):
        """重置机器ID并备份原文件"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} 正在检查配置文件...{Style.RESET_ALL}")
            
            # 检查文件是否存在
            if not os.path.exists(self.db_path):
                print(f"{Fore.RED}{EMOJI['ERROR']} 配置文件不存在: {self.db_path}{Style.RESET_ALL}")
                return False

            # 读取现有配置
            print(f"{Fore.CYAN}{EMOJI['FILE']} 读取当前配置...{Style.RESET_ALL}")
            import json
            with open(self.db_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 备份原文件
            backup_path = self.db_path + '.bak'
            print(f"{Fore.YELLOW}{EMOJI['BACKUP']} 创建配置备份: {backup_path}{Style.RESET_ALL}")
            shutil.copy2(self.db_path, backup_path)

            # 生成新的ID
            print(f"{Fore.CYAN}{EMOJI['RESET']} 生成新的机器标识...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            # 更新配置
            config.update(new_ids)

            # 保存新配置
            print(f"{Fore.CYAN}{EMOJI['FILE']} 保存新配置...{Style.RESET_ALL}")
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 机器标识重置成功！{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}新的机器标识:{Style.RESET_ALL}")
            for key, value in new_ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")
            
            # 修改自动启动部分
            config = Config()
            if config.get('cursor.auto_start', True):
                cursor_path = config.get('cursor.path', '')
                if not cursor_path or not os.path.exists(cursor_path):
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} Cursor 路径未配置或不存在，跳过自动启动{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.CYAN}{EMOJI['ROCKET']} 正在启动 Cursor...{Style.RESET_ALL}")
                    try:
                        import subprocess
                        import sys
                        
                        if os.name == 'nt':  # Windows
                            # 创建一个新的进程组
                            startupinfo = subprocess.STARTUPINFO()
                            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                            startupinfo.wShowWindow = subprocess.SW_HIDE
                            
                            # 使用 creationflags 来创建新的进程组
                            process = subprocess.Popen(
                                [cursor_path],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL,
                                startupinfo=startupinfo,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                            )
                        else:  # macOS
                            process = subprocess.Popen(
                                ['open', cursor_path],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL,
                                preexec_fn=os.setsid  # 在新的会话中运行
                            )
                        
                        # 等待一小段时间检查进程是否成功启动
                        import time
                        time.sleep(2)
                        
                        if process.poll() is None:  # 进程正在运行
                            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} Cursor 已成功启动{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} Cursor 启动失败，请手动启动{Style.RESET_ALL}")
                            
                    except Exception as e:
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} Cursor 启动时出现错误: {str(e)}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} 请尝试手动启动 Cursor{Style.RESET_ALL}")
            
            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 重置过程出错: {str(e)}{Style.RESET_ALL}")
            return False


if __name__ == "__main__":
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Cursor 机器标识重置工具{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    resetter = MachineIDResetter()
    resetter.reset_machine_ids()
    
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} 按回车键退出...") 