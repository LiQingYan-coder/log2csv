import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


def main():
    # 文件路径
    # file_path = "C:/Users/test/Desktop/myCode/log2csv/log2csv/all_report_data.xlsx"
    file_path = "../../docs/beijing demo.xlsx"
    # 读取 Excel 文件
    df = pd.read_excel(file_path)
    # 将字符串列进行编码转换，这里假设简单的映射为数字，实际可根据需要使用更复杂的编码方式
    for column in df.select_dtypes(include=['object']).columns:
        if column!= 'coli_become_slow_result':
            df[column] = pd.factorize(df[column])[0]
    # 将 datetime64 类型的列转换为时间戳
    for column in df.select_dtypes(include=['datetime64']).columns:
        df[column] = df[column].astype('int64') // 10**9  # 转换为秒级时间戳
    # 计算相关性矩阵
    correlation_matrix = df.corr()
    # 提取 'coli_become_slow_result' 列的相关性数据
    coli_correlations = correlation_matrix['coli_become_slow_result']
    # 按相关性绝对值从高到低排序
    sorted_correlations = coli_correlations.abs().sort_values(ascending=False)
    # 打印每一列和 'coli_become_slow_result' 的相关性，包括 p 值和 r 值
    for column in sorted_correlations.index:
        if column!= 'coli_become_slow_result':
            correlation, p_value = pearsonr(df[column], df['coli_become_slow_result'])
            print(f"列 '{column}' 与 'coli_become_slow_result' 的相关性系数 r 为 {correlation}, p 值为 {p_value:.6f}")
    # 解释相关性
    print("\n相关性解释：")
    print("1. 相关性值接近 1 表示强正线性关系。")
    print("2. 相关性值接近 -1 表示强负线性关系。")
    print("3. 相关性值接近 0 表示几乎无线性关系。")
    print("4. p 值表示相关性的显著性，通常小于 0.05 认为显著相关。")


if __name__ == "__main__":
    main()