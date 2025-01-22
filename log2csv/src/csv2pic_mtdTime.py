import webbrowser

import pandas as pd
import plotly.express as px
import os
import plotly.io as pio

from tool.Tool_general import log_message, getGolbalVMFromJson

# mtd指令数量小于此数，则不生成bar图
minDataSize = 20

def read_and_filter_csv(file_path, filter_keyword):
    """读取CSV文件并过滤包含特定关键词的行"""
    try:
        # 针对文件不存在的情况单独处理
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定的文件 {file_path} 不存在")
        df = pd.read_csv(file_path)
    except FileNotFoundError as e:
        log_message(f"ERROR: {e}")
        return None
    except pd.errors.ParserError as e:
        log_message(f"ERROR: {e}")
        return None
    except Exception as e:
        print(f"其他未知错误: {e}")
        return None

    # 只有当读取文件成功，df有值了，才进行后续操作
    if df is not None:
        # 检查读取的数据中是否包含'Content'列，若不存在则抛出异常
        if 'Content' not in df.columns:
            raise KeyError("读取的CSV文件中不存在'Content'列")

        result_df = df[df['Content'].str.contains(filter_keyword, na=False)]
        return result_df
    return None


def create_bar_chart(df, x_col, y_col, title):
    """创建柱状图"""
    fig = px.bar(df, x=x_col, y=y_col, title=title, hover_data={'Content': True})
    fig.update_layout(
        xaxis=dict(tickmode='auto', nticks=20),
        yaxis=dict(range=[0, 4]),
        xaxis_title=x_col,
        yaxis_title=y_col,
        title=dict(text=f'{title}<br>', x=0.0, xanchor='left')
    )
    return fig

def truncate_content(content, max_length=1000):
    """截断内容字符串，如果超过指定长度则添加省略号"""
    return content[:max_length] + '...' if len(content) > max_length else content

def csv2pic(csv_path):
    """主流程：从 JSON 获取 CSV，处理数据，生成图表并保存"""

    # csv_file_path = getGolbalVMFromJson("temp.json", "output_csv_file")
    csv_file_path = csv_path
    log_message("Input CSV file ：" + csv_file_path)
    
    if not csv_file_path or not os.path.exists(csv_file_path):
        log_message("Error: CSV file path not found or does not exist.")
        return

    filter_keyword = 'onfigp'
    filtered_df = read_and_filter_csv(csv_file_path, filter_keyword)
    if filtered_df is None:
        log_message("After filtering [" + filter_keyword + "] in CSV, data is none, dont generate bar chart")
        return
    if len(filtered_df) < minDataSize:
        log_message("After filtering [" + filter_keyword + "] in CSV, data is less than " + str(minDataSize) + ", dont generate bar chart")
        return

    filtered_df['Content'] = filtered_df['Content'].apply(lambda x: truncate_content(x, 180))
    subset_df = filtered_df[['Timestamp', 'Time Difference (s)', 'Content']]
    fig = create_bar_chart(subset_df, 'Timestamp', 'Time Difference (s)', f'包含 \"{filter_keyword}\" 的每条 log 的时耗')

    output_dir = os.path.join(os.path.dirname(csv_file_path), 'csv2pic')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'bar_chart.html')

    # 自定义 HTML 内容，添加 CSV 来源信息
    html_content = f"""
    <html>
    <head><title>Bar Chart</title></head>
    <body>
    <p>CSV Source: <code>{csv_file_path}</code></p>
    <p>Generated file is located at: <code>{os.path.abspath(output_dir)}</code></p>
    {pio.to_html(fig, full_html=True)}
    </body>
    </html>
    """

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    log_message(f"Bar chart saved to {output_file}")

    auto_open_pic_as_html = getGolbalVMFromJson("config.json", "auto_open_pic_as_html")
    if auto_open_pic_as_html:
        log_message("try to open chart in browser...")
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
        log_message("open success")