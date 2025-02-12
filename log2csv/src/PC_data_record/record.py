import subprocess
import sys

# 定义需要检查和安装的包列表
required_packages = ['psutil', 'matplotlib', 'pandas']

# 检查并安装缺失的包
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        print(f"Package {package} is not installed. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed {package}.")
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}. Please install it manually.")

import psutil
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import time

# 初始化历史数据列表
cpu_history = []
memory_history = []
disk_read_history = []
disk_write_history = []
time_history = []

# 创建主窗口
root = tk.Tk()
root.title("System Resource Monitoring")

# 创建图形，包含 4 个子图
fig, axs = plt.subplots(4, 1, figsize=(8, 12))
axs[0].set_title('CPU Usage (%)')
axs[0].set_xlabel('Time')
axs[0].set_ylabel('Usage')
axs[1].set_title('Memory Usage (%)')
axs[1].set_xlabel('Time')
axs[1].set_ylabel('Usage')
axs[2].set_title('Disk Read Rate (KB/s)')
axs[2].set_xlabel('Time')
axs[2].set_ylabel('Rate')
axs[3].set_title('Disk Write Rate (KB/s)')
axs[3].set_xlabel('Time')
axs[3].set_ylabel('Rate')

# 创建画布并将图形嵌入到 Tkinter 窗口中
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# 定义更新函数，用于实时更新资源数据和图表
def update():
    global cpu_history, memory_history, disk_read_history, disk_write_history, time_history

    # 获取当前时间
    current_time = time.strftime("%H:%M:%S")

    # 获取 CPU 使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    # 获取内存使用率
    memory_percent = psutil.virtual_memory().percent

    # 获取磁盘 I/O 统计信息
    disk_io_counters = psutil.disk_io_counters()
    disk_read_bytes = disk_io_counters.read_bytes
    disk_write_bytes = disk_io_counters.write_bytes

    # 计算磁盘读写速率
    if len(disk_read_history) > 0:
        disk_read_rate = (disk_read_bytes - disk_read_history[-1]) / 1024
        disk_write_rate = (disk_write_bytes - disk_write_history[-1]) / 1024
    else:
        disk_read_rate = 0
        disk_write_rate = 0

    # 将数据添加到历史数据列表中
    cpu_history.append(cpu_percent)
    memory_history.append(memory_percent)
    disk_read_history.append(disk_read_bytes)
    disk_write_history.append(disk_write_bytes)
    time_history.append(current_time)

    # 清除子图并重新绘制曲线
    axs[0].clear()
    axs[0].plot(time_history, cpu_history)
    axs[0].set_title('CPU Usage (%)')
    axs[0].set_xlabel('Time')
    axs[0].set_ylabel('Usage')
    axs[0].tick_params(axis='x', rotation=45)

    axs[1].clear()
    axs[1].plot(time_history, memory_history)
    axs[1].set_title('Memory Usage (%)')
    axs[1].set_xlabel('Time')
    axs[1].set_ylabel('Usage')
    axs[1].tick_params(axis='x', rotation=45)

    axs[2].clear()
    axs[2].plot(time_history[1:], [disk_read_history[i + 1] - disk_read_history[i] / 1024 for i in range(len(disk_read_history) - 1)])
    axs[2].set_title('Disk Read Rate (KB/s)')
    axs[2].set_xlabel('Time')
    axs[2].set_ylabel('Rate')
    axs[2].tick_params(axis='x', rotation=45)

    axs[3].clear()
    axs[3].plot(time_history[1:], [disk_write_history[i + 1] - disk_write_history[i] / 1024 for i in range(len(disk_write_history) - 1)])
    axs[3].set_title('Disk Write Rate (KB/s)')
    axs[3].set_xlabel('Time')
    axs[3].set_ylabel('Rate')
    axs[3].tick_params(axis='x', rotation=45)

    # 调整图形布局
    fig.tight_layout()

    # 更新画布显示
    canvas.draw()

    # 将历史数据保存到 CSV 文件中
    data = {
        'Time': time_history,
        'CPU Usage': cpu_history,
        'Memory Usage': memory_history,
        'Disk Read Rate (KB/s)': [0] + [disk_read_history[i + 1] - disk_read_history[i] / 1024 for i in range(len(disk_read_history) - 1)],
        'Disk Write Rate (KB/s)': [0] + [disk_write_history[i + 1] - disk_write_history[i] / 1024 for i in range(len(disk_write_history) - 1)]
    }
    df = pd.DataFrame(data)
    df.to_csv('system_resource_history.csv', index=False)

    # 每隔 1 秒调用一次 update 函数进行更新
    root.after(1000, update)

# 启动更新函数
update()

# 进入 Tkinter 主事件循环
root.mainloop()