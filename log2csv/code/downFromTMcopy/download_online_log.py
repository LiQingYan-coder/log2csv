import os
from datetime import datetime

import requests

def log_message(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{current_time}] {message}")

def process_url(EID, time):
    base_url = "https://ngte-ctrweb.sero.wh.rnd.internal.ericsson.com/ngte/production/NAME/logs/TIME/#/suite"
    # 替换EID
    base_url = base_url.replace("NAME",EID)

    # 创建时间戳命名的文件夹
    folder_path = os.path.join(os.path.expanduser("~/Desktop/logs/seki"), time)
    os.makedirs(folder_path, exist_ok=True)
    url = base_url.replace("TIME", time)

    # 处理下载console.log文件
    new_url = url.replace("/#/suite", "/console.log")
    log_message(f"Downloading {new_url}")
    response = requests.get(new_url)
    output_file_path = os.path.join(folder_path, "console.log")
    with open(output_file_path, "wb") as f:
        f.write(response.content)
    log_message(f"console.log is saved as  {output_file_path}")

    # 确保json子文件夹存在
    json_folder_path = os.path.join(folder_path, "json")
    os.makedirs(json_folder_path, exist_ok=True)
    # 修改URL并下载suite.json文件
    new_url = url.replace("/#/suite", "/json/suite.json")
    log_message(f"Downloading {new_url}")
    response = requests.get(new_url)
    output_file_path = os.path.join(json_folder_path, "suite.json")
    with open(output_file_path, "wb") as f:
        f.write(response.content)
    log_message(f"suite.json is saved as  {output_file_path}")


def testDownloadFromURL(url):
    response = requests.get(url)
    print(response.content)

def extract_timestamps(text_lines):
    """
    从给定的多行文本（以列表形式传入每行内容）中提取每行开头的时间戳，返回时间戳列表
    """
    timestamps = []
    for index, line in enumerate(text_lines, start=1):  # 直接遍历列表中的每行内容
        line = line.strip()  # 去除每行两端的空白字符
        if line:  # 跳过空行
            timestamp = line[:14]  # 提取每行开头的14位字符作为时间戳，可根据实际情况调整长度
            if len(timestamp) == 14 and timestamp.isdigit():  # 验证时间戳是否为14位数字
                timestamps.append(timestamp)

    return timestamps


def read_text_from_file():
    try:
        with open('copyFromTm.txt', 'r', encoding='utf-8') as file:  # 以读取模式打开文件，这里假设文件编码为utf-8，可根据实际情况调整
            text = file.read()
            lines = text.splitlines()  # 将读取到的文本按换行符分割成多行

            return lines
    except FileNotFoundError:
        print("文件temp.txt不存在，请检查文件名和路径是否正确。")
        return []



if __name__ == "__main__":
    testDownloadFromURL("https://ngte-ctrweb.sero.wh.rnd.internal.ericsson.com/ngte/production/eahxnzi/logs/20200827155747/console.log")
    # folder_path = "../seki_name_time_mapping"  # 这里替换为实际的文件夹路径
    #
    # """
    # 读取指定文件夹下所有的txt文件，并分别打印每个文件的内容
    # """
    # # 遍历文件夹下的所有文件和文件夹
    # for root, dirs, files in os.walk(folder_path):
    #     for file in files:
    #         if file.endswith('.txt'):
    #             file_name = os.path.splitext(file)[0]  # 去除后缀获取文件名
    #             file_path = os.path.join(root, file)
    #             try:
    #                 with open(file_path, 'r', encoding='utf-8') as f:
    #                     content = f.read()
    #                     lines = content.splitlines()
    #
    #                     time_list = extract_timestamps(lines)
    #                     for time in time_list:
    #                         process_url(file_name, time)
    #
    #
    #             except Exception as e:
    #                 print(f"读取文件 {file_path} 时出现错误: {e}")




