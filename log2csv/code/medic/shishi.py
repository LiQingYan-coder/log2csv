import pandas as pd


def read_excel(file_path):
    # 读取 Excel 文件
    df = pd.read_excel(file_path)
    return df


def calculate_difference(df):
    # 分离出正常人和患者的列
    normal_cols = [col for col in df.columns if 'HC' in col]
    patient_cols = [col for col in df.columns if 'MDD' in col]
    # 计算正常人和患者的平均值
    normal_mean = df[normal_cols].mean(axis=1)
    patient_mean = df[patient_cols].mean(axis=1)
    # 计算差值
    difference = normal_mean - patient_mean
    # 获取代谢产物名称，假设代谢产物名称在第一列
    metabolite_names = df.iloc[:, 0]
    # 创建一个新的 DataFrame 存储结果
    result_df = pd.DataFrame({
        'Metabolite Name': metabolite_names,
        'Difference': difference.abs()  # 取绝对值
    })
    # 按差异大小排序
    result_df = result_df.sort_values(by='Difference', ascending=False)
    return result_df


def output_to_excel(result_df, output_file):
    # 将结果输出到 Excel 文件
    result_df.to_excel(output_file, index=False)


def main():
    # 请将此处的文件路径替换为你的 Excel 文件的实际路径
    file_path = 'table.xlsx'
    # 请将此处的输出文件路径替换为你想要保存结果的实际路径
    output_file = 'output.xlsx'
    df = read_excel(file_path)
    result_df = calculate_difference(df)
    output_to_excel(result_df, output_file)


if __name__ == "__main__":
    main()