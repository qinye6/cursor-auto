import warnings
import os
import platform
import subprocess
import time
import threading
import sys
import shutil
from datetime import datetime
from pathlib import Path
from colorama import init, Fore, Style
from version import VERSION

# Ignore specific SyntaxWarning
warnings.filterwarnings("ignore", category=SyntaxWarning, module="DrissionPage")

# 设置控制台编码为 UTF-8
if sys.platform.startswith('win'):
    os.system('chcp 65001')

# 初始化colorama
init()

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


class Builder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.version = VERSION
        
        # 设置输出文件名
        self.output_names = {
            "windows": f"cursor-auto-windows-x64-v{VERSION}.exe",
            "linux": f"cursor-auto-linux-x64-v{VERSION}",
            "darwin": f"cursor-auto-darwin-x64-v{VERSION}"
        }
        
        # 设置图标路径
        self.icons = {
            "windows": "assets/icon.ico",
            "linux": "assets/icon.png",
            "darwin": "assets/icon.icns"
        }

    def print_message(self, message, type='info'):
        """打印带颜色的消息"""
        colors = {
            'info': Fore.CYAN,
            'success': Fore.GREEN,
            'error': Fore.RED,
            'warning': Fore.YELLOW
        }
        prefix = {
            'info': '[*]',
            'success': '[+]',
            'error': '[-]',
            'warning': '[!]'
        }
        color = colors.get(type, Fore.WHITE)
        try:
            print(f"{color}{prefix[type]} {message}{Style.RESET_ALL}")
        except UnicodeEncodeError:
            # 如果出现编码错误，尝试使用 ASCII 字符
            print(f"{color}{prefix[type]} {message.encode('ascii', 'replace').decode()}{Style.RESET_ALL}")

    def create_spec(self, platform):
        """创建 .spec 文件"""
        output_name = self.output_names[platform]
        icon_path = self.icons.get(platform)
        
        # 检查图标文件是否存在
        if icon_path and os.path.exists(icon_path):
            icon_config = f"icon='{icon_path}'"
        else:
            icon_config = "icon=None"
        
        # 基础配置
        base_config = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['cursor_pro_keep_alive.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)
"""

        # 平台特定配置
        if platform == "linux":
            platform_config = f"""
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{output_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
    {icon_config}
)"""
        elif platform == "darwin":
            platform_config = f"""
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{output_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_config}
)"""
        else:  # windows
            platform_config = f"""
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{output_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_config}
)"""

        # 创建 spec 文件
        spec_file = self.project_root / f"cursor_auto_{platform}.spec"
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(base_config + platform_config)
        
        return spec_file

    def verify_build(self, file_path):
        """验证构建文件"""
        if not file_path.exists():
            self.print_message(f"Build file not found: {file_path}", 'error')
            return False
        
        size = file_path.stat().st_size
        min_size = 1024 * 1024  # 1MB
        max_size = 1024 * 1024 * 1024  # 1GB
        
        if size < min_size:
            self.print_message(f"Build file too small: {size} bytes", 'error')
            return False
        if size > max_size:
            self.print_message(f"Build file too large: {size} bytes", 'warning')
        
        return True

    def build(self, platform):
        """构建指定平台的可执行文件"""
        try:
            self.print_message(f"Starting build for {platform.capitalize()}", 'info')
            
            # 创建必要的目录
            self.dist_dir.mkdir(exist_ok=True)
            
            # 构建文件名
            output_name = f"cursor-auto-{platform}-x64-v{self.version}"
            if platform == "windows":
                output_name += ".exe"
            
            # 设置输出路径
            output_path = self.dist_dir / output_name
            
            # 构建命令
            cmd = [
                "pyinstaller",
                "--clean",
                "--noconfirm",
                "--name", output_name,
                "--distpath", str(self.dist_dir),
                "--workpath", str(self.build_dir),
                "cursor_pro_keep_alive.py"
            ]
            
            # 添加图标
            if platform in self.icons and os.path.exists(self.icons[platform]):
                cmd.extend(["--icon", self.icons[platform]])
            
            # 执行构建
            self.print_message(f"Executing command: {' '.join(cmd)}", 'info')
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            # 输出构建日志
            if process.stdout:
                print(f"[OUT] {process.stdout}")
            if process.stderr:
                print(f"[ERR] {process.stderr}")
            
            # 检查构建结果
            if process.returncode == 0 and output_path.exists():
                self.print_message(f"Build successful: {output_path}", 'success')
                return True
            else:
                self.print_message("Build failed", 'error')
                return False
                
        except Exception as e:
            self.print_message(f"Build process error: {str(e)}", 'error')
            return False

    def build_all(self):
        """构建所有平台版本"""
        self.clean()
        
        results = {}
        for platform in ["windows", "darwin", "linux"]:
            results[platform] = self.build(platform)
        
        # 打印构建结果摘要
        print("\nBuild Summary:")
        for platform_name, success in results.items():
            status = "Success" if success else "Failed"
            color = Fore.GREEN if success else Fore.RED
            print(f"- {platform_name.capitalize()}: {color}{status}{Style.RESET_ALL}")

    def clean(self):
        """清理构建和分发目录"""
        self.print_message("Cleaning old build files", 'info')
        paths_to_clean = [
            self.dist_dir,
            self.build_dir,
            self.project_root / "release"
        ]
        for path in paths_to_clean:
            if path.exists():
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    self.print_message(f"Error cleaning {path}: {str(e)}", 'warning')


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
    builder = Builder()
    if len(sys.argv) > 1:
        # 构建指定平台
        platform = sys.argv[1].lower()
        if platform in ["windows", "darwin", "linux"]:
            builder.build(platform)
        else:
            builder.print_message(f"Unsupported platform: {platform}", 'error')
    else:
        # 构建所有平台
        builder.build_all()
