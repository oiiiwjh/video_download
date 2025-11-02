# this file is for csv video path coloumn changing in share folder
import pandas as pd
import os
import re

def change_csv(src_csv, tgt_csv):
    vid_dir_base = '/share/wjh/raw_videos'
    print(src_csv)
    id = src_csv.split('/')[-1].split('.')[0]
    match = re.search(r"total_done_sample_supp_\d+", src_csv)
    id = match.group()
    # id = id.replace('done_','')
    print('id',id)
    dt = pd.read_csv(src_csv)
    dt['video_path'] = dt['video_path'].apply(lambda x: f"{vid_dir_base}/{id}/{os.path.basename(x)}")
    
    # for idx, row in dt.iterrows():
    #     if not os.path.exists(row['video_path']):
    #         print(f"Error: {row['video_path']} not exists")
    dt.to_csv(tgt_csv, index=False)
    

if __name__ == '__main__':
    # only have to change meta_path (dir to csv)
    # -------------------------------------
    # id_list = [
    #     "total_done_sample_200_20", "total_done_sample_200_33", "total_done_sample_200_6", 
    #     "total_done_sample_200_61"
    # ]
    # meta_path = [os.path.join('/share/wjh/step1_video/unfinished/outputs',id,'meta') for id in id_list]
    # meta_path.append('/share/wjh/step1_video/unfinished/meta_infos')
    meta_path = [
        '/home/wjh/projects/vid_download/csvs/samples'
    ]
    selected_files = [
        # "total_done_sample_supp_9.csv",
        # "total_done_sample_supp_10.csv",
        # "total_done_sample_supp_11.csv",
        "total_done_sample_supp_14.csv",
        "total_done_sample_supp_15.csv",
    ]
    # 逐级遍历base_dir下的所有csv文件
    for base_dir in meta_path:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if not file.endswith('.csv'):
                    print(f"Skip {file}")
                    continue
                if 'supp' not in file:
                    # print(f"Skip {file}")
                    continue
                if file not in selected_files:
                    # print(f"Skip {file}")
                    continue
                print(f"Processing {file}")
                src_csv = os.path.join(root, file)
                tgt_csv = os.path.join('/share/wjh/csv_share', file)
                # if os.path.exists(tgt_csv):
                #     # print(f"File already exists: {tgt_csv}")
                #     continue
                if len(os.path.basename(src_csv).split('_')) != 5:
                    print(f"Skip {src_csv}")
                    continue
                print(src_csv,tgt_csv)
                change_csv(src_csv, tgt_csv)
    # file_list = [
    #     # '/home/wjh/projects/vid_download/csvs/samples/total_done_sample_500_1.csv',
    #     # '/home/wjh/projects/vid_download/csvs/samples/total_done_sample_500_2.csv',
    #     # '/home/wjh/projects/vid_download/csvs/samples/total_done_sample_500_3.csv',
    #     '/home/wjh/projects/vid_download/csvs/samples/total_done_sample_200.csv',
    #     '/home/wjh/projects/vid_download/csvs/samples/total_done_sample_500.csv',
    # ]
    # for file in file_list:
    #     tgt_csv = os.path.join('/share/wjh/csv_share', file.split('/')[-1])
    #     # change_csv(file, tgt_csv)