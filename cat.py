import pandas as pd
import os

src_csv = '/home/wjh/projects/vid_download/panda70m_training_full.csv'
tgt_csv = '/home/wjh/projects/vid_download/total_0427.csv'
src_df = pd.read_csv(src_csv)
tgt_df = pd.read_csv(tgt_csv)

src_set = set(src_df['url'].tolist())
tgt_set = set(tgt_df['video_url'].tolist())
print(len(src_set), len(tgt_set))

diff_set = src_set - tgt_set
print(len(diff_set))

tgt_diff_set = tgt_set - src_set
print(len(tgt_diff_set))