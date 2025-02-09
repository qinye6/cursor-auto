# 🚀 Cursor Auto

<div align="center">

![Cursor Auto](logo.png)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)](https://github.com/qinye6/cursor-auto)

[English](README_EN.md) | 简体中文

</div>

## 📖 项目介绍

Cursor Auto 是一个强大的自动化工具，用于自动构建和管理 Cursor 试用账号。本工具支持 Windows、macOS 和 Linux 平台，提供了直观的界面和完整的功能集。

### ✨ 核心功能

- 🔄 自动账号管理
  - 自动注册新账号
  - 自动验证邮箱
  - 智能账号轮换
- 🌐 跨平台支持
  - Windows 系统支持
  - macOS 系统支持
  - Linux 系统支持
- 🛠 智能构建系统
  - 自动环境检测
  - 依赖自动安装
  - 构建过程可视化
- 📊 完整日志系统
  - 详细的运行日志
  - 错误追踪和诊断
  - 性能监控

## 🔧 环境要求

### 基础环境
- 🐍 Python 3.7+
- 📦 pip (Python包管理器)
- 🔄 Git (可选，用于版本控制)

### 系统要求
- 💻 Windows 10/11
- 🍎 macOS 10.15+
- 🐧 Linux (主流发行版)

### 浏览器要求
- 🌐 支持以下任一浏览器：
  - Google Chrome
  - Microsoft Edge
  - Brave Browser
  
注意：浏览器最好为最新版本以确保兼容性。

### Python 依赖
```bash
# 核心依赖
colorama==0.4.6        # 终端颜色支持
DrissionPage==4.1.0.17 # 浏览器自动化
psutil==5.9.8         # 系统资源监控
requests==2.31.0      # HTTP 请求处理
pyinstaller==6.3.0    # 应用打包工具

# 平台特定依赖
pywin32==306          # 仅 Windows 平台需要
```

## 🚀 快速开始

### 📥 下载和安装

1. 克隆仓库：
```bash
git clone https://github.com/qinye6/cursor-auto.git
cd cursor-auto
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

### 💻 使用方法

#### Windows 平台

```batch
# 方法 1：以管理员身份运行
右键 build.bat -> 以管理员身份运行

# 方法 2：命令行运行(需要管理员权限)
以管理员身份运行命令提示符
cd /d "项目目录"
build.bat
```

⚠️ **注意**: Windows 平台需要管理员权限才能正常运行程序，因为需要修改系统注册表。

#### macOS 平台

```bash
# 添加执行权限
chmod +x build.mac.command

# 运行脚本 (需要 sudo 权限)
sudo ./build.mac.command
```

⚠️ **注意**: macOS 平台需要 sudo 权限才能正常运行程序，因为需要修改系统标识。

#### Linux 平台

```bash
# 添加执行权限
chmod +x build.sh

# 运行脚本
./build.sh
```

## 📁 项目结构

```
cursor-auto/
├── 📜 build.py           # 主构建脚本
├── 🔧 build.bat          # Windows构建脚本
├── 🔧 build.mac.command  # macOS构建脚本
├── 🔧 build.sh           # Linux构建脚本
├── 📋 build.spec         # PyInstaller配置
├── 📦 requirements.txt   # 依赖清单
├── ⚙️ config.template.json # 配置模板
├── 📊 logger.py          # 日志管理
├── 🌐 browser_utils.py   # 浏览器工具
├── 📧 email_api.py       # 邮件接口
├── 🔑 cursor_auth_manager.py # 认证管理
├── 🤖 cursor_pro_keep_alive.py # 主程序
├── 📁 logs/             # 日志目录
├── 📁 dist/             # 构建输出
└── 📁 build/            # 临时文件
```

## ⚙️ 配置说明

### 配置文件
项目使用 JSON 格式的配置文件：

1. `config.template.json`: 配置模板
```json
{
    "email": {
        "service": "your_service",
        "username": "your_email",
        "password": "your_password"
    },
    "browser": {
        "type": "chrome",
        "headless": false
    }
}
```

2. `config.json`: 本地配置（从模板复制修改）

### 环境变量
支持通过环境变量覆盖配置：
- `CURSOR_EMAIL_SERVICE`
- `CURSOR_EMAIL_USERNAME`
- `CURSOR_EMAIL_PASSWORD`
- `CURSOR_BROWSER_TYPE`

### 临时邮箱
本项目使用了[[cloudflare_temp_email](https://github.com/dreamhunter2333/cloudflare_temp_email)]临时邮箱获取注册邮箱api<br>可以查看相关[[部署文档](https://temp-mail-docs.awsl.uk/zh/guide/github-action)]来部署到cloudfalare上使用

## 📝 日志系统

### 日志级别
- 🔴 ERROR: 错误信息
- 🟡 WARNING: 警告信息
- 🔵 INFO: 一般信息
- 🟢 DEBUG: 调试信息

### 日志位置
- 构建日志：`logs/build_YYYYMMDD_HHMMSS.log`
- 运行日志：`logs/runtime_YYYYMMDD_HHMMSS.log`

## ❗ 常见问题

### 1. 构建相关
- ❓ **问题**: 构建失败，提示缺少依赖
  - ✅ **解决**: 运行 `pip install -r requirements.txt`

- ❓ **问题**: PyInstaller 打包错误
  - ✅ **解决**: 清理 `build` 和 `dist` 目录后重试

### 2. 运行相关
- ❓ **问题**: 浏览器启动失败
  - ✅ **解决**: 检查 Chrome/Edge/Brave 是否正确安装，并确保为最新版本
  - ✅ **解决**: 确保浏览器没有被其他程序占用
  - ✅ **解决**: 检查浏览器驱动是否与浏览器版本匹配

- ❓ **问题**: 浏览器自动化失败
  - ✅ **解决**: 关闭浏览器的开发者模式
  - ✅ **解决**: 清除浏览器缓存和 Cookie
  - ✅ **解决**: 检查是否有反自动化插件在运行

- ❓ **问题**: 邮箱验证失败
  - ✅ **解决**: 检查邮箱配置和网络连接

## 🔨 开发指南

### 代码风格
- 遵循 PEP 8 规范
- 使用类型注解
- 添加详细注释

### 提交规范
```
feat: 新功能
fix: 修复问题
docs: 文档更新
style: 代码格式
refactor: 代码重构
test: 测试相关
chore: 构建相关
```

### 开发流程
1. 创建功能分支
2. 开发新功能
3. 编写测试用例
4. 提交代码审查
5. 合并到主分支

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 🙏 致谢

本项目参考了以下优秀的开源项目：

- [cursor-auto-free](https://github.com/chengazhen/cursor-auto-free) - 提供了基础的自动化框架和邮箱验证逻辑
- [gpt-cursor-auto](https://github.com/hmhm2022/gpt-cursor-auto) - 提供了 ChatGPT Access Token 获取的思路
- [cursor-auto-free](https://github.com/yeongpin/cursor-auto-free) - 提供了额外的功能特性参考

感谢这些项目的开发者为开源社区做出的贡献！

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 👥 贡献者

感谢所有贡献者的付出！

## 📞 联系方式

- 📧 Email: tmpemail@qinye.asia

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=qinye6/cursor-auto&type=Date)](https://star-history.com/#qinye6/cursor-auto&Date)

---

<div align="center">

**如果这个项目对您有帮助，请考虑给它一个 Star ⭐️**

</div> 