<!--
 * @Author: jeremiah.wang
 * @Date: 2025-02-25 21:02:09
 * @LastEditTime: 2025-02-26 11:51:09
 * @Description: 
-->
## func cal
cal_csv_plot
cal_csv
cal_diff_csv
cal_vid

## files
cookies* for download
### important csv (meta_infos/)
meta_info_0221.csv 总文件csv
meta_info_0221_with_hours.csv 总文件csv(with hours)

bigger_videos.txt 交给外包来下载的数据
meta_info_bigger.csv 交给外包来下载的数据(csv type)

meta_info_0225_done.csv 截至0225前下载在服务器中的数据(video_path指向视频路径, nums = 2024)
meta_info_0225.csv 截至0225前未下载的数据(nums = 24776)

## main func
- download related
downlaod.py
downlaod.sh

- sample specific nums
sample.py

- temp file
temp.py
tmp.py


## others
ffmpeg.sh for ffmpeg install

## download log
### 0225
- 将外包所需的数据分出, 为meta_info_bigger.csv, 并且从原csv(0221)中去除,得到csv(0225)
- 0225之前的一批数据保存为csv: meta_info_0225_done.csv
- 从meta_info_0225.csv中采样, sample_1000 & sample_1000_1, 并开始下载
- 0225 night: dlding [sample_1000, sample_1000_1, sample_3000, sample_3000_1]
### 0226
- 0225的数据未下载完成,原因:流量没了
### 0304
- meta_info_0304_done: 14984
- meta_info_0304: 9792
### 0305
本批数据中，0305中是之前本地下载的数据
- meta_info_0305_done: 707
- meta_info_0305: 9085
另外，bigger数据需要自己下载，则同样将youtube local从中滤去：
- meta_info_0305_bigger_done: 457 
- meta_info_0305_bigger: 9543
### 0306
- 在meta_info_0305的基础上，分成几个sample：3000, 3000_1, 3000_2, 3000_3
  

## meta_infos
- 目前，0312_smaller, 0311 尚未下载。其中包含大量不可下载的视频
- meta_info_biggest是长一些的视频，目前使用一些关键词筛选/时长筛选来选择其中一部分sample


# 传输数据setting
vim /etc/ssh/sshd_config
设置maxsession 调大

# 存在重复的
## 对于total_done_sample_500_1.csv而言
total_done_sample_200_110.csv: 1
1
['N-n3oFFPgNI']
total_done_sample_200_142.csv: 1
1
['tTLMcDgIie8']
## 对于total_done_sample_500_3.csv而言
total_done_sample_200_134.csv: 1
1
['UW7TIV-AHDs']


## 下载完成数据后的处理
1. 1_process_folder2csv
2. 2_process_dlded
get ..._sample_done, then process it to supp_i.csv in csvs/sample
3. mv to new folder in raw_video: cp_multi
4. change csv file to share/csv_share: change_share
5. check whether cp failed between csvs/samples and /share/raw_videos: process_failed

## meta_infos
meta_info_0331是最新需要下载
left_rows是被sample_by_keywords处理的结果

现在，total_done_sample_supp(7,8,left)并未执行，3 cp multi后的步骤，需要等yyk执行完后进行（for cpu limit）

total_done_sample_supp_left，是一部分应被sample_by_keywords滤掉的下载内容

