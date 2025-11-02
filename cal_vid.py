'''
Author: jeremiah.wang
Date: 2025-02-18 18:55:49
LastEditTime: 2025-02-21 20:24:51
Description: 
'''
import os
import cv2
import time
import subprocess
from pymediainfo import MediaInfo
import json
def get_video_duration(video_path):
    # Get video duration
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # frame_count = 0
    duration = frame_count / fps
    cap.release()
    return fps,frame_count,duration

def get_video_metadata(video_path):
    mi = MediaInfo.parse(video_path)
    # for tk in mi.tracks:
    #     print(tk.codec)
    myFormat = mi.to_data()['tracks'][1]['format']
    return myFormat



def convert_av1_to_h264(input_path, output_path):
    cmd = [
        'ffmpeg',
        '-i', input_path,
        "-vcodec", "h264",
        # "-c","copy",
        # " -vcodec h264 -threads 5 -preset ultrafast ",
        # '-c:a', 'aac',
        '-an', '-sn',
        
        output_path
    ]
    try:
        # subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess.run(cmd)
        print(f"Successfully converted {input_path} to H.264 at {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e.output.decode(' utf8 ')}")
        
if __name__ == "__main__":
    # cal duration
    vid_dir = "/home/wjh/download/csvs/nasdata/wjh/videos/csvs/patch1_sample_500_4"
    IMG_EXTENSIONS = ('mp4','webm')
    total_duration = 0 # seconds
    total_duration_json = 0 # minutes
    for root, _, files in os.walk(vid_dir):
        for file in files:
            time.sleep(1)
            # print('='*20,f"[{file}]","="*20)
            if file.endswith(IMG_EXTENSIONS):
                video_path = os.path.join(root, file)
                # video_path = '/home/wjh/download/test/5fPp0z_thRs_1.mp4'
                output_path = video_path
                
                # transform video and check codec
                # print('='*20,f"[{file}] before {codec}","="*20) 
                try:
                    codec = get_video_metadata(output_path)
                except Exception as e:
                    print(f"[{e}] {file}",'-'*10,'>>')
                    continue
                # if codec == "AV1":
                #     output_path = video_path.replace(".mp4","_h264.mp4")
                #     convert_av1_to_h264(video_path, output_path)
                #     codec = get_video_metadata(video_path)
                #     print('='*20,f"[{file}] after {codec}","="*20)
                
                # get video duration
                fps,frame_count,duration = get_video_duration(output_path)
                print(file, codec, fps, frame_count, duration)
                total_duration += duration
            elif file.endswith('json'):
                dt = json.load(open(os.path.join(root, file)))
                duration = dt['duration']
                has_hr = len(duration.split(':')) == 3
                if has_hr:
                    total_duration_json += int(duration.split(':')[0])*60 + int(duration.split(':')[1]) + int(duration.split(':')[2])/60
                else:
                    total_duration_json += int(duration.split(':')[0]) + int(duration.split(':')[1])/60
                print(file, total_duration_json)
    # print(f"Total video duration: {total_duration} seconds")
    print(f"Total video duration: {total_duration/60} minutes")
    print(f"Total video duration_json: {total_duration_json} minutes")
    # vis codec
    
