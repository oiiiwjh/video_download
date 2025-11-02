'''
Author: jeremiah.wang
Date: 2025-02-18 18:48:23
LastEditTime: 2025-02-21 23:31:19
Description: 计算时长and plot
'''
import pandas as pd
import matplotlib.pyplot as plt

def calculate_hours(duration):
    parts = duration.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        total_hours = hours + minutes / 60 + seconds / 3600
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        total_hours = minutes / 60 + seconds / 3600
    else:
        total_hours = 0
    return total_hours

def calculate_hours_min_thres(df, thres):
    df_hrs = df[df['hours'] > thres]
    total_rows_hrs = len(df_hrs)
    total_hours_hrs = df_hrs['hours'].sum()
    avg_hours_hrs = total_hours_hrs / total_rows_hrs
    _percent = (total_rows_hrs / len(df)) * 100
    print(f"Total vids > {thres} hour: nums[{total_rows_hrs}], percent: [{_percent}], total hours: [{total_hours_hrs}], Average hours: [{avg_hours_hrs}]")

def calculate_hours_max_thres(df, thres):
    df_hrs = df[df['hours'] <= thres]
    total_rows_hrs = len(df_hrs)
    total_hours_hrs = df_hrs['hours'].sum()
    avg_hours_hrs = total_hours_hrs / total_rows_hrs
    _percent = (total_rows_hrs / len(df)) * 100
    print(f"Total vids <= {thres} hour: nums[{total_rows_hrs}], percent: [{_percent}], total hours: [{total_hours_hrs}], Average hours: [{avg_hours_hrs}]")

def process_csv(input_path, output_path, hist_path):
    # 读取主CSV文件
    df = pd.read_csv(input_path)
    
    # 添加一列表示小时数
    df['hours'] = df['duration'].apply(calculate_hours)
    
    # 输出：总行数，总小时数，平均小时数
    total_rows = len(df)
    total_hours = df['hours'].sum()
    avg_hours = total_hours / total_rows
    print(f"Total vids: {total_rows}, Total hours: {total_hours}, Average hours: {avg_hours}")
    
    # # 输出小于等于1小时的视频总行数，总小时数，平均小时数
    # calculate_hours_max_thres(df,1)
    # # 输出大于1小时的视频总行数，总小时数，平均小时数
    # calculate_hours_min_thres(df,1)
    # # 输出大于4小时的视频总行数，总小时数，平均小时数
    # calculate_hours_min_thres(df,4)
    # # 输出大于8小时的视频总行数，总小时数，平均小时数
    # calculate_hours_min_thres(df,8)
    
    calculate_hours_min_thres(df, 12)
    # 保存修改后的CSV文件
    df.to_csv(output_path, index=False)
    
    # 按照hours来统计直方图，间隔为1小时
    fig, ax1 = plt.subplots()

    # 左侧纵坐标：视频数量
    ax1.hist(df['hours'], bins=range(0, int(df['hours'].max()) + 1, 1), edgecolor='black', color='green')
    ax1.set_xlabel('Hours')
    ax1.set_ylabel('Vid_nums', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # 右侧纵坐标：百分比
    ax2 = ax1.twinx()
    ax2.set_ylabel('Percentage', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.set_ylim(0, 100)
    total_vids = len(df)
    counts, bins, patches = ax1.hist(df['hours'], bins=range(0, int(df['hours'].max()) + 1, 1))# , edgecolor='black')
    percentages = (counts / total_vids) * 100
    ax2.plot(bins[:-1], percentages, 'r--')

    # 保存直方图
    fig.savefig(hist_path)
    print(f"Histogram saved to {hist_path}")

if __name__ == "__main__":
    # input_path = 'csvs/patch1.csv'
    # output_path = 'csvs/patch1_with_hours.csv'
    input_path = 'meta_info_0221.csv'
    output_path = 'meta_info_0221_with_hours.csv'
    hist_path = 'hist.png'
    
    process_csv(input_path, output_path, hist_path)