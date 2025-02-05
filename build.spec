# -*- mode: python ; coding: utf-8 -*-
import sys
import platform
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# 收集所有需要的数据和二进制文件
def collect_pkg_data(package):
    datas, binaries, hiddenimports = collect_all(package)
    return datas, binaries, hiddenimports

# 收集各个包的数据
browser_datas, browser_binaries, browser_hiddenimports = collect_pkg_data('browser_utils')
config_datas, config_binaries, config_hiddenimports = collect_pkg_data('config')
email_datas, email_binaries, email_hiddenimports = collect_pkg_data('email_api')

# 合并所有收集到的数据
all_datas = []
all_datas.extend(browser_datas)
all_datas.extend(config_datas)
all_datas.extend(email_datas)

all_binaries = []
all_binaries.extend(browser_binaries)
all_binaries.extend(config_binaries)
all_binaries.extend(email_binaries)

all_hiddenimports = []
all_hiddenimports.extend(browser_hiddenimports)
all_hiddenimports.extend(config_hiddenimports)
all_hiddenimports.extend(email_hiddenimports)

# 添加基本的隐藏导入
all_hiddenimports.extend([
    'playwright',
    'asyncio',
    'colorama',
    'psutil',
    'winreg',
    'email_generator',
    'browser_utils',
    'get_email_code',
    'reset_machine',
    'auto_updater',
    'config',
    'logo',
    'exit_cursor',
    'DrissionPage',
    'requests',
    'json',
    'logging',
    'datetime',
    'uuid',
    'random',
    'time',
    'os',
    'sys',
    'shutil',
    'traceback',
    'subprocess',
    'threading',
])

# 添加平台特定的依赖
if platform.system() == 'Windows':
    all_hiddenimports.extend([
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'win32com.client',
        'win32security',
        'win32event',
        'winerror',
        'pywintypes',
    ])

a = Analysis(
    ['cursor_pro_keep_alive.py'],
    pathex=[],
    binaries=all_binaries,
    datas=[
        *all_datas,
        ('config.template.json', '.'),
        ('logo.txt', '.'),
        ('logo.png', '.'),
        ('email_api.py', '.'),
        ('get_email_code.py', '.'),
        ('turnstilePatch/*', 'turnstilePatch/'),
        ('email_generator.py', '.'),
        ('browser_utils.py', '.'),
        ('reset_machine.py', '.'),
        ('auto_updater.py', '.'),
        ('config.py', '.'),
        ('logo.py', '.'),
        ('exit_cursor.py', '.'),
    ],
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Cursor Auto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.png',  # 确保有这个图标文件
) 