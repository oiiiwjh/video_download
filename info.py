# 遍历vid_dir的视频，给出对应的视频大小、时间长度、分辨率、帧率、比特率、编码器
# 使用ffmpeg
import os
import subprocess
import csv

vid_dir = "/mnt/d/projects/video_download/test"
vid_list = [f for f in os.listdir(vid_dir) if f.endswith('.mp4')]
print(f"检测到视频文件数量: {len(vid_list)}")

# 输出 CSV 路径（保存在视频目录下）
out_csv = os.path.join(vid_dir, "video_info.csv")
rows = []
# header
rows.append(["filename", "size_bytes", "size_MB", "duration_sec", "width", "height", "fps", "bitrate", "codec"])

total_duration = 0.0
total_size = 0

for vid in vid_list:
    vid_path = os.path.join(vid_dir, vid)
    # 获取 duration 和 size
    cmd = [
        "/usr/local/bin/ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1:nokey=1",
        vid_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"ffprobe 读取 format 失败: {vid} -> {result.stderr.strip()}")
        continue
    parts = result.stdout.strip().split("\n")
    if len(parts) < 2:
        print(f"ffprobe format 输出格式异常: {vid} -> {result.stdout}")
        continue
    try:
        duration = float(parts[0])
        size = int(parts[1])
    except Exception as e:
        print(f"解析 duration/size 失败: {vid} -> {e}")
        continue

    total_duration += duration
    total_size += size

    # 获取流信息（宽高、帧率、比特率、编码器）
    cmd = [
        "/usr/local/bin/ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,bit_rate,codec_name",
        "-of", "default=noprint_wrappers=1:nokey=1",
        vid_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"ffprobe 读取 stream 失败: {vid} -> {result.stderr.strip()}")
        continue
    stream_parts = result.stdout.strip().split("\n")[:5]
    if len(stream_parts) < 5:
        # 如果信息不完整，填充空值
        stream_parts += [""] * (5 - len(stream_parts))

    # ffprobe 顺序: width,height,r_frame_rate,bit_rate,codec_name
    try:
        width = stream_parts[0] if stream_parts[0] else 0
        height = stream_parts[1] if stream_parts[1] else 0
        r_frame_rate = stream_parts[2] if stream_parts[2] else "0/1"
        bit_rate = stream_parts[3]
        codec_name = stream_parts[4]
        fr_parts = r_frame_rate.split("/")
        fps = float(fr_parts[0]) / float(fr_parts[1]) if len(fr_parts) == 2 and int(fr_parts[1]) != 0 else 0.0
    except Exception as e:
        print(f"解析 stream 信息失败: {vid} -> {e}")
        width = height = 0
        fps = 0.0
        bit_rate = ""
        codec_name = ""

    print(f"视频文件: {vid}")
    size_mb = size / (1024 * 1024)
    print(f"大小: {size_mb:.2f} MB")
    print(f"时长: {duration} 秒")
    print(f"分辨率: {width}x{height}")
    print(f"帧率: {fps} fps")
    print(f"比特率: {bit_rate} bps")
    print(f"编码器: {codec_name}")

    # 添加到 CSV 行
    rows.append([vid, size, f"{size_mb:.2f}", f"{duration:.2f}", width, height, f"{fps:.3f}", bit_rate, codec_name])

print(f"总时长: {total_duration} 秒")
total_size_mb = total_size / (1024 * 1024)
print(f"总大小: {total_size_mb:.2f} MB")

# 写入 CSV（覆盖）
try:
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        # 写入总计行
        writer.writerow(["TOTAL", total_size, f"{total_size_mb:.2f}", f"{total_duration:.2f}", "", "", "", "", ""])
    print(f"已写入 CSV: {out_csv}")
except Exception as e:
    print(f"写入 CSV 失败: {e}")