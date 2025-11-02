'''
Author: jeremiah.wang
Date: 2024-11-22 16:12:02
LastEditTime: 2025-02-25 22:17:28
Description: yt-dlp download video from youtube
'''
# from https://huggingface.co/Ligeng-Zhu/panda70m-download
import sys, os, os.path as osp
import yt_dlp
import asyncio
from concurrent.futures import ProcessPoolExecutor
import fire
import pandas as pd
import json

def ytb_download(url, json_info, output_dir="ytb_videos/"):
    
    os.makedirs(output_dir, exist_ok=True)
    uid = url.split("?v=")[-1]
    yt_opts = {
        # beginning: "bv[height=720][ext=mp4]"
        # "format": "bv[height=720]",  # [vcodec!^=av] # Download the best quality available
        "format": "bv", # for panda70m
        # "format": "bv[height=720][ext=mp4][vcodec!^=av]", 
        "proxy":"127.0.0.1:7893",
        "outtmpl": osp.join(output_dir, f"{uid}.%(ext)s"),  # Set the output template
        # "cookiesfrombrowser": "chrome",  # Automatically use Chrome's cookies
        # "cookiefile": "cookies.txt",  # Use a custom cookies file
        # "postprocessors": [
        #     {
        #         "key": "FFmpegVideoConvertor",
        #         "preferedformat": "mp4",  # Convert video to mp4 format, and it cost a lot of time !!
        #     }
        # ],
        # "verbose" : True,
        'abort-on-error': True, # Abort downloading when an error occurs
        'retries': 60, # Number of retries
        'ffmpeg_location': '/usr/bin/ffmpeg', # Path to ffmpeg
        'quiet': True, # Suppress output
        'sleep-requested': 5, # Sleep for 1.25 seconds between requests
        'min-sleep-interval': 60,
        'max-sleep-interval': 90,
    }

    video_path_mp4 = osp.join(output_dir, f"{uid}.mp4")
    video_path_webm = osp.join(output_dir, f"{uid}.webm")
    meta_path = osp.join(output_dir, f"{uid}.json")
    
    if (osp.exists(video_path_mp4) or osp.exists(video_path_webm)) and osp.exists(meta_path):
        print(f"\033[91m{uid} already labeled.\033[0m")
        return 0

    try:
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download([url])
        with open(osp.join(output_dir, f"{uid}.json"), "w") as fp:
            json.dump(json_info, fp, indent=2)
        return 0
    except Exception as e:
        print(f"\033[91mError downloading {url}: {e}\033[0m")
        # with open(f"{output_dir}_failed_urls.txt", "a") as f:
        # with open(f"/home/wjh/projects/vid_download/meta_infos/z0322_dld.log", "a") as f:
        #     f.write(f"{url}\n")
        if 'Requested format is not available' in str(e):
            with open(f"/home/wjh/projects/vid_download/meta_infos/z0322_dld_format_noavailable.log", "a") as f:
                f.write(f"{url}\n")
        elif 'removed by' in str(e):
            with open(f"/home/wjh/projects/vid_download/meta_infos/z0322_dld_removed_by.log", "a") as f:
                f.write(f"{url}\n")
        elif 'Private video' in str(e):
            with open(f"/home/wjh/projects/vid_download/meta_infos/z0322_dld_private_video.log", "a") as f:
                f.write(f"{url}\n")
        else:
            with open(f"/home/wjh/projects/vid_download/meta_infos/z0322_dld_othererr.log", "a") as f:
                f.write(f"{url}, {str(e)}\n")
        return -1



async def main(csv_path, max_workers=10, shards=0, total=-1, limit=False):
    # [wjh] base dir
    # base_dir = '/share/wjh'
    base_dir = '/share/wjh/panda70m/raw_videos' # for panda70m
    
    PPE = ProcessPoolExecutor(max_workers=max_workers)
    loop = asyncio.get_event_loop()

    df = pd.read_csv(csv_path)
    csv_path = csv_path.split('/')[-1]
    output_dir =  csv_path.replace(os.path.basename(csv_path),f'{base_dir}/{csv_path.split(".")[0]}')

    tasks = []

    data_list = list(df.iterrows())

    if total > 0:
        chunk = len(data_list) // total
        begin_idx = shards * chunk
        end_idx = (shards + 1) * chunk
        if shards == total - 1:
            end_idx = len(data_list)
        data_list = data_list[begin_idx:end_idx]
    print(f"download total {len(data_list)} videos")
    
    for idx, (index, row) in enumerate(data_list):
        # video_url = row["video_url"]
        video_url = row["url"] # for panda70m
        json_info = {
            # "duration": row["duration"],
            # "description": row["description"],
            "caption": row["caption"],
        }
        tasks.append(
            loop.run_in_executor(PPE, ytb_download, video_url, json_info, output_dir)
        )
        if idx >= 20 and limit:
            break
    res = await asyncio.gather(*tasks)

    print(f"[{sum(res)} / {len(res)}]")


# def entry(csv="meta_data_sample_500.csv", shards=0, total=-1, limit=False,max_workers=16):
#     print(shards,total,max_workers)
#     asyncio.run(main(csv, max_workers=max_workers, shards=shards, total=total, limit=limit))


import time

def entry(csv="meta_data_sample_500.csv", shards=0, total=-1, limit=False, max_workers=2):
    print(csv, shards, total, max_workers)
    start_time = time.time()
    print(f"\033[92mStarting execution at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\033[0m")
    asyncio.run(main(csv, max_workers=max_workers, shards=shards, total=total, limit=limit))
    end_time = time.time()
    print(f"\033[92mFinished execution at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}\033[0m")
    print(f"\033[92mTotal execution time: {end_time - start_time:.2f} seconds\033[0m")


# def copy_video(src_path, dst_path):
#     """
#     Copy the video files from the source to the destination.
#     :param error_csv: Path to the error CSV file.
#     :return: None
#     """
#     shutil.copy(src_path, dst_path)
#     print(f"复制视频：{src_vid} -> {new_vid}")
        
def add_download(csv_path):
    data = pd.read_csv(csv_path)
    for i in range(len(data)):
        video_path = data.iloc[i]['new_vid_path']
        video_url = video_path.split('/')[-1]
        video_url = video_url.split('.')[0]
        video_url = f'https://www.youtube.com/watch?v={video_url}'
        output_dir = os.path.dirname(video_path)
        ytb_download(video_url, json_info={}, output_dir='videos/')
        print(f"Downloaded {video_url} to {video_path}")
if __name__ == "__main__":
    fire.Fire(entry)
    # add_download(csv_path='/home/wjh/projects/vid_download/error_1.csv')    
