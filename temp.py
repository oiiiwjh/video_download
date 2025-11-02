# import pandas as pd
# import os
# path1 = '/home/wjh/projects/vid_download/meta_infos/meta_info_0401.csv'
# path2 = '/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_7.csv'
# path3 = '/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_8.csv'
# df1 = pd.read_csv(path1)
# df2 = pd.read_csv(path2)
# df3 = pd.read_csv(path3)
# print(len(df1), len(df2))

# # nt_df = df2[~df2['video_url'].isin(df1['video_url'])]
# ids_1 = (df1['id'].tolist())
# ids_2 = (df2['id'].tolist())
# ids_3 = (df3['id'].tolist())

# print(len(ids_1), len(ids_2), len(ids_3))
# ids_2 = list(set(ids_2) - set(ids_1))
# ids_3 = list(set(ids_3) - set(ids_1))
# print(len(ids_2), len(ids_3))
# # df1 = df1[df1['id'].isin(ids_2)]
# print(len(df1))
# df2 = df2[df2['id'].isin(ids_2)]
# print(len(df2))
# # df2.to_csv('/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_7.csv', index=False)
# # df1 = df1[df1['id'].isin(df3['id'])]
# # print(len(df1))

# # df1.to_csv('/home/wjh/projects/vid_download/meta_infos/meta_info_0331.csv', index=False)
import os
import pandas as pd
import shutil

# csv_path = '/home/wjh/projects/vid_download/meta_infos/succ.csv'
# df = pd.read_csv(csv_path)
# tgt_dir = '/share/wjh/raw_videos/total_done_sample_apd_1'
# for i in range(len(df)):
#     path_src = df.iloc[i]['video_path']
#     base_name = os.path.basename(path_src)
#     if not os.path.exists(path_src):
#         print(f'{path_src} not exists')
#         continue
#     shutil.copy(path_src, tgt_dir)
#     new_path = os.path.join(tgt_dir, base_name)
#     # change video_path to new_path
#     df.at[i, 'video_path'] = new_path
#     print(f'copy {path_src} to {tgt_dir}')
        
# df.to_csv('/home/wjh/projects/vid_download/meta_infos/new.csv', index=False)

dir_path = '/home/wjh/projects/vid_download/csvs/samples'
files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.csv')]
print(files)
# Read all CSV files and concatenate them into a single DataFrame, 去除重复行
df_cat = [pd.read_csv(f) for f in files]
total_len = 0
for i in range(len(df_cat)):
    print(len(df_cat[i]))
    total_len += len(df_cat[i])
print(total_len)
df = pd.concat(df_cat, ignore_index=True)
df = df.drop_duplicates()
print(len(df))
df.to_csv('total_0427.csv', index=False)