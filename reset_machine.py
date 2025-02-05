import os
import hashlib
import shutil
import uuid
import sys
import logging
from colorama import Fore, Style, init
from config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # 添加历史记录
        self.history = []
        # 添加备份管理
        self.backups = {}

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

            # 生成新的ID
            print(f"{Fore.CYAN}{EMOJI['RESET']} 生成新的机器标识...{Style.RESET_ALL}")
            new_ids = self.generate_new_ids()

            # 更新系统级别的ID
            if not self.update_system_ids(new_ids):
                print(f"{Fore.YELLOW}{EMOJI['INFO']} 系统级别ID更新失败，继续更新应用级别ID...{Style.RESET_ALL}")

            # 备份和更新配置文件
            success = self.update_config_file(new_ids)
            if not success:
                return False

            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 机器标识重置成功！{Style.RESET_ALL}")
            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 重置过程出错: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Reset process failed: {e}")
            return False

    def update_system_ids(self, new_ids):
        """更新系统级别的ID"""
        try:
            print(f"{Fore.CYAN}{EMOJI['INFO']} 正在更新系统标识...{Style.RESET_ALL}")
            
            if sys.platform.startswith("win"):
                self._update_windows_machine_guid()
            elif sys.platform == "darwin":
                self._update_macos_platform_uuid(new_ids)
                
            print(f"{Fore.GREEN}{EMOJI['SUCCESS']} 系统标识更新成功{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 系统标识更新失败: {str(e)}{Style.RESET_ALL}")
            logger.error(f"System IDs update failed: {e}")
            return False

    def _update_windows_machine_guid(self):
        """更新Windows MachineGuid"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SOFTWARE\\Microsoft\\Cryptography",
                0,
                winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
            )
            new_guid = str(uuid.uuid4())
            winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
            winreg.CloseKey(key)
            logger.info("Windows MachineGuid updated successfully")
        except PermissionError:
            print(f"{Fore.YELLOW}{EMOJI['INFO']} 需要管理员权限来更新Windows MachineGuid{Style.RESET_ALL}")
            raise
        except Exception as e:
            logger.error(f"Failed to update Windows MachineGuid: {e}")
            raise

    def _update_macos_platform_uuid(self, new_ids):
        """更新macOS Platform UUID"""
        try:
            uuid_file = "/var/root/Library/Preferences/SystemConfiguration/com.apple.platform.uuid.plist"
            if os.path.exists(uuid_file):
                # 使用sudo来执行plutil命令
                cmd = f'sudo plutil -replace "UUID" -string "{new_ids["telemetry.macMachineId"]}" "{uuid_file}"'
                result = os.system(cmd)
                if result == 0:
                    logger.info("macOS Platform UUID updated successfully")
                else:
                    raise Exception("Failed to execute plutil command")
        except Exception as e:
            logger.error(f"Failed to update macOS Platform UUID: {e}")
            raise

    def update_config_file(self, new_ids):
        """更新配置文件"""
        try:
            # 读取现有配置
            print(f"{Fore.CYAN}{EMOJI['FILE']} 读取当前配置...{Style.RESET_ALL}")
            import json
            with open(self.db_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 备份原文件
            backup_path = self.db_path + '.bak'
            print(f"{Fore.YELLOW}{EMOJI['BACKUP']} 创建配置备份: {backup_path}{Style.RESET_ALL}")
            shutil.copy2(self.db_path, backup_path)

            # 更新配置
            config.update(new_ids)

            # 保存新配置
            print(f"{Fore.CYAN}{EMOJI['FILE']} 保存新配置...{Style.RESET_ALL}")
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)

            print(f"\n{Fore.CYAN}新的机器标识:{Style.RESET_ALL}")
            for key, value in new_ids.items():
                print(f"{EMOJI['INFO']} {key}: {Fore.GREEN}{value}{Style.RESET_ALL}")

            return True

        except Exception as e:
            print(f"{Fore.RED}{EMOJI['ERROR']} 配置文件更新失败: {str(e)}{Style.RESET_ALL}")
            logger.error(f"Config file update failed: {e}")
            return False

    def backup_ids(self):
        """备份当前标识"""
        current_ids = self.get_current_ids()
        backup_id = str(uuid.uuid4())
        self.backups[backup_id] = current_ids
        return backup_id
        
    def restore_backup(self, backup_id):
        """恢复备份"""
        if backup_id in self.backups:
            return self.set_machine_ids(self.backups[backup_id])

if __name__ == "__main__":
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{EMOJI['RESET']} Cursor 机器标识重置工具{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    
    resetter = MachineIDResetter()
    resetter.reset_machine_ids()
    
    print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    input(f"{EMOJI['INFO']} 按回车键退出...") 