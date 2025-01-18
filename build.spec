# -*- mode: python ; coding: utf-8 -*-
import sys
import platform

block_cipher = None

# 确保 turnstilePatch 目录存在并包含所需文件
import os
turnstile_dir = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'turnstilePatch')
if not os.path.exists(turnstile_dir):
    os.makedirs(turnstile_dir)

# 平台特定配置
is_windows = platform.system().lower() == 'windows'
is_mac = platform.system().lower() == 'darwin'
is_linux = platform.system().lower() == 'linux'

# 基础依赖
hidden_imports = [
    'colorama',
    'requests',
    'psutil',
    'DrissionPage',
    'email_api',
    'get_email_code',
]

# 平台特定依赖
if is_windows:
    hidden_imports.extend([
        'win32console',
        'win32gui',
        'ctypes',
        'win32api',
        'win32con',
    ])

a = Analysis(
    ['cursor_pro_keep_alive.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.png', '.'),
        ('email_api.py', '.'),
        ('get_email_code.py', '.'),
        ('turnstilePatch/*', 'turnstilePatch/'),
        ('config.template.json', '.'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 平台特定的可执行文件配置
if is_windows:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='Cursor-auto',
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
        icon='logo.png',
        version='file_version_info.txt',
        uac_admin=True,
    )
elif is_mac:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='Cursor-auto',
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
        icon='logo.png',
    )
else:  # Linux
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='Cursor-auto',
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
    ) 