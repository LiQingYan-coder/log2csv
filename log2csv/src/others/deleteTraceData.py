import tkinter as tk
from tkinter import filedialog
import os
import shutil


def delete_trace_data_folders():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 弹出对话框让用户选择文件夹
    selected_folder = filedialog.askdirectory()
    if not selected_folder:
        print("没有选择文件夹，操作取消")
        return

    # 记录删除日志的文件路径，这里放在选择的文件夹同级目录下的delete_log.txt
    log_file_path = os.path.join(os.path.dirname(selected_folder), "delete_log.txt")
    total_size_deleted = 0  # 用于统计总共释放的磁盘空间大小，单位为字节
    with open(log_file_path, "w") as log_file:
        for root_dir, dirs, files in os.walk(selected_folder):
            for dir_name in dirs:
                if dir_name == "traceData" or dir_name == "charts":
                    target_folder = os.path.join(root_dir, dir_name)
                    try:
                        # 计算要删除的文件夹及其内部文件的总大小
                        size = get_folder_size(target_folder)
                        total_size_deleted += size
                        # 使用shutil.rmtree来删除文件夹及其内部所有内容
                        shutil.rmtree(target_folder)
                        log_file.write(f"已删除文件夹: {target_folder}，释放空间: {size} 字节\n")
                    except OSError as e:
                        log_file.write(f"删除文件夹 {target_folder} 时出错: {str(e)}\n")

    # 将字节大小转换为更合适的单位（比如KB、MB等）展示
    size_str = convert_size(total_size_deleted)
    print(f"删除操作已完成，日志文件已生成在 {log_file_path}，总共释放磁盘空间: {size_str}")


def get_folder_size(folder_path):
    """
    计算文件夹及其内部所有文件的总大小
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            file_path = os.path.join(dirpath, f)
            total_size += os.path.getsize(file_path)
    return total_size


def convert_size(size_bytes):
    """
    将字节大小转换为合适的单位（KB、MB、GB等）
    """
    units = ["字节", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"


if __name__ == "__main__":
    delete_trace_data_folders()
