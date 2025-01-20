import Tool

if __name__ == "__main__":
    log_file_path = Tool.select_log_file() # 从UI中选取log文件
    Tool.log2csv(log_file_path) # 处理该log文件