import os
import pandas as pd
from tqdm import tqdm

base_dir = '/share/wjh/megasam_outputs'
pd_path = '/home/wjh/projects/vid_download/sampled_clips_scores.csv'
dt = pd.read_csv(pd_path)
# 将num_frames求和
total_num_frames = dt['num_frames'].sum()
print(f"总帧数: {total_num_frames}")

dt_ids = list(dt['id'])

# 定义文件大小变量, MB计算
cache_flow_size = 0
depth_anything_size = 0
uni_depth_size = 0
img_size = 0
reconstruct_size = 0
pose_size = 0
motion_prb_size = 0
dispsize = 0
# 遍历所有子目录
for root, dirs, files in os.walk(base_dir):
    print(f"当前目录: {root}")
    print(f"子目录: {dirs}")
    # print(f"文件: {files}")
    id_root = root.split('/')
    if len(id_root) > 4:
        id_root = id_root[4]
        if id_root not in dt_ids:
            print(f"跳过目录: {root}")
            continue
    # print(id_root)
    for file in tqdm(files):
        # print(file)
        # pass
        path = os.path.join(root, file)
        # 计算文件大小
        file_size = os.path.getsize(path)
        # MB
        file_size_mb = file_size / (1024 * 1024)
        # add to size
        if 'cache-flow' in path:
            cache_flow_size += file_size_mb
        elif 'depth-anything' in path:
            depth_anything_size += file_size_mb
        elif 'unidepth' in path:
            uni_depth_size += file_size_mb
        elif 'img' in path:
            img_size += file_size_mb
        elif 'reconstructions' in path:
            reconstruct_size += file_size_mb
            if 'poses' in path:
                pose_size += file_size_mb
            if 'motion_prob' in path:
                motion_prb_size += file_size_mb
            if 'disps' in path:
                dispsize += file_size_mb
        else:
            print(f"未知文件: {path}")
            continue
        # 打印文件大小
        # print(f'文件: {path}, 大小: {file_size_mb:.2f} MB')
        # print(cache_flow_size, depth_anything_size, uni_depth_size, img_size, reconstruct_size)

# 将结果保存到CSV文件
data = {
    'total_num_frames': [total_num_frames],
    'total_seconds': [total_num_frames / 30],
    'cache_flow_size': [cache_flow_size],
    'depth_anything_size': [depth_anything_size],
    'uni_depth_size': [uni_depth_size],
    'img_size': [img_size],
    'reconstruct_size': [reconstruct_size],
    'pose_size': [pose_size],
    'motion_prb_size': [motion_prb_size],
    'dispsize': [dispsize]
}
df = pd.DataFrame(data)
# output_csv_path = os.path.join(base_dir, 'file_sizes.csv')
output_csv_path = 'file_sizes.csv'
df.to_csv(output_csv_path, index=False)