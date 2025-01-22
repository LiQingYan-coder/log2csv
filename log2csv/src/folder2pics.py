import csv
import os
import tkinter as tk
import csv2pic_mtdTime
from tkinter import filedialog
from tool.Tool_getInfoFromLoaclFile import getInfo_from_suiteJson
from tool.Tool_general import add_file_link_to_result, log_message, log2csv, getGolbalVMFromJson, judge_coli_slower, get_coli_count

def process_log_file(log_file_path):

    # get config from xml
    need_update_csv = getGolbalVMFromJson("config.json","have_csv_but_need_update")

    # 如果日志目录下已存在默认生成的 temp_console_log.csv ，则不再重复执行
    temp_csv_path = os.path.join(log_file_path, "temp_console_log.csv") # 构建 temp_console_log.csv 的路径
    if os.path.exists(temp_csv_path): # 检测是不是已经存在csv文件
        if need_update_csv: # 需要更新csv
            log2csv(log_file_path)
        else:
            log_message(f"{temp_csv_path} already exists, no need to process again.")
    else:
        log2csv(log_file_path)

    csv_path = os.path.join(os.path.dirname(log_file_path), "temp_console_log.csv")
    # 根据csv画图,生成html
    csv2pic_mtdTime.csv2pic(csv_path)

def collect_data_from_folder(folder_path):
    results = []
    for subdir, dirs, files in os.walk(folder_path):
        if "console.log" in files:
            log_file_path = os.path.join(subdir, "console.log")
            log_message("current solving folder: {}".format(subdir))

            process_log_file(log_file_path)

            csv_file_path = os.path.join(subdir, "temp_console_log.csv")
            coli_become_slow_result = judge_coli_slower(csv_file_path)
            if coli_become_slow_result < 0:
                log_message("coli result < 0, dont generate excel line")
                continue

            result = getInfo_from_suiteJson(subdir)
            # 额外添加字段如下：
            result['Folder'] = subdir
            result['coli_become_slow_result'] = coli_become_slow_result
            result['coli_count'] = get_coli_count(csv_file_path)

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
