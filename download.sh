
###
 # @Author: jeremiah.wang
 # @Date: 2024-11-29 17:42:46
 # @LastEditTime: 2025-02-25 22:36:11
 # @Description: download.sh for download.py
### 
# csv_file_list=('1.csv' '2.csv')
# patch1_sample_500_1 下载在'/nasdata/wjh/videos'
csv_file_list=(
    # 0311,0312smaller,redownload
    # "meta_infos/unsucc.csv"
    "/share/wjh/panda70m/data/test-00000-of-00000.csv"
    # 'meta_infos/meta_info_0410.csv'
)
# ,'meta_infos/meta_info_0225_sample_3000_2.csv','meta_infos/meta_info_0225_sample_3000_3.csv')
for csv_file in "${csv_file_list[@]}"; do
    start_time=$(date +%s)
    echo "-------------------- $csv_file --------------------"
    echo -e "\e[31mstart_time: $start_time\e[0m"  # 使用红色字体输出
    python download.py --csv="$csv_file"
    end_time=$(date +%s)
    echo -e "\e[31mend_time: $end_time\e[0m"  # 使用红色字体输出
    elapsed_time=$((end_time - start_time))
    echo -e "\e[32melapsed_time: ${elapsed_time}s\e[0m"  # 使用绿色字体输出
done

# quick cmd
# check the number of json files
# ls -l videos/patch1_sample_100_1/*.json | wc -l

# check the format available for a video
# yt-dlp -F --list-formats https://www.youtube.com/watch\?v\=omP01s7RUSA --proxy 127.0.0.1:7892 --cookies cookies.txt

# 可以一次下载整个博主的全部视频：
# yt-dlp -vU -S res:360 --dateafter 20221101 --datebefore 20221130 https://www.youtube.com/@geopoliticshaiphong
