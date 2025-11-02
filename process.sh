DEVICE=226
STAGE=2

CUDA_LIST=0,1,2,3,4,5,6,7
GPU_NUM=8

ROOT_CSV=/nasdata/csv/${DEVICE}
CLIP_PAYH=/root/step2_megasam/clips
DIR_PATH=/nasdata/megasam_outputs
LOG_PATH=/nasdata/logs
EMPTY_DIR=/nasdata/empty

for dir in ${ROOT_CSV} ${CLIP_PAYH} ${DIR_PATH} ${EMPTY_DIR}; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
    fi
done

measure_time() {
    local step_number=$1
    shift
    local green="\e[32m"
    local red="\e[31m"
    local no_color="\e[0m"
    local yellow="\e[33m"
    
    start_time=$(date +%s)
    echo -e "${green}Step $step_number started at: $(date)${no_color}"

    "$@"

    end_time=$(date +%s)
    echo -e "${red}Step $step_number finished at: $(date)${no_color}"
    echo -e "${yellow}Duration: $((end_time - start_time)) seconds${no_color}"
    echo "---------------------------------------"
}

while true; do
    # 判断目录中是否有csv文件
    if [ -z "$(ls -A $ROOT_CSV/*.csv 2>/dev/null)" ]; then
        echo "No csv files found in $ROOT_CSV. Waiting..."
        sleep 5
        continue
    else
        for csv in "$ROOT_CSV"/*.csv; do
            # 提取文件名（不包含扩展名）
            filename=$(basename "$csv" .csv)
            echo "Processing file: $csv"

            tosutil cp -r tos://nanjin-uni-v100/stage${STAGE}/${filename} ${CLIP_PAYH}

            ROOT_LOG="${LOG_PATH}/${filename}"
            if [ ! -d "${ROOT_LOG}" ]; then
                mkdir -p ${ROOT_LOG}
            fi

            python rename.py ${csv} --clips_path ${CLIP_PAYH}/${filename}

            measure_time 1 python run_inference.py ${csv} --dir_path ${DIR_PATH} \
            --gpu_id ${CUDA_LIST} --num_workers 16 --extract_videos \
            --extract_interval 0.2 > ${ROOT_LOG}/extract_videos.txt

            CUDA_VISIBLE_DEVICES=${CUDA_LIST} measure_time 2 torchrun --standalone --nproc_per_node ${GPU_NUM} Depth-Anything/inference.py \
            ${csv} \
            --encoder vitl \
            --checkpoints_path checkpoints \
            --dir_path ${DIR_PATH} \
            --bs 32 \
            --num_workers ${GPU_NUM} > ${ROOT_LOG}/depth_anything.txt


            CUDA_VISIBLE_DEVICES=${CUDA_LIST} measure_time 3 torchrun --standalone --nproc_per_node ${GPU_NUM} UniDepth/inference.py \
            ${csv} \
            --dir_path ${DIR_PATH} \
            --checkpoints_path checkpoints \
            --bs 64 \
            --num_workers ${GPU_NUM} > ${ROOT_LOG}/unidepth.txt

            measure_time 4 python run_inference.py ${csv} --dir_path ${DIR_PATH} \
            --checkpoints_path checkpoints --gpu_id ${CUDA_LIST} \
            --num_workers $((GPU_NUM * 4))\
            --camera_tracking > ${ROOT_LOG}/camera_tracking.txt

            # background process
            tosutil mkdir tos://nanjin-uni-v100/stage${STAGE}_megasam/${filename} &
            tosutil cp -r /nasdata/megasam_outputs/${filename} tos://nanjin-uni-v100/stage${STAGE}_megasam/${filename} &
            tosutil rm -r tos://nanjin-uni-v100/stage${STAGE}/${filename} &
            rsync --delete-before --force -r ${EMPTY_DIR}/ ${DIR_PATH}/${filename}/ &
            rsync --delete-before --force -r ${EMPTY_DIR}/ ${CLIP_PAYH}/${filename}/ &
            mv ${csv} /nasdata/csv/finish &
        done
        echo "Waiting for all background tasks to finish..."
        wait
    fi
done
