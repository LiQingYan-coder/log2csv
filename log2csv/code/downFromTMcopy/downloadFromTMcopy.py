import importlib
import sys
import subprocess
import re
import os
from datetime import datetime

import requests
import urllib3
from tabulate import tabulate
import tkinter as tk
from tkinter import filedialog


def log_message(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{current_time}] {message}")

def check_and_install_package(package_name):
    try:
        importlib.import_module(package_name)
        log_message(f"{package_name} 已安装")
    except ImportError:
        log_message(f"{package_name} 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        log_message(f"{package_name} 已安装完成")


def process_url(url, output_base_folder):
    # 使用正则表达式提取 14 位时间戳
    timestamp = re.search(r"\d{14}", url)
    if timestamp:
        timestamp = timestamp.group()
        # 组合新文件夹
        output_folder_of_this_log = os.path.join(output_base_folder, timestamp)
        # 确保新文件夹存在
        os.makedirs(output_folder_of_this_log, exist_ok=True)
    else:
        log_message("Warning！ Input url dont find 14 timestamp.")
        return

    # 处理下载 console.log 文件
    new_url = url.replace("/#/suite", "/console.log")
    log_message(f"Downloading {new_url}")
    try:
        # 暂时关闭 SSL 证书验证，仅用于开发或测试环境
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(new_url, verify=False)
    except requests.exceptions.SSLError as e:
        log_message(f"SSL 错误: {e}")
        return
    consolelog_output_path = os.path.join(output_folder_of_this_log, "console.log")
    with open(consolelog_output_path, "wb") as f:
        f.write(response.content)
    log_message(f"console.log is saved as  {consolelog_output_path}")


    # 确保 json 子文件夹存在
    json_output_path = os.path.join(output_folder_of_this_log, "json")
    os.makedirs(json_output_path, exist_ok=True)

    # 修改 URL 并下载 suite.json 文件
    new_url = url.replace("/#/suite", "/json/suite.json")
    log_message(f"Downloading {new_url}")
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(new_url, verify=False)
    except requests.exceptions.SSLError as e:
        return
    output_file_path = os.path.join(json_output_path, "suite.json")
    with open(output_file_path, "wb") as f:
        f.write(response.content)
    log_message(f"suite.json is saved as  {output_file_path}")


def read_mapping_file(mapping_file):
    mapping_dict = {}
    with open(mapping_file, 'r', encoding='utf-8') as mapfile:
        for line in mapfile:
            parts = line.strip().split()
            if len(parts) == 2:
                mapping_dict[parts[0]] = parts[1]
    return mapping_dict


def process_input_file(input_file):
    formatted_lines = []
    temp_line = ""
    with open(input_file, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            if temp_line:
                temp_line += "," + stripped_line
            else:
                temp_line = stripped_line
        else:
            if temp_line:
                formatted_lines.append(temp_line)
                temp_line = ""
    if temp_line:
        formatted_lines.append(temp_line)
    final_text = "\n".join(formatted_lines).strip()
    final_text = final_text.replace('\t', ',')
    processed_lines = [",".join([elem.strip() for elem in line.split(",")]) for line in final_text.split("\n")]
    return processed_lines


def extract_info_and_replace_url(processed_lines, mapping_dict):
    timestamp_list = []
    eid_list = []
    site_name_list = []
    url_list = []
    final_url_list = []
    for line in processed_lines:
        elements = line.split(',')
        timestamp = elements[0]
        eid = elements[3]
        site_name = elements[5]
        timestamp_list.append(timestamp)
        eid_list.append(eid)
        site_name_list.append(site_name)
        if site_name in mapping_dict:
            url = mapping_dict[site_name]
            url = url.replace("TIME", timestamp).replace("EID", eid)
            final_url_list.append(url)
            url_list.append(url)
        else:
            url_list.append("N/A")
            final_url_list.append("N/A")
    return timestamp_list, eid_list, site_name_list, url_list, final_url_list


def generate_table(processed_lines, table_output_file):
    table_data = []
    for line in processed_lines:
        table_data.append(line.split(','))
    table_text = tabulate(table_data, tablefmt="grid")
    with open(table_output_file, 'w', encoding='utf-8') as table_outfile:
        table_outfile.write(table_text)


def format_text(input_file, output_file, table_output_file, mapping_file):
    mapping_dict = read_mapping_file(mapping_file)
    processed_lines = process_input_file(input_file)
    timestamp_list, eid_list, site_name_list, url_list, final_url_list = extract_info_and_replace_url(processed_lines, mapping_dict)
    generate_table(processed_lines, table_output_file)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        final_text = "\n".join(processed_lines)
        outfile.write(final_text)
    return timestamp_list, eid_list, site_name_list, url_list, final_url_list


def main():
    # 检查所需包是否安装
    packages_to_check = ['re', 'os', 'requests', 'urllib3', 'tabulate', 'tkinter']
    for package in packages_to_check:
        check_and_install_package(package)

    root = tk.Tk()
    root.withdraw()
    output_base_folder = filedialog.askdirectory(title="请选择输出的文件夹根目录位置")
    if not output_base_folder:
        log_message("未选择文件夹，程序退出")
        return
    input_file = 'copyFromTm.txt'
    output_file = 'output.txt'
    table_output_file = 'table_output.txt'
    mapping_file = 'site_serverIP_mapping.txt'
    timestamp_list, eid_list, site_name_list, url_list, final_url_list = format_text(input_file, output_file, table_output_file, mapping_file)
    for url in final_url_list:
        if url!= "N/A":
            process_url(url, output_base_folder)


if __name__ == "__main__":
    main()