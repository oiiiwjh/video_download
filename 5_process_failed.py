# 处理失败的文件
import os
import pandas as pd
from tqdm import tqdm
import shutil

def get_vid_size(vid_path):
    """
    Get the size of the video file.
    :param vid_path: Path to the video file.
    :return: Size of the video file in bytes.
    """
    if not os.path.exists(vid_path):
        print(f"视频文件不存在：{vid_path}")
        return 0
    return os.path.getsize(vid_path)
def check_csv(vid_path, csv_path):
    """
    Check if the CSV file is empty or not.
    :param csv_path: Path to the CSV file.
    :return: True if the CSV file is empty, False otherwise.
    """
    error_csv_path = 'error_1.csv'
    error = []
    sample_name = vid_path.split('/')[-1]
    print('sample_name:', sample_name)
    data = pd.read_csv(csv_path)
    for i in tqdm(range(len(data)), desc=f"Checking {sample_name}"):
        base_name = data.iloc[i]['video_path'].split('/')[-1]
        new_vid = os.path.join(vid_path, base_name) # video path
        src_vid = data.iloc[i]['video_path'] # source video path
        if src_vid.startswith('/nasdata'):
            src_vid = src_vid.replace('/nasdata/wjh/videos', '/share/wjh', 1)
        if not src_vid.startswith('/share'):
            print(f"无效路径（非/share开头）：{src_vid}")
            error.append([new_vid, src_vid, 0, 0, 0])
            continue
        # if not os.path.exists(src_vid):
        #     print(f"源文件不存在：{src_vid}")
        #     error.append([new_vid, src_vid, 0, 0, 1])
        #     continue
        if not os.path.exists(new_vid):
            print(f"目标文件不存在：{new_vid}")
            error.append([new_vid, src_vid, 0, 0, 2])
            continue
        # print(new_vid, src_vid)
        new_size = get_vid_size(new_vid)
        src_size = get_vid_size(src_vid)
        if new_size != src_size:
            print(f"视频大小不一致：{new_vid} ({new_size}) vs {src_vid} ({src_size})")
            error.append([new_vid, src_vid, new_size, src_size, 3])
    # save error to csv, error_csv already exists
    if len(error) > 0:
        error_df = pd.DataFrame(error, columns=['new_vid_path', 'src_vid_path', 'new_size', 'src_size', 'error'])
        error_df.to_csv(error_csv_path, mode='a', index=False, header=False)
        print(f"错误信息已保存到 {error_csv_path}")
    
def copy_video(error_csv):
    """
    Copy the video files from the source to the destination.
    :param error_csv: Path to the error CSV file.
    :return: None
    """
    data = pd.read_csv(error_csv)
    for i in tqdm(range(len(data)), desc="Copying videos"):
        error_type = data.iloc[i]['error']
        if error_type != 3:
            continue
        new_vid = data.iloc[i]['new_vid_path']
        src_vid = data.iloc[i]['src_vid_path']
        shutil.copy(src_vid, new_vid)
        print(f"复制视频：{src_vid} -> {new_vid}")
        
if __name__ == '__main__':
    vid_dir = '/share/wjh/raw_videos'
    csv_dir = '/share/wjh/csv_share'

    error_csv_path = 'error_1.csv'
    # Check if the CSV file 存在，若不存在， 新建一个空的CSV文件，包含表头，分别为 new_vid_path, src_vid_path, new_size, src_size
    if not os.path.exists(error_csv_path):
        df = pd.DataFrame(columns=['new_vid_path', 'src_vid_path', 'new_size', 'src_size', 'error'])
        df.to_csv(error_csv_path, index=False)
    print(f"错误信息已保存到 {error_csv_path}")
    # print(os.listdir(vid_dir))
    # vid_list = os.listdir(vid_dir)
    # vid_list.sort()
    # vid_list = pd.read_csv('/home/wjh/projects/vid_download/cp_1.csv')['name'].tolist()
    # vid_list = [vid.split('.')[0] for vid in vid_list]
    vid_list = os.listdir(csv_dir)
    vid_list = [vid.split('.')[0] for vid in vid_list if 'supp' in vid]
    vid_list = [
        # "total_done_sample_supp_9.csv",
        # "total_done_sample_supp_10.csv",
        # "total_done_sample_supp_11.csv",
        "total_done_sample_supp_14.csv",
        "total_done_sample_supp_15.csv",
        
        # 'total_done_sample_supp_7',
        # 'total_done_sample_supp_8',
        # 'total_done_sample_supp_9',
        # 'total_done_sample_supp_10',
        # 'total_done_sample_supp_11',
    ]
    csv_dir = '/share/wjh/raw_videos/'
    # vid_dir = '/mnt/usb-hdd-1/data/raw_videos/total_done_sample_200_1'
    # vid_list = os.listdir('/share/wjh/raw_videos/total_done_sample_200_1')
    # print(tgt_paths)
    # print(vid_list)
    for vid in vid_list:
        # if 'total_done' not in vid:
        #     continue
        csv_path = os.path.join(csv_dir, vid)
        vid_path = os.path.join(vid_dir, vid)
        if not os.path.exists(csv_path):
            continue
        # print('csv_path:', csv_path)
        # print('vid_path:', vid_path)
        # check_csv(vid_path, csv_path)
        before_size = os.path.getsize(csv_path)
        after_size = os.path.getsize(vid_path)
        # print('before_size:', before_size)
        # print('after_size:', after_size)
        if before_size != after_size:
            print(f"视频大小不一致：{csv_path} ({before_size}) vs {vid_path} ({after_size})")
            # error.append([vid_path, csv_path, before_size, after_size, 3])
    
    # copy_video(error_csv_path)
    