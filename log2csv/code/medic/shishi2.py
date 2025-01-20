import pandas as pd
from scipy.stats import ttest_ind, mannwhitneyu


def read_excel(file_path):
    # 读取 Excel 文件
    df = pd.read_excel(file_path)
    return df


def t_test(df):
    # 分离出正常人和患者的列
    normal_cols = [col for col in df.columns if 'HC' in col]
    patient_cols = [col for col in df.columns if 'MDD' in col]
    # 提取数据
    normal_data = df[normal_cols].values.flatten()
    patient_data = df[patient_cols].values.flatten()
    # 执行 t 检验
    t_stat, p_value = ttest_ind(normal_data, patient_data)
    return t_stat, p_value


def mann_whitney_u_test(df):
    # 分离出正常人和患者的列
    normal_cols = [col for col in df.columns if 'HC' in col]
    patient_cols = [col for col in df.columns if 'MDD' in col]
    # 提取数据
    normal_data = df[normal_cols].values.flatten()
    patient_data = df[patient_cols].values.flatten()
    # 执行 Mann-Whitney U 检验
    u_stat, p_value = mannwhitneyu(normal_data, patient_data)
    return u_stat, p_value


def main():
    # 请将此处的文件路径替换为你的 Excel 文件的实际路径
    file_path = 'table.xlsx'
    df = read_excel(file_path)
    # 执行 t 检验
    t_stat, t_p_value = t_test(df)
    print(f"T 检验统计量: {t_stat}, p 值: {t_p_value}")
    # 执行 Mann-Whitney U 检验
    u_stat, u_p_value = mann_whitney_u_test(df)
    print(f"Mann-Whitney U 检验统计量: {u_stat}, p 值: {u_p_value}")


if __name__ == "__main__":
    main()