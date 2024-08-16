import os 
import re
import subprocess
import random
import shutil
import click
from pathlib import Path
from tqdm import tqdm
from loguru import logger
from glob import glob


_ARABIC_UNICODE_RANGES = [
    (0x0600, 0x06FF),  # Arabic
    (0x0750, 0x077F),  # Arabic Supplement
    (0x08A0, 0x08FF),  # Arabic Extended-A
    (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
    (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
    (0x1EE00, 0x1EEFF) # Arabic Mathematical Alphabetic Symbols
]

def is_arabic_char(char):
    return any(start <= ord(char) <= end for start, end in _ARABIC_UNICODE_RANGES)

def contains_only_arabic(text):
    for char in text:
        if not (is_arabic_char(char) or char.isspace()):
            return False
    return True

def remove_punctuation(text):
    # 定义所有语言的标点符号
    punctuations = r""".,!?:;—()\[\]{}'\"…`~。，！？：；、‘’“”《》（）……——「」『』〈〉«»․‥—―¡¿،؛؟ㆍ"""
    # 使用正则表达式去除标点符号
    cleaned_text = re.sub(f"[{re.escape(punctuations)}]", "", text)
    return cleaned_text

def check_lab_files(directory):
    logger.info("Start checking if the text contains non-Arabic characters.")
    dirty_data = []
    for root, dirs, files in os.walk(directory):
        for file in tqdm(files, desc="Checking..."):
            if file.endswith(".lab"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = remove_punctuation(content)
                    if not contains_only_arabic(content):
                        dirty_data.append(os.path.join(root, file))

    if len(dirty_data) == 0:
        logger.info("No dirty data, text Checking finish.")
        exit(0)

    logger.info(f"Remove {len(dirty_data)}/ total: {len(files)}")
    key = input("Are you sure to remove the dirty sample?(Y/N)").lower()
    if key == 'y' or key == "yes":
        key = input("be sure again?(Y/N)").lower()
        if key == 'y' or key == "yes":  
            for file in tqdm(dirty_data, desc="Remove dirty data..."):
                file = Path(file)
                subprocess.run(['rm', file.with_suffix('.lab')], check=True)
                subprocess.run(['rm', file.with_suffix('.wav')], check=True)
            logger.info(f"Remove {len(dirty_data)} sample, text Check finis.")
    else:
        logger.info("Nothing change, text Check finish.")

def check_all_files_avaliable(directory, suffix_list=None):
    if suffix_list is None:   # default
        suffix_list = ['.phe', '.npy']

    logger.info(f"Checking Data Integrity: {' '.join(suffix_list)}")
    names = []
    for file in tqdm(glob(f"{directory}/**/**.*", recursive=True), desc=f"Reading {directory}..."):
        file = Path(file)
        names.append(file.parent / file.stem)

    names = list(set(names))
    wav_miss = []
    other_miss = []
    reomve_nums = 0
    for name in tqdm(names, desc="Checking..."):
        if not name.with_suffix('.wav').exists(): 
            wav_miss.append(name)
            logger.info(name)
        else:
            for suffix in suffix_list:
                if not name.with_suffix(suffix).exists():
                    other_miss.append(name)
                    break

    if len(wav_miss) == 0 and len(other_miss) == 0:
        logger.info("No dirty data, text Checking finish.")
        exit(0)

    logger.info(f"Wav file loss {len(wav_miss)}/ other file loss {len(other_miss)}/ total: {len(names)}")
    key = input(f"Are you sure to remove file with wav file <loss {len(wav_miss)}/ total: {len(names)}>? (Y/N)").lower()
    if key == 'Y' or key == "YES":
        key = input("Be sure again(Y/N).").lower()
        if key == 'Y' or key == "YES":  
            for name in tqdm(wav_miss,desc="Removing..."):
                subprocess.run(f'rm {str(name)}.*', shell=True, check=True)
                reomve_nums += 1
            logger.info(f"Remove operation finish, total remove {len(wav_miss)}.")
    else:
        logger.info("Nothing change.")

@click.command()
@click.option(
    "--input-dir",
    default="/data/zhongjiafeng/Arabic/AFS",
    type=str,
)
@click.option(
    "--mode",
    default='text',
    type=str,
)
def main(
    input_dir: str,
    mode: str,
):
    if mode == 'text':
        check_lab_files(input_dir)
    elif mode == 'comple':
        check_all_files_avaliable(input_dir)
    else:
        logger.info(f"mode param <{mode}> is unvalid.")


if __name__ == '__main__':
    main()
