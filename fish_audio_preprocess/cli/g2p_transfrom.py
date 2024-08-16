import click
import torch
from pathlib import Path
from loguru import logger
from tqdm import tqdm
from fish_audio_preprocess.utils.file import list_files, split_list
from phonemizer import phonemize
from fish_audio_preprocess.utils.clean import clean_and_phonemize_text

@click.command()
@click.option(
    "--input-dir",
    default="/data/zhongjiafeng/Arabic/AFS",
    type=str,
)
@click.option(
    "--lang",
    help="Number of workers to use for processing, defaults to 2",
    default='ar',
    show_default=True,
    type=str,
)
@click.option(
    "--num-workers",
    help="Number of workers to use for processing, defaults to 2",
    default=2,
    show_default=True,
    type=int,
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Search recursively",
)

def g2p_transfrom(
    input_dir: str,
    lang : str,
    num_workers: int,
    recursive,
):
    """
    Predict the mean opinion score of speech.
    """
    input_dir = Path(input_dir)
    
    logger.info(f"Using {num_workers} workers for processing")
    logger.info(f"Input audio files in {input_dir}")

    text_files = list_files(input_dir, recursive=recursive)
    text_files = [file for file in text_files if file.suffix in ['.lab']]

    if len(text_files) == 0:
        logger.error(f"No text files found in {input_dir}.")
        return

    texts = []
    for file in tqdm(text_files, desc="Loading Text..."):
        text = file.read_text().strip()
        texts.append(text)

    phones = clean_and_phonemize_text(texts, lang=lang)
    
    skip = 0
    for phe, file in tqdm(zip(phones, text_files), desc="Writing phoneme..."):   
        phone_file = file.with_suffix('.phe')
        if not phone_file.exists(): 
            phone_file.write_text(phe) 
        else:
            skip += 1
    logger.info(f"g2p transfrom Done, writting {len(phones)} phoneme file, skip {skip}.")

if __name__ == '__main__':
    g2p_transfrom()