vid_path="/mnt/d/projects/video_download/test/avc1.640020_300-1280x720_PySzLfnAeuE_NA_麓山寺.mp4"
cmd = [
        "/usr/local/bin/ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,bit_rate,codec_name",
        "-of", "default=noprint_wrappers=1:nokey=1",
        vid_path
    ]
import os

# 执行cmd
result = os.popen(' '.join(cmd)).read()
print(result)