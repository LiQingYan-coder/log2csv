import csv
import os
import tkinter as tk
import Tool
import csv2pic_mtdTime
from tkinter import filedialog
from Tool_getInfoFromLoaclFile import getInfo_from_suiteJson
from Tool import add_file_link_to_result, log_message

def process_log_file(log_file_path):

    Tool.log2csv(log_file_path)

    dir_path = os.path.dirname(log_file_path)
    csv_path = os.path.join(dir_path, "temp_console_log.csv")
    csv2pic_mtdTime.csv2pic(csv_path)

def collect_data_from_folder(folder_path):
    """遍历文件夹并收集数据."""
    results = []
    already_have_csv_and_pic_dont_need_generate_again = Tool.getGolbalVMFromJson("config.json",
                                                                              "already_have_csv_and_pic_dont_need_generate_again")
    for subdir, dirs, files in os.walk(folder_path):
        if "console.log" in files:
            log_file_path = os.path.join(subdir, "console.log")
            csv_file_path = os.path.join(subdir, "temp_console_log.csv")

            log_message("current solving folder: {}".format(subdir))

            coli_become_slow_result = Tool.judge_coli_slower(csv_file_path)
            if coli_become_slow_result < 0:
                continue

            if not already_have_csv_and_pic_dont_need_generate_again:
                process_log_file(log_file_path)

            result = getInfo_from_suiteJson(subdir)
            # 额外添加字段如下：
            result['Folder'] = subdir
            result['coli_become_slow_result'] = coli_become_slow_result
            result['coli_count'] = Tool.get_coli_count(csv_file_path)

            # 添加console log 的超链接
            result['console.log'] = '=HYPERLINK("' + os.path.join(subdir, "console.log") + '","console log")'
            # 使用封装的函数添加config.xml文件的超链接信息
            result = add_file_link_to_result(result, 'config.xml', os.path.join(subdir, "mje", "testData-beans-original", "beans2"), '.xml', '_Config_')
            # 使用封装的函数添加suite.xml文件的超链接信息
            result = add_file_link_to_result(result, 'suite.xml', os.path.join(subdir, "suitefile"), '.xml', 'Suite')
            # 使用封装的函数添加bar_chart对应的html文件的超链接信息
            result = add_file_link_to_result(result, 'bar_chart', os.path.join(subdir, "csv2pic"), '.html', 'bar_chart')

            results.append(result)
            log_message("finish 1 log analyse, a new line will add to excel")

    return results

def write_results_to_csv(results, output_file_path):
    """将结果写入 CSV 文件."""
    if results:
        fieldnames = set().union(*(d.keys() for d in results))
    else:
        fieldnames = []

    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(results)

def folder2pics():
    root = tk.Tk()
    root.withdraw()

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_file_path = os.path.join(output_dir, 'report_data.csv')

    folder_path = filedialog.askdirectory()
    if folder_path:
        results = collect_data_from_folder(folder_path)
        write_results_to_csv(results, output_file_path)
        print(f"Logs report file has been created at: {output_file_path}")

if __name__ == "__main__":
    folder2pics()
