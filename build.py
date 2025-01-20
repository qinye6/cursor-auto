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
        self.version = VERSION
        self.project_root = Path(__file__).parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
        # 设置输出文件名
        self.output_names = {
            "windows": "cursor-auto-windows-x64.exe",
            "linux": "cursor-auto-linux-x64",
            "darwin": "cursor-auto-darwin-x64"
        }
        
        # 设置图标路径
        self.icons = {
            "windows": "assets/icon.ico",
            "linux": "assets/icon.png",
            "darwin": "assets/icon.icns"
        }

    def create_spec(self, platform):
        """创建 .spec 文件"""
        output_name = f"cursor-auto-{platform}-x64-v{self.version}"
        icon_path = self.icons.get(platform)
        
        # 检查图标文件是否存在
        if icon_path and os.path.exists(icon_path):
            icon_config = f"icon=['{icon_path}']"
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

        # 平台特定的配置
        if platform == "windows":
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
        elif platform == "linux":
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
        else:  # darwin
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
)

app = BUNDLE(
    exe,
    name='{output_name}.app',
    {icon_config},
    bundle_identifier=None,
)"""

        # 创建 spec 文件
        spec_file = self.project_root / f"cursor_auto_{platform}.spec"
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(base_config + platform_config)
        
        return spec_file

    def build(self, platform):
        """构建指定平台的可执行文件"""
        try:
            print(f"\n{Fore.CYAN}[*] 开始构建 {platform.capitalize()} 版本...{Style.RESET_ALL}")
            
            # 创建 spec 文件
            spec_file = self.create_spec(platform)
            print(f"{Fore.CYAN}[*] 已创建 spec 文件: {spec_file}{Style.RESET_ALL}")
            
            # 构建命令
            cmd = [
                "pyinstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ]
            
            # 执行构建
            print(f"{Fore.CYAN}[*] 执行命令: {' '.join(cmd)}{Style.RESET_ALL}")
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            # 输出构建日志
            if process.stdout:
                print(f"[OUT] {process.stdout}")
            if process.stderr:
                print(f"[ERR] {process.stderr}")
            
            # 检查构建结果
            if process.returncode == 0:
                print(f"{Fore.GREEN}[+] {platform.capitalize()} 版本构建成功{Style.RESET_ALL}")
                
                try:
                    # 创建 releases 目录
                    releases_dir = self.project_root / "releases"
                    releases_dir.mkdir(exist_ok=True)
                    
                    # 根据平台处理文件
                    if platform == "windows":
                        src_file = self.dist_dir / "cursor-auto-windows-x64.exe"
                        dst_file = releases_dir / "cursor-auto-windows-x64.exe"
                    elif platform == "linux":
                        src_file = self.dist_dir / "cursor-auto-linux-x64.exe"
                        dst_file = releases_dir / "cursor-auto-linux-x64"
                    else:  # darwin
                        src_file = self.dist_dir / "cursor-auto-darwin-x64.exe"
                        dst_file = releases_dir / "cursor-auto-darwin-x64"
                    
                    # 复制文件
                    if src_file.exists():
                        shutil.copy2(src_file, dst_file)
                        print(f"{Fore.GREEN}[+] 文件已复制到: {dst_file}{Style.RESET_ALL}")
                        
                        # 设置可执行权限（对于 Linux 和 macOS）
                        if platform in ["linux", "darwin"]:
                            os.chmod(dst_file, 0o755)  # rwxr-xr-x
                            print(f"{Fore.GREEN}[+] 已设置可执行权限{Style.RESET_ALL}")
                        
                        # 处理 macOS 的 .app 包
                        if platform == "darwin":
                            app_src = self.dist_dir / "cursor-auto-darwin-x64.app"
                            if app_src.exists():
                                app_dst = releases_dir / "cursor-auto-darwin-x64.app"
                                if app_dst.exists():
                                    shutil.rmtree(app_dst)
                                shutil.copytree(app_src, app_dst)
                                print(f"{Fore.GREEN}[+] macOS App包已复制到: {app_dst}{Style.RESET_ALL}")
                        
                        return True
                    else:
                        print(f"{Fore.RED}[-] 找不到源文件: {src_file}{Style.RESET_ALL}")
                        return False
                        
                except Exception as e:
                    print(f"{Fore.RED}[-] 处理文件时出错: {str(e)}{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.RED}[-] {platform.capitalize()} 版本构建失败{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[-] 构建过程出错: {str(e)}{Style.RESET_ALL}")
            return False

    def build_all(self):
        """构建所有平台版本"""
        self.clean()
        
        results = {}
        for platform in ["windows", "darwin", "linux"]:
            results[platform] = self.build(platform)
        
        # 打印构建结果摘要
        print("\n构建结果摘要:")
        for platform_name, success in results.items():
            status = "成功" if success else "失败"
            color = Fore.GREEN if success else Fore.RED
            print(f"- {platform_name.capitalize()}: {color}{status}{Style.RESET_ALL}")

    def clean(self):
        """清理构建和分发目录"""
        print(f"{Fore.CYAN}[*] 清理旧的构建文件...{Style.RESET_ALL}")
        paths_to_clean = [
            self.dist_dir,
            self.build_dir,
            self.project_root / "releases"
        ]
        for path in paths_to_clean:
            if path.exists():
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"{Fore.YELLOW}[!] 清理 {path} 时出错: {str(e)}{Style.RESET_ALL}")


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
            print(f"{Fore.RED}[-] 不支持的平台: {platform}{Style.RESET_ALL}")
    else:
        # 构建所有平台
        builder.build_all()
