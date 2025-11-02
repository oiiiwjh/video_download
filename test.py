import pandas as pd
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import cv2
import os
os.environ['OPENCV_FFMPEG_READ_TIMEOUT'] = '5000'  # Set timeout for OpenCV FFMPEG read
csv_name = '/home/wjh/projects/vid_download/panda_70m.csv'
dt = pd.read_csv(csv_name)

def get_video_info_ffmpeg(video_path):
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=avg_frame_rate,nb_frames,duration',
        '-of', 'json',
        video_path
    ]
    try:
        # result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        # info = json.loads(result.stdout)
        # stream = info['streams'][0]
        # # fps
        # avg_frame_rate = stream.get('avg_frame_rate', '0/1')
        # num, denom = avg_frame_rate.split('/')
        # fps = float(num) / float(denom) if float(denom) != 0 else 0
        # # duration
        # duration = float(stream.get('duration', 0))
        # # frame_count
        # nb_frames = stream.get('nb_frames')
        # if nb_frames is not None:
        #     frame_count = int(nb_frames)
        # else:
        #     frame_count = int(fps * duration) if fps > 0 and duration > 0 else 0
        # return fps, duration, frame_count
        # get frame count
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)#, params=['ffmpeg_read_timeout=5000'])
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # get fps
        fps = cap.get(cv2.CAP_PROP_FPS)
        # get duration in seconds
        duration = frame_count / fps
        # print(f"Video: {video_path}, FPS: {fps}, Duration: {duration:.2f} seconds, Frame Count: {frame_count}")
        return fps, duration, frame_count
    except Exception as e:
        print(f"Error processing video {video_path}: {e}")
        return None, None, None

dt['fps'] = None
dt['duration'] = None
dt['frame_count'] = None

def process_row(idx_row):
    i, row = idx_row
    video_path = row['video_path']
    fps, duration, frame_count = get_video_info_ffmpeg(video_path)
    return i, fps, duration, frame_count, video_path

results = []
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_row, item): item[0] for item in dt.iterrows()}
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing videos"):
        i, fps, duration, frame_count, video_path = future.result()
        if fps is not None:
            dt.at[i, 'fps'] = fps
            dt.at[i, 'duration'] = duration
            dt.at[i, 'frame_count'] = frame_count
        else:
            print(f'Failed to open video: {video_path}')

dt.to_csv(csv_name, index=False)