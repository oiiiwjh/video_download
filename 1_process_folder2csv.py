# 根据json和视频文件，将其整合为csv文件，包含id, vid_path

# TODO: 处理不含有json文件的视频
import pandas as pd
import os
from collections import Counter
from tqdm import tqdm
import shutil
import cv2
import ffmpeg
try:
    from pandarallel import pandarallel

    PANDA_USE_PARALLEL = True
except ImportError:
    PANDA_USE_PARALLEL = False
def video_path_check(json_path):
    """Check if the video path exists."""
    vid_paths = [json_path.replace('.json', EXT) for EXT in ['.webm', '.mp4', '.mkv']]
    for vid_path in vid_paths:
        if os.path.exists(vid_path):
            return vid_path
    return ""

def dir_to_csv(tgt_dir, tgt_csv, cal_duration=False):
    
    # generate csv file, based on video dir, and save to tgt_csv
    print('='*20, f'Generate csv file: [{tgt_csv}]', '='*20)
    datalist = []
    for root, dirs, files in os.walk(tgt_dir):
        for file in tqdm(files):
            if file.endswith('.mp4') or file.endswith('.webm'):
                # print
                vid_path = os.path.join(root, file)
                # print(vid_path)
                vid_duration = 0
                try:
                    # 使用ffmpeg得到视频时长
                    # vid_duration = os.popen(f'/usr/bin/ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {vid_path}').read()
                    vid_id = os.path.basename(vid_path).split('.')[0]
                    if cal_duration:
                        cap = cv2.VideoCapture(vid_path)
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        nums = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        if fps == 0:
                            print(f'fps is 0, video path: {vid_path}, nums: {nums}')
                            continue
                        vid_duration = nums / fps
                        # vid_duration = ffmpeg.probe(vid_path)['format']['duration']
                        vid_duration = float(vid_duration)
                        vid_duration = f'{int(vid_duration/3600):02}:{int((vid_duration%3600)/60):02}:{int(vid_duration%60):02}' if vid_duration >= 3600 else f'{int((vid_duration%3600)/60):02}:{int(vid_duration%60):02}'
                        datalist.append({'id': vid_id, 'vid_duration': vid_duration, 'video_path': vid_path})
                    else:
                        datalist.append({'id': vid_id, 'video_path': vid_path})
                except Exception as e:
                    print(f'[{e}], video path: {vid_path}')
                    continue
    df = pd.DataFrame(datalist)
    df.to_csv(tgt_csv, index=False) # , mode='w', chunksize=1000)

def move_files_to_dir(tgt_dir, mv_vid_list):
    
    # move video to another directory tgt_dir
    print('='*20, f'Moving videos to [{tgt_dir}] directory', '='*20)
    # tgt_dir若不存在，则创建
    if not os.path.exists(tgt_dir):
        os.makedirs(tgt_dir)
    
    for vid_path in tqdm(mv_vid_list):
        # 若vid_path在tgt_dir中已存在，则跳过
        if os.path.exists(os.path.join(tgt_dir, os.path.basename(vid_path))):
            continue
        # print(vid_path, tgt_dir)
        shutil.move(vid_path, tgt_dir)

def get_duplicates(json_list):

    # process duplicated json file
    id_list = [os.path.basename(js).split('.')[0] for js in json_list]
    id_counter = Counter(id_list)
    duplicates = [item for item, count in id_counter.items() if count > 1]

    print('Duplicate IDs:', duplicates, len(duplicates))
    id_list = list(set(id_list))
    print('-'*20, 'final length:', len(id_list), '-'*20)
    id_dict = {id_: [] for id_ in duplicates}
    return duplicates, id_dict

if __name__ == '__main__':
    # # 读取meta_data_0225.csv文件
    # df = pd.read_csv('/share/wjh/videos/meta_data_0225.csv')
    # ids = list(df['id'])
    # # 从指定csv文件中，按照id将其中条目分开，分别保存到不同的csv文件中
    # csv_path = '/share/wjh/videos/meta_info_0225.csv'
    # df = pd.read_csv(csv_path)
    # for id in ids:
    #     temp_df = df[df['id'] == id]
    #     temp_df.to_csv(f'/share/wjh/videos/0225/{id}.csv', index=False)
    
    vid_paths = [
        "/share/wjh/meta_info_0410",
        # "/share/wjh/0324",
        # "/share/wjh/meta_info_0311", # smaller ones in big csv, besides biggest means the most biggest ones
        # "/share/wjh/meta_info_0322_biggest",
    ]
    tgt_dir = '/share/wjh/0420'
    vid_paths.append(tgt_dir) # make sure the tgt_dir is included
    tgt_csv = '/share/wjh/meta_data_0420.csv'
    # load json file paths
    json_list = []
    for vid_path in vid_paths:
        print(vid_path)
        # json_list.append(pd.read_csv(vid_path+'.csv'))
        for root, dirs, files in os.walk(vid_path):
            for file in files:
                if file.endswith('.json'):
                    # json_list.append(pd.read_csv(os.path.join(root, file)))
                    json_list.append(os.path.join(root, file))
                    # print(os.path.join(root, file))
    print(len(json_list))
    
    duplicates, id_dict = get_duplicates(json_list)
    # separate repeated and non-repeated json files
    mv_json_list = []
    mv_vid_list = []
    not_found_list = []
    print('='*20, 'process non-repeated id', '='*20)
    for json_path in tqdm(json_list):
        id_ = os.path.basename(json_path).split('.')[0]
        vid_path = video_path_check(json_path)
        if vid_path:
            if id_ in duplicates:
                id_dict[id_].append([json_path, vid_path])
            else:
                mv_json_list.append(json_path)
                mv_vid_list.append(vid_path)
        else:
            not_found_list.append(json_path)
    print(f'Video path not found list: [{len(not_found_list)}]')

    # process repeated json files, select the longest video, add to the list
    print('='*20, 'process repeated id', '='*20)
    for id_, paths in id_dict.items():
        if len(paths) == 1:
            (json_path, vid_path) = paths[0]
            mv_json_list.append(json_path)
            mv_vid_list.append(vid_path)
            
        else: # len(paths) > 1:
            print(f'ID: {id_}, paths: {paths}')
            # 检查每一个视频的时长，选择最长的视频
            max_duration = 0
            max_path = ''
            for (json_path, vid_path) in paths:
                # 检查视频文件长度
                vid_duration = os.popen(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {vid_path}').read()
                if float(vid_duration) > max_duration:
                    max_duration = float(vid_duration)
                    max_path = vid_path
            mv_json_list.append(json_path)
            mv_vid_list.append(vid_path)
            print(vid_path, max_duration)

    # move video files to tgt_dir
    move_files_to_dir(tgt_dir, mv_vid_list)
    # folder to csv
    dir_to_csv(tgt_dir, tgt_csv)