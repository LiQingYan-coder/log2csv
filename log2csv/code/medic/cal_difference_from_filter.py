import pandas as pd
import os
import datetime


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


def calculate_difference(df, group1_cols, group2_cols):
    if df is None:
        return None
    if not group1_cols or not group2_cols:
        print("未找到相应组别的数据列，请检查列名。")
        return None
    # 计算组 1 和组 2 的平均值
    group1_mean = df[group1_cols].mean(axis=1)
    group2_mean = df[group2_cols].mean(axis=1)
    # 将平均值从指数形式转换为浮点数
    group1_mean = pd.to_numeric(group1_mean, errors='coerce')
    group2_mean = pd.to_numeric(group2_mean, errors='coerce')
    # 计算差值
    difference = (group1_mean - group2_mean).abs()  # 取绝对值
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
    # 处理 NaN 值，可以根据需要修改处理方式
    result_df = result_df.dropna(subset=['Difference'])
    return result_df


def output_to_excel(result_df, output_file, sheet_name):
    if result_df is not None:
        # 检查文件是否存在
        if not os.path.exists(output_file):
            # 如果文件不存在，使用 mode='w' 创建文件
            with pd.ExcelWriter(output_file, engine='openpyxl', mode='w') as writer:
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)
        else:
            # 文件存在，使用 mode='a' 追加数据
            with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
                result_df.to_excel(writer, sheet_name=sheet_name, index=False)


def main(file_path='table.xlsx'):
    df = read_excel(file_path)
    if df is not None:
        # 分别定义不同的组列组合
        group_combinations = [
            (['HC'], ['MDD']),
            (['MDD-F'], ['MDD-M']),
            (['HC-F'], ['MDD-F']),
            (['HC-M'], ['MDD-M']),
            (['HC-M'], ['HC-F'])
        ]
        # 生成带有时间戳的输出文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"metabolite_differences_{timestamp}.xlsx"
        for i, (group1, group2) in enumerate(group_combinations):
            # 根据列名包含的关键字筛选出相应的列
            group1_cols = [col for col in df.columns if group1[0] in col]
            group2_cols = [col for col in df.columns if group2[0] in col]
            result_df = calculate_difference(df, group1_cols, group2_cols)
            # 生成不同的 sheet 名称
            sheet_name = f"{group1[0]}_vs_{group2[0]}_Difference"
            output_to_excel(result_df, output_file, sheet_name)


if __name__ == "__main__":
    main()