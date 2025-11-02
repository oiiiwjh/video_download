# 将文件复制到对应位置
import pandas as pd
import os
import shutil
from multiprocessing import Pool, Manager
from tqdm import tqdm
import time

def move_file(args):
    """
    使用大缓冲区移动文件，并处理元数据
    """
    src, dst, queue = args
    try:
        # 预处理检查
        if not os.path.exists(src):
            queue.put({'type': 'error', 'msg': f"Source not found: {src}"})
            return

        # 创建目标目录
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        
        # 复制文件内容（使用大缓冲区）
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            shutil.copyfileobj(fsrc, fdst, length=4*1024*1024)  # 16MB buffer
            # shutil.copyfileobj(fsrc, fdst, length=32*1024*1024)  # 16MB buffer
        
        # 保留元数据
        shutil.copystat(src, dst)
        
        # 删除源文件
        # os.remove(src)
        
        # 获取文件大小用于进度统计
        file_size = os.path.getsize(dst)
        queue.put({'type': 'progress', 'size': file_size})
        
    except Exception as e:
        # 清理可能存在的部分复制文件
        if os.path.exists(dst):
            try: os.remove(dst)
            except: pass
        queue.put({'type': 'error', 'msg': f"{src} -> {dst} | Error: {str(e)}"})

def main(csv_path):
    # 配置参数
    tgt_dir = csv_path.split('/')[-1].replace('.csv', '')  # 目标目录（默认与CSV文件同名）
    # num_workers = os.cpu_count() * 2
    num_workers = 8
    
    # 读取CSV文件
    df = pd.read_csv(csv_path)
    src_list = df['video_path'].tolist()

    # 生成任务列表（自动过滤无效路径）
    valid_tasks = []
    total_size = 0
    for src in src_list:
        src = src.strip()
        if src.startswith('/nasdata'):
            src = src.replace('/nasdata/wjh/videos', '/share/wjh', 1)
        if not src.startswith('/share'):
            print(f"无效路径（非/share开头）：{src}")
            continue
        if not os.path.exists(src):
            print(f"源文件不存在：{src}")
            continue
            
        # dst = src.replace('/NASdata', '/share', 1)
        base_name = os.path.basename(src)
        dst = os.path.join('/share/wjh/raw_videos', tgt_dir, base_name)
        if os.path.exists(dst):
            print(f"目标文件已存在：{dst}")
            continue
            
        try:
            file_size = os.path.getsize(src)
            valid_tasks.append((src, dst))
            total_size += file_size
        except:
            print(f"无法获取文件大小：{src}")
            continue

    print(f"待处理文件数：{len(valid_tasks)}")
    print(f"总数据量：{total_size/1024/1024:.2f} MB")

    # 准备多进程环境
    manager = Manager()
    queue = manager.Queue()
    task_args = [(src, dst, queue) for src, dst in valid_tasks]

    # 创建进程池
    with Pool(processes=num_workers) as pool:
        # 启动异步任务
        pool.map_async(move_file, task_args)
        
        # 进度监控
        progress = tqdm(total=total_size, unit='B', unit_scale=True, 
                        desc="传输进度", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]")
        
        transferred = 0
        errors = []
        
        while transferred < total_size:
            while not queue.empty():
                msg = queue.get()
                if msg['type'] == 'progress':
                    progress.update(msg['size'])
                    transferred += msg['size']
                elif msg['type'] == 'error':
                    errors.append(msg['msg'])
            
            # 检查剩余任务
            remaining = total_size - transferred
            if remaining > 0:
                # time.sleep(0.5)  # 降低CPU占用
                pass
            else:
                break
        
        # 处理剩余消息
        while not queue.empty():
            msg = queue.get()
            if msg['type'] == 'progress':
                progress.update(msg['size'])
            elif msg['type'] == 'error':
                errors.append(msg['msg'])
        
        progress.close()
        
        # 输出汇总信息
        summary = []
        summary.append(f"\n操作完成！成功传输：{len(valid_tasks)-len(errors)} 文件")
        summary.append(f"传输总量：{transferred/1024/1024:.2f} MB")
        if errors:
            summary.append("\n错误列表：")
            for error in errors:  # 显示最后5个错误
                summary.append(f"• {error}")
                summary.append(f"（共 {len(errors)} 个错误，完整日志请查看程序输出）")
        
        # 打印到控制台
        for line in summary:
            print(line)
        
        # 写入日志文件
        log_file = "cp_log.txt"
        with open(log_file, "a") as f:
            for line in summary:
                f.write(line + "\n")

if __name__ == "__main__":
    # 
    # csv_list = [
    #     "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_200_1.csv",
    # ]
    done_csv = os.listdir('/share/wjh/raw_videos')
    done_csv = [csv.split('.')[0] for csv in done_csv if 'total_done_sample' in csv]
    total_csv = os.listdir('/home/wjh/projects/vid_download/csvs/samples')
    total_csv = [csv.split('.')[0] for csv in total_csv if 'total_done_sample' in csv]
    print(done_csv, total_csv)
    # list做差集
    csv_list = list(set(total_csv) - set(done_csv))
    print(len(csv_list), csv_list)
    # csv_pd = pd.read_csv('/home/wjh/projects/vid_download/cp_1.csv')
    # csv_list = csv_pd['name'].tolist()
    # csv_list = [f"/home/wjh/projects/vid_download/csvs/samples/{csv}.csv" for csv in csv_list]

    # manully add csv
    csv_list = [
        # "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_9.csv",
        # "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_10.csv",
        # "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_11.csv",
        # "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_12.csv",
        "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_14.csv",
        "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_15.csv",
        # "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_3.csv",
        # "/home/wjh/projects/vid_download/csvs/samples/total_done_sample_supp_4.csv",
    ]
    for csv in csv_list:
        print(f"Processing {csv}...")
        main(csv)
        print(f"Done {csv}...")
        # ，，注意注意，执行时注将将删文件去掉