import os
import re
import subprocess as sp
import shutil
import click
from pathlib import Path
from tqdm import tqdm
from loguru import logger
def find_max_suffix_number(directory):
    max_number = -1
    pattern = re.compile(r'_(\d+)\.')

    for root, _, files in os.walk(directory):
        for file in files:
            match = pattern.search(file)
            if match:
                number = int(match.group(1))
                if number > max_number:
                    max_number = number

    return max_number

def move_audio_files(source_dir, target_dir):
    audio_extensions = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a')

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    idx = find_max_suffix_number(target_dir)

    # 遍历源目录及其子目录中的所有文件
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(audio_extensions):
                source_path = os.path.join(root, file)
                target_path = os.path.join(target_dir, f'afs_ar_{idx:08}.wav')
                print(f"正在移动: {source_path} 到 {target_path}")
                shutil.move(source_path, target_path)
                idx += 1


@click.command()
@click.option(
    "--input-dir",
    default="/data/zhongjiafeng/Arabic/AFS",
    type=str,
)
@click.option(
    "--output-dir",
    default=None,
    type=str,
)
def main(input_dir, output_dir):
    logger.info(f"Start process raw data from {input_dir}.")
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    meta_list = list(input_dir.glob('**/*.list'))
    idx = find_max_suffix_number(output_dir)
    skip = 0
    for i, meta in enumerate(meta_list):
        with meta.open('r', encoding='utf-8') as fp:
            lines = fp.readlines()
        for line in tqdm(lines, desc=f"{i}/{len(meta_list)} meta:"):
            audio_path, _, _, text = line.strip().split('|')
            audio_path = Path(audio_path)
            text = text.strip()

            src_audio_path = input_dir / '/'.join(str(audio_path).split('/')[-3:])
            tgt_audio_path = output_dir / f'afs_ar_{idx:08}.wav'
            text_path = tgt_audio_path.with_suffix('.lab')
            
            if src_audio_path.exists():
                command = ['cp',f'{src_audio_path}',f'{tgt_audio_path}']
                sp.check_call(command, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                text_path.write_text(text)
                idx += 1
            else:
                print(f"File {str(src_audio_path)} not found skip.")
                skip += 1
    
    logger.info(f"Total process audio {idx + 1}, skip {skip}.")
            

if __name__ == '__main__':
    main()