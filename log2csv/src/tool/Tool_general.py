
from datetime import datetime
import json
import os
import re
import tkinter as tk
from tkinter import filedialog

import pandas as pd

MAX_CONTENT_LENGTH = 1000  # 设置最大内容长度

def log_message(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{current_time}] {message}")
    

def save_to_csv(records, output_file_path):
    log_message("Saving csv file...")
    df = pd.DataFrame(records)
    df.to_csv(output_file_path, index=False, encoding='utf-8')
    log_message("Save csv done")


def save_paths_to_json(log_file_path, output_file_path):
    file_paths = {
        "input_log_file": log_file_path,
        "output_csv_file": output_file_path
    }
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(current_directory, '../../', 'config')
    json_file_path = os.path.join(config_dir, "temp.json")

    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(file_paths, json_file, ensure_ascii=False, indent=4)

    # log_message(f"temp.json saved to {json_file_path}")

def select_file(dialog_function, title, filetypes, defaultextension=None):
    root = tk.Tk()
    root.withdraw()
    file_path = dialog_function(
        title=title,
        defaultextension=defaultextension,
        filetypes=filetypes
    )
    return file_path

def select_log_file():
    return select_file(filedialog.askopenfilename, 'select .log from ...', [("Log files", "*.log"), ("All files", "*.*")])

def clean_content(content):
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', content)

# timestamp format define
def detect_timestamp_format(file_path):
    timestamp_patterns = {
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}": "%Y-%m-%d %H:%M:%S,%f",
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2},\d{3}": "%Y-%m-%dT%H:%M:%S,%f",
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{6}": "%Y-%m-%d %H:%M:%S,%f", # @tianyang wang need this format
        r"\d{2}:\d{2}:\d{2}\.\d{3}": "%H:%M:%S.%f"
    }
    with open(file_path, 'r', encoding='latin-1') as file:
        for line in file:
            for pattern, fmt in timestamp_patterns.items():
                if re.search(pattern, line):
                    return pattern, fmt
    return None, None


def parse_log_line(line, pattern, timestamp_format, last_content):
    match = re.search(pattern, line)
    if match:
        timestamp_str = match.group(0)
        current_timestamp = datetime.strptime(timestamp_str, timestamp_format)
        return current_timestamp, line[len(timestamp_str):].strip(), last_content
    else:
        new_content = last_content + " " + line
        if len(new_content) > MAX_CONTENT_LENGTH:
            new_content = new_content[:MAX_CONTENT_LENGTH]  # 截断到最大长度
        return None, None, new_content

def process_log_and_saveCSV(log_file_path):
    pattern, timestamp_format = detect_timestamp_format(log_file_path)
    if not pattern:
        log_message("No recognized timestamp format found.")
        return []

    last_timestamp = None
    last_content = ""
    records = []

    with open(log_file_path, 'r', encoding='latin-1') as file:
        log_message("Parsing, please wait...")

        for currentLineIndex, line in enumerate(file, start=1):
            if currentLineIndex % 50000 == 0:
                log_message(f"Parsing ... current line is: {currentLineIndex}")

            line = line.strip()
            current_timestamp, current_content, last_content = parse_log_line(line, pattern, timestamp_format, last_content)
            
            if current_timestamp:
                if last_timestamp:
                    time_diff = (current_timestamp - last_timestamp).total_seconds()
                    records.append({
                        "Timestamp": last_timestamp.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3], # this format used in csv output file.
                        "Time Difference (s)": time_diff,
                        "Content": clean_content(last_content)
                    })
                last_timestamp = current_timestamp
                last_content = current_content

        log_message("Parse done")
    return records


