import pandas as pd
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
from functools import partial

def move_files_to_dir(tgt_dir, mv_vid_list):
    """多线程拷贝文件并显示进度（每个CSV处理一个进度条）"""
    os.makedirs(tgt_dir, exist_ok=True)
    
    # 过滤已存在的文件
    existing = {os.path.basename(f) for f in os.listdir(tgt_dir)}
    filtered_list = [f for f in mv_vid_list if os.path.basename(f) not in existing]
    
    if not filtered_list:
        return  # 没有需要拷贝的文件时直接返回
    
    with tqdm(total=len(filtered_list), desc=f'Copying {os.path.basename(tgt_dir)}', position=1, leave=False) as pbar:
        def copy_file(vid_path):
            dst = os.path.join(tgt_dir, os.path.basename(vid_path))
            if not os.path.exists(dst):
                shutil.copy(vid_path, dst)
            else: 
                if os.path.getsize(vid_path) != os.path.getsize(dst):
                    shutil.copy(vid_path, dst)
            pbar.update(1)
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(copy_file, filtered_list)


def main(csv_path,tgt_dir):
    tgt_dir = os.path.join(tgt_dir, csv_path.split('/')[-1].replace('.csv', ''))
    df = pd.read_csv(csv_path)
    src_list = df['video_path'].str.replace('nas', 'NAS', case=False).tolist()
    # src_list = df['video_path'].tolist()
    # src_list = [x.replace('nas','NAS') for x in src_list]
    # move video files to tgt_dir
    move_files_to_dir(tgt_dir, src_list)
    
if __name__ == '__main__':

    tgt_dir = '/NASdata/wjh/videos/not_done'
    csv_pd = pd.read_csv('/home/wjh/projects/vid_download/for_local_cp.csv')
    csv_list = csv_pd['name'].tolist()
    csv_list = [f"/home/wjh/projects/vid_download/csvs/samples/{csv}.csv" for csv in csv_list]
    # csv_list = csv_list[::-1]
    for csv in csv_list:
        print(f"Processing {csv}...")
        main(csv, tgt_dir)
        print(f"Done {csv}...")


# 最终写一个检查所有copy结果的脚本
# 比较的内容：
    # 1. share中文件数量是否与csv文件一致
    # 2. share中文件的大小是否与与csv中原始位置的大小一致？ 不一致要重新复制