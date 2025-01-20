import sys
import importlib
import subprocess
from datetime import datetime

# 改变标准输出和错误输出的编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def log_message(message):
    """
    打印带时间戳的日志信息，精确到毫秒。
    
    Parameters:
    - message: str, 要打印的日志信息。
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{current_time}] {message}")

def install_and_import(package):
    """
    检查包是否已安装，如果没有则安装它。

    Parameters:
    - package: str, 包的名称。
    """
    try:
        importlib.import_module(package)
        log_message(f"'{package}' already installed")
    except ImportError:
        log_message(f"'{package}' not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            log_message(f"'{package}' installation successful")
        except subprocess.CalledProcessError as e:
            log_message(f"Failed to install '{package}': {e}")

def main():
    required_packages = ['openpyxl', 'pandas', 'plotly']
    begin_time = datetime.now()
    log_message("Checking Python packages...")

    for package in required_packages:
        install_and_import(package)
    
    end_time = datetime.now()
    log_message(f"Checking Python packages done, duration: {end_time - begin_time}")

if __name__ == "__main__":
    main()
