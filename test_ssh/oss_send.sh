#!/bin/bash

# ~/oss/oss login
# Username:15029201766
# Password:XzXeKvP@cD29XME

# ~/oss/oss mkdir oss://datasets

# ~/oss/oss cp 个人数据.zip oss://datasets/


#查看我上传的 个人数据.zip
# ~# ~/oss/oss ls -s -d oss://datasets/

remote_path=oss://data_208/
local_path=result.zip

# Record the start time
start_time=$(date +%s)

# Start cp
~/oss/oss cp $local_path $remote_path

# Record the end time
end_time=$(date +%s)

# Calculate the elapsed time
elapsed_time=$((end_time - start_time))

echo "Elapsed time: $elapsed_time seconds"