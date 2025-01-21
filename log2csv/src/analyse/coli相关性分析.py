import pandas as pd
import matplotlib.pyplot as plt


def main():
    # 文件路径
    # file_path = "C:/Users/test/Desktop/myCode/log2csv/log2csv/all_report_data.xlsx"
    file_path = "C:/Users/test/Desktop/myCode/log2csv/log2csv/beijing demo.xlsx"
    # 读取 Excel 文件
    df = pd.read_excel(file_path)
    # 将字符串列进行编码转换，这里假设简单的映射为数字，实际可根据需要使用更复杂的编码方式
    for column in df.select_dtypes(include=['object']).columns:
        if column != 'coli_become_slow_result':
            df[column] = pd.factorize(df[column])[0]
    # 计算相关性矩阵
    correlation_matrix = df.corr()
    # 提取 'coli_become_slow_result' 列的相关性数据
    coli_correlations = correlation_matrix['coli_become_slow_result']
    # 按相关性绝对值从高到低排序
    sorted_correlations = coli_correlations.abs().sort_values(ascending=False)
    # 打印每一列和 'coli_become_slow_result' 的相关性
    for column in sorted_correlations.index:
        correlation = coli_correlations[column]
        print(f"列 '{column}' 与 'coli_become_slow_result' 的相关性为 {correlation}")
    # 解释相关性
    print("\n相关性解释：")
    print("1. 相关性值接近 1 表示强正线性关系。")
    print("2. 相关性值接近 -1 表示强负线性关系。")
    print("3. 相关性值接近 0 表示几乎无线性关系。")

    # 绘制 'coli_become_slow_result' 和每一个字段的散点图
    for column in df.columns:
        if column != 'coli_become_slow_result':
            plt.figure(figsize=(8, 6))
            plt.scatter(df[column], df['coli_become_slow_result'])
            plt.xlabel(column)
            plt.ylabel('coli_become_slow_result')
            plt.title(f'coli_become_slow_result vs {column}')
            plt.show()


if __name__ == "__main__":
    main()