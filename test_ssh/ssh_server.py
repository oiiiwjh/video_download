# ssh files to server
import pandas as pd
import os
import asyncssh
import asyncio
import time
from datetime import timedelta

def get_valid_paths(csv_path):
    """从CSV中读取并验证文件路径"""
    df = pd.read_csv(csv_path)
    video_paths = df['video_path'].dropna().tolist()
    return [p for p in video_paths if os.path.isfile(p)]

def remote_path_gen(local_path, remote_base):
    """生成远程路径"""
    filename = os.path.basename(local_path)
    remote_path = os.path.join(remote_base, filename)
    return remote_path

async def transfer_file(semaphore, local_path, hostname, port, username, auth, remote_base, results):
    """异步传输单个文件"""
    async with semaphore:
        try:
            async with asyncssh.connect(
                hostname, 
                port,
                username=username,
                known_hosts=None,
                **auth
            ) as conn:
                async with conn.start_sftp_client() as sftp:
                    # 准备远程路径
                    filename = os.path.basename(local_path)
                    remote_path = os.path.join(remote_base, filename)
                    remote_dir = os.path.dirname(remote_path)
                    
                    # 创建目录（支持递归创建）
                    try:
                        await sftp.makedirs(remote_dir, exist_ok=True)
                    except asyncssh.sftp.SFTPFailure as e:
                        if e.code != asyncssh.sftp.FX_FILE_ALREADY_EXISTS:
                            raise
                    
                    # 执行文件传输
                    file_size = os.path.getsize(local_path)
                    start_time = time.time()
                    await sftp.put(local_path, remote_path)
                    end_time = time.time()
                    duration = end_time - start_time
                    file_size_mb = file_size / (1024 * 1024)  # 转换为MB
                    print(f"✅ 成功传输 {local_path}，大小: {file_size_mb:.2f} MB，耗时: {duration:.2f} s")
                    
                    # 记录文件大小和传输时间
                    results.append((file_size_mb, duration))
                    
        except Exception as e:
            print(f"❌ 传输失败 {local_path}: {str(e)}")

async def main(csv_path, hostname, port, username, auth, remote_base, concurrency=20):
    """主异步函数"""
    valid_paths = get_valid_paths(csv_path)
    print(f"📁 待传输文件数: {len(valid_paths)}")
    
    # 创建信号量控制并发量
    semaphore = asyncio.Semaphore(concurrency)
    print('🚦 并发量:', concurrency)
    
    # 记录总传输时间
    total_start_time = time.time()
    
    # 用于记录每个文件的大小和传输时间
    results = []
    
    # 创建异步任务列表
    tasks = [
        transfer_file(
            semaphore,
            path,
            hostname,
            port,
            username,
            auth,
            remote_base,
            results
        ) for path in valid_paths
    ]
    
    # 并行执行所有任务
    await asyncio.gather(*tasks)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    print(f"📊 总传输时间: {total_duration:.2f} s")
    
    # 计算平均传输速度
    total_size_mb = sum(file_size for file_size, _ in results)
    average_speed = total_size_mb / total_duration if total_duration > 0 else 0
    print(f"📊 平均传输速度: {average_speed:.2f} MB/s")

if __name__ == "__main__": #  root@
    HOSTNAME = 'connect.westc.gpuhub.com'
    PORT = 31371
    USERNAME = 'root'
    CSV_PATH = 'ssh_test_csv.csv'
    REMOTE_BASE = '/root/autodl-tmp/videos_208'
    df = pd.read_csv(CSV_PATH)
    AUTH = {
        # 密码认证
        "password": "bByUcZBJBG0Y",
        
        # 密钥认证（推荐）
        # "client_keys": ["/path/to/private_key"]
    }
    # 并发参数
    CONCURRENCY = 10  # 根据网络状况调整（建议5-50之间）

    # 执行异步主程序
    asyncio.run(main(
        CSV_PATH,
        HOSTNAME,
        PORT,
        USERNAME,
        AUTH,
        REMOTE_BASE,
        CONCURRENCY
    ))