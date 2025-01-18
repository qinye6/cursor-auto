# 🚀 Cursor Auto

<div align="center">

![Cursor Auto](logo.png)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg)](https://github.com/qinye6/cursor-auto)

English | [简体中文](README.md)

</div>

## 📖 Introduction

Cursor Auto is a powerful automation tool for building and managing Cursor trial accounts. This tool supports Windows, macOS, and Linux platforms, providing an intuitive interface and comprehensive functionality.

### ✨ Core Features

- 🔄 Automatic Account Management
  - Auto account registration
  - Email verification automation
  - Smart account rotation
- 🌐 Cross-Platform Support
  - Windows support
  - macOS support
  - Linux support
- 🛠 Intelligent Build System
  - Automatic environment detection
  - Dependency auto-installation
  - Build process visualization
- 📊 Complete Logging System
  - Detailed runtime logs
  - Error tracking and diagnostics
  - Performance monitoring

## 🔧 Requirements

### Basic Environment
- 🐍 Python 3.7+
- 📦 pip (Python package manager)
- 🔄 Git (optional, for version control)

### System Requirements
- 💻 Windows 10/11
- 🍎 macOS 10.15+
- 🐧 Linux (major distributions)

### Browser Requirements
- 🌐 Supports any of the following browsers:
  - Google Chrome
  - Microsoft Edge
  - Brave Browser
  
Note: The browser should be the latest version to ensure compatibility.

### Python Dependencies
```bash
# Core dependencies
colorama==0.4.6        # Terminal color support
DrissionPage==4.1.0.17 # Browser automation
psutil==5.9.8         # System resource monitoring
requests==2.31.0      # HTTP request handling
pyinstaller==6.3.0    # Application packaging

# Platform-specific dependencies
pywin32==306          # Windows only
```

## 🚀 Quick Start

### 📥 Download and Install

1. Clone the repository:
```bash
git clone https://github.com/qinye6/cursor-auto.git
cd cursor-auto
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 💻 Usage

#### Windows Platform

```batch
# Method 1: Double-click
Double-click build.bat

# Method 2: Command line
build.bat
```

#### macOS Platform

```bash
# Add execution permission
chmod +x build.mac.command

# Run script
./build.mac.command
```

#### Linux Platform

```bash
# Add execution permission
chmod +x build.sh

# Run script
./build.sh
```

## 📁 Project Structure

```
cursor-auto/
├── 📜 build.py           # Main build script
├── 🔧 build.bat          # Windows build script
├── 🔧 build.mac.command  # macOS build script
├── 🔧 build.sh           # Linux build script
├── 📋 build.spec         # PyInstaller config
├── 📦 requirements.txt   # Dependencies list
├── ⚙️ config.template.json # Config template
├── 📊 logger.py          # Log management
├── 🌐 browser_utils.py   # Browser utilities
├── 📧 email_api.py       # Email interface
├── 🔑 cursor_auth_manager.py # Auth management
├── 🤖 cursor_pro_keep_alive.py # Main program
├── 📁 logs/             # Log directory
├── 📁 dist/             # Build output
└── 📁 build/            # Temporary files
```

## ⚙️ Configuration

### Config Files
The project uses JSON format configuration files:

1. `config.template.json`: Configuration template
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

2. `config.json`: Local configuration (copy from template)

### Environment Variables
Configuration can be overridden via environment variables:
- `CURSOR_EMAIL_SERVICE`
- `CURSOR_EMAIL_USERNAME`
- `CURSOR_EMAIL_PASSWORD`
- `CURSOR_BROWSER_TYPE`

### Temporary Email
This project uses the [[cloudflare_temp_email](https://github.com/dreamhunter2333/cloudflare_temp_email)] temporary email API to obtain registration emails. You can refer to the [[deployment documentation](https://temp-mail-docs.awsl.uk/en/cli.html)] to deploy it to Cloudflare.

## 📝 Logging System

### Log Levels
- 🔴 ERROR: Error messages
- 🟡 WARNING: Warning messages
- 🔵 INFO: General information
- 🟢 DEBUG: Debug information

### Log Locations
- Build logs: `logs/build_YYYYMMDD_HHMMSS.log`
- Runtime logs: `logs/runtime_YYYYMMDD_HHMMSS.log`

## ❗ Common Issues

### 1. Build Related
- ❓ **Issue**: Build fails with missing dependencies
  - ✅ **Solution**: Run `pip install -r requirements.txt`

- ❓ **Issue**: PyInstaller packaging error
  - ✅ **Solution**: Clean `build` and `dist` directories and retry

### 2. Runtime Related
- ❓ **Issue**: Browser launch failure
  - ✅ **Solution**: Check if Chrome/Edge/Brave is properly installed and up to date
  - ✅ **Solution**: Ensure browser is not being used by other processes
  - ✅ **Solution**: Verify browser driver matches browser version

- ❓ **Issue**: Browser automation failure
  - ✅ **Solution**: Disable browser developer mode
  - ✅ **Solution**: Clear browser cache and cookies
  - ✅ **Solution**: Check for anti-automation plugins

- ❓ **Issue**: Email verification failure
  - ✅ **Solution**: Check email configuration and network connection

## 📄 Development Guide

### Code Style
- Follow PEP 8 guidelines
- Use type annotations
- Add detailed comments

### Commit Convention
```
feat: New feature
fix: Bug fix
docs: Documentation update
style: Code formatting
refactor: Code refactoring
test: Testing related
chore: Build related
```

### Development Process
1. Create feature branch
2. Develop new feature
3. Write test cases
4. Submit code review
5. Merge to main branch

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 🙏 Acknowledgments

This project was inspired by and references the following excellent open source projects:

- [cursor-auto-free](https://github.com/chengazhen/cursor-auto-free) - Provided the basic automation framework and email verification logic
- [gpt-cursor-auto](https://github.com/hmhm2022/gpt-cursor-auto) - Provided insights into ChatGPT Access Token acquisition
- [cursor-auto-free](https://github.com/yeongpin/cursor-auto-free) - Provided additional feature references

Thanks to the developers of these projects for their contributions to the open source community!

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 👥 Contributors

Thanks to all contributors!

## 📞 Contact

- 📧 Email: tmpemail@qinye.asia

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=qinye6/cursor-auto&type=Date)](https://star-history.com/#qinye6/cursor-auto&Date)

---

<div align="center">

**If this project helps you, please consider giving it a star ⭐️**

</div> 