#!/bin/bash

# 检查输入参数是否存在
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
  echo "Usage: $0 <data_direction> <output_direction> <start_stage> <end_stage> "
  exit 1
fi

# 初始化
export CUDA_VISIBLE_DEVICES=0
source ~/miniconda3/etc/profile.d/conda.sh

# 获取起始阶段和结束阶段参数
start_stage=$3
end_stage=$4
data_direction=$1
output_direction=$2

# 确保结束阶段不小于起始阶段
if [ "$end_stage" -lt "$start_stage" ]; then
  echo "End stage must be greater than or equal to start stage."
  exit 1
fi


# 阶段1
if [ "$start_stage" -le 1 ] && [ "$end_stage" -ge 1 ]; then
  echo "Running Stage 1..."
  conda activate audiopp
  cd /home/zhongjiafeng/repo/audio-preprocess/src
  python ./raw_extract.py \
    --input-dir $data_direction \
    --output-dir $output_direction
  if [ $? -ne 0 ]; then
    echo "Stage 1 failed. Exiting..."
    exit 1
  fi
fi

# 阶段2
if [ "$start_stage" -le 2 ] && [ "$end_stage" -ge 2 ]; then
  echo "Running Stage 2..."
  conda activate audiopp
  cd /home/zhongjiafeng/repo/audio-preprocess/src
  python ./data_check.py \
    --input-dir $output_direction \
    --mode 'text'
  if [ $? -ne 0 ]; then
    echo "Stage 2 failed. Exiting..."
    exit 1
  fi
fi

# 阶段3
if [ "$start_stage" -le 3 ] && [ "$end_stage" -ge 3 ]; then
  echo "Running Stage 3..."
  cd /home/zhongjiafeng/repo/audio-preprocess/fish_audio_preprocess/cli
  python ./g2p_transfrom.py --input-dir $output_direction --lang 'ar'
  if [ $? -ne 0 ]; then
    echo "Stage 3 failed. Exiting..."
    exit 1
  fi
fi


# 阶段4
if [ "$start_stage" -le 4 ] && [ "$end_stage" -ge 4 ]; then
  echo "Running Stage 4..."
  conda activate fish-speech
  cd /home/zhongjiafeng/repo/fish-speech
  python ./tools/vqgan/extract_vq.py $output_direction
  if [ $? -ne 0 ]; then
    echo "Stage 4 failed. Exiting..."
    exit 1
  fi
fi

# 阶段5
if [ "$start_stage" -le 5 ] && [ "$end_stage" -ge 5 ]; then
  echo "Running Stage 5..."
  conda activate audiopp
  cd /home/zhongjiafeng/repo/audio-preprocess/src
  python ./data_check.py \
  --input-dir $output_direction  \
  --mode "comple" 
  if [ $? -ne 0 ]; then
    echo "Stage 5 failed. Exiting..."
    exit 1
  fi
fi

# 阶段6
if [ "$start_stage" -le 6 ] && [ "$end_stage" -ge 6 ]; then
  echo "Running Stage 6..."
  conda activate fish-speech
  cd /home/zhongjiafeng/repo/fish-speech
  python ./tools/llama/build_dataset.py \
   --input $output_direction\
   --output /data/zhongjiafeng/Arabic/proto \
   --text-extension '.phe' \
   --tag $(basename "$output_direction")
  if [ $? -ne 0 ]; then
    echo "Stage 6 failed. Exiting..."
    exit 1
  fi
fi

echo "Completed stages up to $end_stage successfully!"