# 读取config文件夹中json获取全局变量
def getGolbalVMFromJson(fileName, jsonElement):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, '../../', 'config')
    config_path = os.path.join(config_dir, fileName)
    with open(config_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    return config.get(jsonElement, True)


def log2csv(log_file_path):
    log_message("Input log file: " + log_file_path)
     # 加载外部VM参数
    manual_output_selection = getGolbalVMFromJson("config.json", "manual_output_selection")

    if not log_file_path:
        log_message("No log file selected.")
        return

    records = process_log_and_saveCSV(log_file_path)

    if manual_output_selection:
        output_file_path = select_file(filedialog.asksaveasfilename, 'save .csv to ...', [("Excel files", "*.csv"), ("All files", "*.*")], ".csv")
        if not output_file_path:
            log_message("No output file selected.")
            return
    else:
        # Use a default temporary file path
        output_file_path = os.path.join(os.path.dirname(log_file_path), "temp_console_log.csv")
        log_message(f"manual_select is false in config.json. Using default path: {output_file_path}")

    save_to_csv(records, output_file_path)
    save_paths_to_json(log_file_path, output_file_path)
    log_message(f"log2csv complete. csv saved to {output_file_path}")


# 在生成coli时耗柱状图，鼠标悬停在某个柱的时候，会显示该条柱状图对应log行的详细内容，但是太长不容易看，所以限制一个最大长度，也许未来能做成滚轮，但是我懒
def make_text_selectable(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # 插入 CSS 样式
    style = '''
    <style>
    .plotly .xtick > text, .plotly .ytick > text, .plotly .hoverlayer > text {
        user-select: text;
    }
    </style>
    '''
    content = content.replace('</head>', style + '</head>')

    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(content)


## 判断coli时延相比于正常，总计慢了多少，最后输出csv表格的时候，会用到这个方法。
def howMuch_coli_slower(csv_path):
    df = pd.read_csv(csv_path)
    # 筛选出Content列包含'onfig'的数据行
    filtered_df = df[df['Content'].str.contains('onfigP', case=False)]

    # 进一步筛选Time Difference (s)列处于[0.02, 3]区间的数据
    valid_df = filtered_df[(filtered_df['Time Difference (s)'] >= 0.02) & (filtered_df['Time Difference (s)'] <= 3)]
    normal_mean = valid_df['Time Difference (s)'].iloc[:40].mean()

    # 从第41个点开始，统计到最后一个点，计算与平均值的差值并累加
    extra_or_less_time_sum = (valid_df['Time Difference (s)'].iloc[40:] - normal_mean).sum()
    return round(extra_or_less_time_sum, 3)

def get_coli_count(csv_path):
    df = pd.read_csv(csv_path)
    # 筛选出Content列包含'onfig'的数据行
    filtered_df = df[df['Content'].str.contains('onfigP', case=False)]
    return len(filtered_df)

## 自动判断coli时延是否逐渐变长，最后输出csv表格的时候，会用到这个方法。
def judge_coli_slower(csv_path):
    try:
        df = pd.read_csv(csv_path)
        # 筛选出Content列包含'onfig'的数据行
        filtered_df = df[df['Content'].str.contains('onfigP', case=False)]
        # 进一步筛选Time Difference (s)列处于[0.02, 3]区间的数据
        valid_df = filtered_df[(filtered_df['Time Difference (s)'] >= 0.02) & (filtered_df['Time Difference (s)'] <= 3)]
        if len(valid_df) < 80:
            log_message(f"filtered data size <80, dont count")
            return -1
        # 从前向后取 X 个符合条件的值并计算平均值，中位数
        normal_mean = valid_df['Time Difference (s)'].iloc[:40].mean()
        normal_Median = valid_df['Time Difference (s)'].iloc[:40].median()

        # 从后向前取 X 个符合条件的值并计算平均值，中位数
        final_mean = valid_df['Time Difference (s)'].iloc[-40:].mean()
        final_median = valid_df['Time Difference (s)'].iloc[-40:].median()

        if final_mean >= normal_mean * 3 or final_median >= normal_Median * 1.3:
            return 1  # coli存在变慢 标记个1
        if normal_mean >= 1:
            return 2 # 一开始coli就慢，标记个2
        if normal_mean * 1.8 > final_mean >= normal_mean * 1.6:
            return 0.7
        if normal_mean * 1.6 > final_mean >= normal_mean * 1.4:
            return 0.3
        return 0

    except FileNotFoundError:
        # 捕获文件不存在的异常
        # 可能原因：传入的文件路径不正确，比如路径拼写错误、文件被误删除或者不在指定的查找路径范围内等情况。
        log_message(f"file: {csv_path} dont exist")
        return -2
    except pd.errors.ParserError:
        # 捕获数据解析错误异常（pandas库中特定的解析相关错误）
        # 可能原因：CSV文件的格式不符合预期，例如分隔符使用错误、列数不一致、数据类型不匹配等情况，导致pandas无法正确解析文件内容。
        log_message(f"analyse {csv_path} error, check the format")
        return -3
    except ValueError:
        # 捕获值相关的错误异常
        # 可能原因：在代码中对数据进行类型转换（如将字符串转换为数值类型等操作）时出现问题，例如文件中Time Difference (s)列的数据存在无法转换为浮点数的非数字字符等情况。
        log_message(f"value convert error")
        return -4
    except KeyError:
        # 捕获键不存在的异常
        # 可能原因：代码中使用的列名（如'Content'、'Time Difference (s)'等）在CSV文件中不存在，可能是文件结构发生变化或者列名拼写错误等情况导致。
        log_message(f"{csv_path} dont have wanted columns name")
        return -5
    except Exception as e:
        # 捕获其他未明确的通用异常
        # 可能原因：包括但不限于内存不足、系统权限问题、程序运行时的其他未知错误等情况，这些情况较难提前准确预估，但通过捕获通用异常可以避免程序因未处理的异常而崩溃。
        log_message(f"solving {csv_path} occur other error: {e}")
        return -6
    

def add_file_link_to_result(result, key, target_folder, file_extension, file_keyword):
    """
    查找指定文件夹下符合条件的文件，并将其路径以超链接格式添加到result字典中。

    :param result: 目标字典
    :param key: 要添加到字典中的键
    :param target_folder: 查找文件的目标文件夹路径
    :param file_extension: 文件的扩展名，如 '.xml'、'.html' 等
    :param file_keyword: 文件名中需要包含的关键字
    """
    if not os.path.exists(target_folder):
        log_message(f"Warning!!! {target_folder} dont exit,  {key} in csv link will be null")
        # 使用None表示未找到文件，后续可以根据这个值来进行更灵活地处理，而不是硬编码一个默认路径
        result[key] = None
        return result

    file_path = None
    for file in os.listdir(target_folder):
        if file.endswith(file_extension) and file_keyword in file:
            file_path = os.path.join(target_folder, file)
            break

    if file_path is None:
        log_message(f"Warning!!! In {target_folder} dont find {key} file")
    else:
        result[key] = '=HYPERLINK("' + file_path + '", "' + file_keyword + '")'
    return result