'''
Author: jeremiah.wang
Date: 2024-11-27 22:03:10
LastEditTime: 2025-02-25 22:28:19
Description: 从一个csv文件中随机采样一定数量的行，保存到另一个csv文件中。此外可以添加一些筛选条件 如：视频长度不能大于1小时。
'''
import pandas as pd
import numpy as np
import re
import os

def check_hrs(row):
    """Check if the duration of the video is in an hour."""
    hrs_tag = len(row['duration'].split(':')) == 3
    hrs = 0
    if hrs_tag:
        hrs = int(row['duration'].split(':')[0])
    if hrs > 0:
        # print(row['duration'].split(':'))
        return True # if hrs > 0, return True for delete
    return False # if hrs == 0, return False for keep

def row_filters(row): # return True if you dont want it
    # return re.search('[\u4e00-\u9fff]', text) is not None
    return check_hrs(row)

def sample_csv(file_path, except_paths, total_nums, output_path, filter_opts=False, debug=False):
    # Read the main CSV file
    df = pd.read_csv(file_path)
    total_rows = len(df)
    print(f'Total rows in main file: {total_rows}')
    
    # Read and concatenate all CSV files in except_paths
    if len(except_paths) == 0:
        except_df = pd.DataFrame(columns=df.columns)
        print("No except paths provided.")
    else:
        except_dfs = [pd.read_csv(path) for path in except_paths]
        except_df = pd.concat(except_dfs, ignore_index=True)
    # Filter out rows that are in the except_df
    filtered_df = df.merge(except_df, how='left', indicator=True).query('_merge == "left_only"').drop('_merge', axis=1)
    
    # Filter out rows that contain Chinese characters
    if filter_opts:
        filtered_df = filtered_df[~filtered_df.apply(row_filters,axis=1)]
        # filtered_df = filtered_df[~filtered_df.apply(lambda row: row.map(row_filters)).any(axis=1)] # before for chinense check
    else:
        print("No filter for Chinese characters.")
    filtered_total_rows = len(filtered_df)
    print(f'Total rows after filtering: {filtered_total_rows}, chinese & exists')
    
    # If no rows are left after filtering, raise an error or handle accordingly
    if filtered_df.empty:
        raise ValueError("No rows left after filtering out entries with Chinese characters and except paths.")
    # If filter_df length < total_nums, save filter_df to a csv file, the output_path=f'meta_data_sample_{len(filtered_df)}.csv'
    if len(filtered_df) < total_nums:
        filtered_df.to_csv(f'meta_data_sample_{len(filtered_df)}.csv', index=False)
        return
    # Sample from the filtered DataFrame
    sample_indices = np.random.choice(len(filtered_df), min(total_nums, len(filtered_df)), replace=False)
    sampled_df = filtered_df.iloc[sample_indices]
    if not debug:
        # print(f'Sampled rows: {len(sampled_df)}')
        sampled_df.to_csv(output_path, index=False)
        return True
    return False

# file_path = input("输入csv文件地址: ")
# total_nums = int(input("输入采样行数: "))
# output_path = input("输入保存csv文件地址: ")
if __name__ == "__main__":
    # ================================ customized parameters =========================================
    file_path = 'meta_info_0225.csv'
    total_nums = 3000
    filter_opts = False # True: 按照某些条件过滤数据，False: 不过滤数据
    debug = False # True: 不保存采样数据，False: 保存采样数据
    output_path = file_path.replace('.csv', f'_sample_{total_nums}.csv')
    
    except_paths = [
        'meta_info_0225_sample_1000_1.csv',
        'meta_info_0225_sample_1000.csv',
    ]
    # ================================================================================================
    # f'meta_data_sample_{total_nums}.csv'
    counter = 1
    while os.path.exists(output_path):
        print(f'File {output_path} already exists. Trying next name...')
        except_paths.append(output_path)
        output_path = file_path.replace('.csv', f'_sample_{total_nums}_{counter}.csv')
        counter += 1

    except_paths = [path for path in except_paths if os.path.isfile(path)]

    saved = sample_csv(
        file_path=file_path, 
        except_paths=except_paths, 
        total_nums=total_nums, 
        output_path=output_path, 
        filter_opts=filter_opts, debug=debug
    )
    if saved:
        print(f"Except paths: [{except_paths}]")
        print(f"Saved sampled CSV file to {output_path}")
            