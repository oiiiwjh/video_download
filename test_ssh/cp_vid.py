import pandas as pd
import os
import shutil
path = 'ssh_test_csv_1.csv'
tgt_dir = 'csv_1'
df = pd.read_csv(path)
video_paths = df['video_path'].dropna().tolist()
video_paths = [p for p in video_paths if os.path.isfile(p)]
print(len(video_paths))
os.makedirs(tgt_dir, exist_ok=True)
# shutil.rmtree(tgt_dir, ignore_errors=True)
for pt in video_paths:
    shutil.copy(pt, tgt_dir)