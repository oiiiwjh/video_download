import os
import pandas as pd
# check total hours
# path = '/home/wjh/projects/vid_download/meta_infos/meta_info_0324.csv'
# df = pd.read_csv(path)
# # cal total hours, using hours column
# total_hours = 0
# for index, row in df.iterrows():
#     if row['hours'] != '0':
#         total_hours += float(row['hours'])
# print(f'total hours: {total_hours}')
# -------------------------------------------------------------
# check file temp

# import pandas as pd

# txt_path = '/home/wjh/projects/vid_download/meta_infos/z0322_dld_othererr.log'
# src_csv_path = '/home/wjh/projects/vid_download/meta_infos/meta_info_0331.csv'
# tgt_csv_path = '/home/wjh/projects/vid_download/meta_infos/meta_info_0331.csv'
# no_tgt_csv_path = '/home/wjh/projects/vid_download/meta_infos/meta_info_0331_no.csv'

# with open(txt_path, 'r') as f:
#     lines = f.readlines()
# lines = [line.strip().split('=')[-1] for line in lines]
# src_pd = pd.read_csv(src_csv_path)
# print('src_pd', len(src_pd))
# # check if lines in src_pd['video_url']
# # src_pd['id'] = src_pd['video_url'].apply(lambda x: os.path.basename(x).split('=')[-1])
# no_tgt = src_pd[src_pd['id'].isin(lines)]
# print('no_tgt', len(no_tgt))
# no_tgt.to_csv(no_tgt_csv_path, index=False)

# tgt_pd = src_pd[~src_pd['id'].isin(lines)]
# print('tgt_pd', len(tgt_pd))
# tgt_pd.to_csv(tgt_csv_path, index=False)

import pandas as pd
import os
# pth = '/home/wjh/projects/vid_download/meta_infos/meta_info_0410_done.csv'
# df = pd.read_csv(pth)
# # 分成多个子文件，每个csv文件包含150条数据
# num_rows = len(df)
# num_files = num_rows // 150 + (num_rows % 150 > 0)
# print(f'num_rows: {num_rows}, num_files: {num_files}')
# for i in range(num_files):
#     start_row = i * 150
#     end_row = min((i + 1) * 150, num_rows)
#     df.iloc[start_row:end_row].to_csv(f'/home/wjh/projects/vid_download/meta_infos/total_done_sample_supp_{i+9}.csv', index=False)
dt = pd.read_csv('/share/wjh/panda70m/dataset/total.csv')
print(len(dt))