import pandas as pd
import os
# src_csv = '/home/wjh/projects/vid_download/csvs/total_vid.csv'
src_csv = '/home/wjh/projects/vid_download/csvs/final_all.csv'

tgt_dir = '/home/wjh/projects/vid_download/csvs/samples'
tgt_dir = ['/home/wjh/projects/vid_download/csvs/samples/{}'.format(f) for f in os.listdir(tgt_dir)]
not_dld_csv = '/home/wjh/projects/vid_download/csvs/samples_notin_final.csv'

src_df = pd.read_csv(src_csv)
# tgt_df = pd.read_csv(tgt_csv)
tgt_df = pd.concat([pd.read_csv(f) for f in tgt_dir], ignore_index=True)

print('len(src_df):', len(src_df))
print('len(tgt_df):', len(tgt_df))

src_df = src_df[~src_df['id'].isin(tgt_df['id'])]
print('len(src_df):', len(src_df))

# save 
src_df.to_csv(not_dld_csv, index=False)
print('save to:', not_dld_csv)
# 给src_csv添加一列id，值为url中的id,os.path.basename(vid_path).split('.')[0]