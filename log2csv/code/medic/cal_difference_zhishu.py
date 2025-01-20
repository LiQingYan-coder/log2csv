import pandas as pd


def read_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到，请检查文件路径是否正确。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def calculate_difference(df):
    if df is None:
        return None
    # 分离出正常人和患者的列
    normal_cols = [col for col in df.columns if 'HC' in col]
    patient_cols = [col for col in df.columns if 'MDD' in col]
    if not normal_cols or not patient_cols:
        print("未找到正常人和患者的数据列，请检查列名。")
        return None
    # 计算正常人和患者的平均值
    normal_mean = df[normal_cols].mean(axis=1)
    patient_mean = df[patient_cols].mean(axis=1)
    # 将平均值从指数形式转换为浮点数
    normal_mean = pd.to_numeric(normal_mean, errors='coerce')
    patient_mean = pd.to_numeric(patient_mean, errors='coerce')
    # 计算差值
    difference = (normal_mean - patient_mean).abs()  # 取绝对值
    # 获取代谢产物名称，假设代谢产物名称在第一列
    metabolite_names = df.iloc[:, 0]
    # 创建一个新的 DataFrame 存储结果
    result_df = pd.DataFrame({
        'Metabolite Name': metabolite_names,
        'Difference': difference
    })
    # 按差异大小排序
    result_df = result_df.sort_values(by='Difference', ascending=False)
    # 对 Difference 列保留两位小数
    result_df['Difference'] = result_df['Difference'].round(2)
    return result_df


def output_to_excel(result_df, output_file):
    if result_df is not None:
        # 将结果输出到 Excel 文件
        result_df.to_excel(output_file, index=False)


def main(file_path='table.xlsx', output_file='output.xlsx'):
    df = read_excel(file_path)
    result_df = calculate_difference(df)
    output_to_excel(result_df, output_file)


if __name__ == "__main__":
    main()