import os 
import random
import shutil
import click
from loguru import logger
@click.command()
@click.option(
    "--input_dir",
    default=None,
    type=str,
)
@click.option(
    "--output_dir",
    default=None,
    type=str,
)
@click.option(
    "--k",
    default=10,
    type=int,
)
def main(input_dir, output_dir, k):
    # 获取目录中所有的文件列表
    all_files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    
    # 过滤语音文件的扩展名（如 .wav, .mp3, .flac 等）
    audio_extensions = ['.wav', '.mp3', '.flac']  # 可以根据需要添加更多扩展名
    audio_files = [f for f in all_files if os.path.splitext(f)[1].lower() in audio_extensions]
    
    # 检查是否有足够的文件供抽样
    if len(audio_files) < k:
        raise ValueError(f"目录中的语音文件数量不足。仅找到 {len(audio_files)} 个语音文件。")
    
    # 随机抽取 k 个语音文件
    sampled_files = random.sample(audio_files, k)
    
    # 创建目标文件夹（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 复制语音文件及其对应的文本文件
    for audio_file in sampled_files:
        # 复制语音文件
        audio_source_path = os.path.join(input_dir, audio_file)
        audio_target_path = os.path.join(output_dir, audio_file)
        shutil.copy(audio_source_path, audio_target_path)
        
        # 寻找并复制对应的文本文件（假设文本文件的扩展名为 .txt，且与语音文件同名）
        text_file = os.path.splitext(audio_file)[0] + '.lab'
        text_source_path = os.path.join(input_dir, text_file)
        text_target_path = os.path.join(output_dir, text_file)
        
        if os.path.exists(text_source_path):
            shutil.copy(text_source_path, text_target_path)
        else:
            logger.info(f"warning: not Found {text_file}. skip.")

if __name__ == '__main__':
    main()