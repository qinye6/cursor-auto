import warnings
import os
import platform
import subprocess
import time
import threading
import sys
import shutil
from datetime import datetime

# Ignore specific SyntaxWarning
warnings.filterwarnings("ignore", category=SyntaxWarning, module="DrissionPage")

CURSOR_LOGO = """
   ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗     
  ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗    
  ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝    
  ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗    
  ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║    
   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝    
                █████╗ ██╗   ██╗████████╗ ██████╗         
               ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗        
               ███████║██║   ██║   ██║   ██║   ██║        
               ██╔══██║██║   ██║   ██║   ██║   ██║        
               ██║  ██║╚██████╔╝   ██║   ╚██████╔╝        
               ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝         
    ██████╗ ██╗   ██╗██╗██╗     ██████╗                  
    ██╔══██╗██║   ██║██║██║     ██╔══██╗                 
    ██████╔╝██║   ██║██║██║     ██║  ██║                 
    ██╔══██╗██║   ██║██║██║     ██║  ██║                 
    ██████╔╝╚██████╔╝██║███████╗██████╔╝                 
    ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚═════╝                  
"""

# 添加日志记录
def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    return log_file

def log_message(log_file, message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
    if level == "ERROR":
        print(f"\033[91m{message}\033[0m")
    elif level == "WARNING":
        print(f"\033[93m{message}\033[0m")
    else:
        print(message)


class LoadingAnimation:
    def __init__(self):
        self.is_running = False
        self.animation_thread = None

    def start(self, message="Building"):
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate, args=(message,))
        self.animation_thread.start()

    def stop(self):
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        print("\r" + " " * 70 + "\r", end="", flush=True)  # Clear the line

    def _animate(self, message):
        animation = "|/-\\"
        idx = 0
        while self.is_running:
            print(f"\r{message} {animation[idx % len(animation)]}", end="", flush=True)
            idx += 1
            time.sleep(0.1)


def print_logo():
    print("\033[96m" + CURSOR_LOGO + "\033[0m")
    print("\033[93m" + "Building Cursor Keep Alive...".center(56) + "\033[0m\n")


def progress_bar(progress, total, prefix="", length=50):
    filled = int(length * progress // total)
    bar = "█" * filled + "░" * (length - filled)
    percent = f"{100 * progress / total:.1f}"
    print(f"\r{prefix} |{bar}| {percent}% Complete", end="", flush=True)
    if progress == total:
        print()


def simulate_progress(message, duration=1.0, steps=20):
    print(f"\033[94m{message}\033[0m")
    for i in range(steps + 1):
        time.sleep(duration / steps)
        progress_bar(i, steps, prefix="Progress:", length=40)


def filter_output(output):
    """ImportantMessage"""
    if not output:
        return ""
    important_lines = []
    for line in output.split("\n"):
        # Only keep lines containing specific keywords
        if any(
            keyword in line.lower()
            for keyword in ["error:", "failed:", "completed", "directory:"]
        ):
            important_lines.append(line)
    return "\n".join(important_lines)


def check_environment():
    """检查构建环境"""
    required_tools = {
        "python": "python --version",
        "pip": "pip --version",
        "pyinstaller": "pyinstaller --version"
    }
    
    for tool, command in required_tools.items():
        try:
            subprocess.run(command.split(), check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False, f"{tool} not found or not working properly"
    return True, "Environment check passed"


def get_platform_config():
    """获取平台特定的配置"""
    system = platform.system().lower()
    configs = {
        "windows": {
            "spec_file": "build.spec",
            "output_dir": "dist/windows",
            "separator": "\\",
            "executable_ext": ".exe"
        },
        "darwin": {
            "spec_file": "build.spec",
            "output_dir": "dist/mac",
            "separator": "/",
            "executable_ext": ".app"
        },
        "linux": {
            "spec_file": "build.spec",
            "output_dir": "dist/linux",
            "separator": "/",
            "executable_ext": ""
        }
    }
    return configs.get(system)


def build():
    # 设置日志
    log_file = setup_logging()
    log_message(log_file, "Starting build process")

    # 清屏
    os.system("cls" if platform.system().lower() == "windows" else "clear")
    print_logo()

    # 环境检查
    env_ok, env_message = check_environment()
    if not env_ok:
        log_message(log_file, f"Environment check failed: {env_message}", "ERROR")
        return

    # 获取平台配置
    platform_config = get_platform_config()
    if not platform_config:
        log_message(log_file, f"Unsupported operating system: {platform.system()}", "ERROR")
        return

    # 创建输出目录
    os.makedirs(platform_config["output_dir"], exist_ok=True)
    log_message(log_file, f"Created output directory: {platform_config['output_dir']}")

    # 构建命令
    pyinstaller_command = [
        "pyinstaller",
        platform_config["spec_file"],
        "--distpath", platform_config["output_dir"],
        "--workpath", f"build/{platform.system().lower()}",
        "--noconfirm"
    ]

    # 执行构建
    loading = LoadingAnimation()
    try:
        loading.start("Building in progress")
        result = subprocess.run(pyinstaller_command, check=True, capture_output=True, text=True)
        loading.stop()

        # 处理输出
        if result.stderr:
            log_message(log_file, "Build warnings/errors:", "WARNING")
            log_message(log_file, result.stderr)
        
        # 复制配置文件
        if os.path.exists("config.template.json"):
            config_dest = os.path.join(platform_config["output_dir"], "config.json")
            shutil.copy2("config.template.json", config_dest)
            log_message(log_file, f"Copied configuration file to {config_dest}")

        log_message(log_file, "Build completed successfully!")
        print(f"\n\033[92mBuild completed successfully! Output directory: {platform_config['output_dir']}\033[0m")

    except subprocess.CalledProcessError as e:
        loading.stop()
        log_message(log_file, f"Build failed with error code {e.returncode}", "ERROR")
        if e.stderr:
            log_message(log_file, e.stderr, "ERROR")
    except Exception as e:
        loading.stop()
        log_message(log_file, f"Unexpected error: {str(e)}", "ERROR")
    finally:
        loading.stop()


if __name__ == "__main__":
    build()
