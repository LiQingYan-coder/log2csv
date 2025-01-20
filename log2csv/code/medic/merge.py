import tkinter as tk
from tkinter import filedialog
import pandas as pd

# 创建Tkinter根窗口（主窗口），但不显示它
root = tk.Tk()
root.withdraw()

# 弹出文件选择对话框，让用户选择Excel文件
excel_file_path = filedialog.askopenfilename(title="选择Excel文件", filetypes=[("Excel文件", "*.xlsx")])
if not excel_file_path:
    print("未选择任何文件，程序结束。")
    exit()

# 读取Excel文件的第一个Sheet作为第一张表
df1 = pd.read_excel(excel_file_path, sheet_name=0)

# 读取Excel文件的第二个Sheet作为第二张表
df2 = pd.read_excel(excel_file_path, sheet_name=1)

# 按照'Metabo_SampleID'这个键进行合并，使用内连接（inner join），你可按需修改连接方式
merged_df = pd.merge(df1, df2, on='Metabo_SampleID')

# 指定输出的CSV文件路径，这里会在当前目录下生成名为'merged_table.csv'的文件，可按需修改
output_csv_path ='merged_table.csv'
merged_df.to_csv(output_csv_path, index=False)

print(f"已成功将两张表合并，并输出为CSV文件：{output_csv_path}")