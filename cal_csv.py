'''
Author: jeremiah.wang
Date: 2025-02-18 18:48:23
LastEditTime: 2025-02-18 18:49:05
Description: 计算时长
'''
import csv
from collections import Counter
import re

def extract_city(description):
    cities = ['上海', '北京', '广州', '深圳', '杭州', '成都', '重庆', '南京', '武汉', '西安', '长沙', '宁波', '苏州', '厦门', '青岛', '天津', '大连', '沈阳', '济南', '郑州', '昆明', '贵阳', '长春', '哈尔滨', '福州', '合肥', '石家庄', '南昌', '太原', '呼和浩特', '乌鲁木齐', '兰州', '银川', '西宁', '南宁', '海口', '三亚', '拉萨', '澳门', '香港', '台北']
    for city in cities:
        if city in description:
            return city
    return '其他'

def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    else:
        return 0

def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def analyze_csv(file_path):
    video_count = 0
    total_duration = 0
    # city_counter = Counter()

    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            video_count += 1
            
            # 統計視頻時長
            duration = row['duration']
            # print(duration)
            total_duration += time_to_seconds(duration)
            
            # 統計城市出現次數
            # city = extract_city(row['description'])
            # city_counter[city] += 1

    # 計算平均時長
    average_duration = total_duration / video_count if video_count > 0 else 0

    return video_count, seconds_to_hms(total_duration), seconds_to_hms(int(average_duration)) # , city_counter.most_common(5)

# 使用函數
file_path = 'patch1_sample_100.csv'
# video_count, total_duration, average_duration, top_cities = analyze_csv(file_path)
video_count, total_duration, average_duration = analyze_csv(file_path)

print(f"視頻總數: {video_count}")
print(f"總時長: {total_duration}")
print(f"平均時長: {average_duration}")
# print("出現次數最多的5個城市:")
# for city, count in top_cities:
#     print(f"{city}: {count}次")