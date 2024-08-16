import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import subprocess as sp

import click
import torch
from pathlib import Path
from loguru import logger
from tqdm import tqdm

from fish_audio_preprocess.utils.file import AUDIO_EXTENSIONS, list_files, split_list
def replace_lastest(string, old, new):
    return string[::-1].replace(old[::-1], new[::-1], 1)[::-1]

@click.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--output_dir", 
    default = None,
    type=click.Path(exists=True, file_okay=False),
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
    default=False,
    help="Search recursively",
)
@click.option(
    "--model-type",
    help="ASR model type (funasr or whisper)",
    default="UTMOS",
    show_default=True,
)
@click.option(
    "--threshold",
    help="Threshold to filte speech",
    default=4.0,
    show_default=True,
)
@click.option(
    "--move/--remove",
    help="Threshold to filte speech",
    default=False,
)
def mos_predict(
    input_dir: str,
    output_dir: str,
    num_workers: int,
    recursive: bool,
    model_type,
    threshold: float = None,
    move: bool = True,

):
    """
    Predict the mean opinion score of speech.
    """
    if move and not output_dir is None:
        raise ValueError
     
    output_dir = Path(output_dir) if not output_dir is None else None 
    input_dir = Path(input_dir)
    scores_file = input_dir / f"{model_type}_score.txt"

    if not scores_file.exists():
        from fish_audio_preprocess.utils.mos_predict import batch_mos_predict

        logger.info("Socre file is not found, to predict MOS.")
        # predict mos scores
        if model_type == "utmos":
            logger.info("Using UTMOS model as default")

        if not torch.cuda.is_available():
            logger.warning(
                "CUDA is not available, using CPU. This will be slow and even this script can not work. "
                "To speed up, use a GPU enabled machine or install torch with cuda builtin."
            )
        logger.info(f"Using {num_workers} workers for processing")
        logger.info(f"Predict audio files in {input_dir}")

        audio_files = list_files(input_dir, recursive=recursive)
        audio_files = [str(file) for file in audio_files if file.suffix in AUDIO_EXTENSIONS]

        if len(audio_files) == 0:
            logger.error(f"No audio files found in {input_dir}.")
            return

        # 按照 num workers 切块
        chunks = split_list(audio_files, num_workers)

        with ProcessPoolExecutor(mp_context=mp.get_context("spawn")) as executor:
            tasks = []
            for chunk in chunks:
                tasks.append(
                    executor.submit(
                        batch_mos_predict,
                        files=chunk,
                        model_type=model_type,
                        pos=len(tasks),
                    )
                )
            results = {}
            for task in tasks:
                ret = task.result()
                for res in ret.keys():
                    results[res] = ret[res]

            logger.info("Output to MOS score file")
            
        sorted_res = sorted(results.items(), key=lambda item: item[1], reverse=True)
        with open(scores_file, 'w', encoding="utf-8") as fp:
            for file, score in tqdm(sorted_res):
                fp.write(f"{Path(file).name}|{score:05f}\n")
    else:
        logger.info("Socre file has created, please check.")

    if not threshold is None:
        if not move:
            logger.info(f"Start filtering sample with score < {threshold}.")
            name_scores_pair = scores_file.open('r').readlines()
            name_scores_pair = [line.split('|') for line in name_scores_pair]
        
            filter_file = [f for f, s in name_scores_pair if float(s) < threshold]
            for file in tqdm(filter_file, desc="Remove lower mos samples ..."):
                ori_file = input_dir / file
                command = f'rm {str(ori_file.with_suffix(".*"))}'
                sp.check_call(command, shell=True, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

            logger.info("Done.")
            logger.info(f"Total remove {len(filter_file)} samples.")
        else:
            logger.info(f"Start filtering sample with score > {threshold}.")
            name_scores_pair = scores_file.open('r').readlines()
            name_scores_pair = [line.split('|') for line in name_scores_pair]
        
            filter_file = [f for f, s in name_scores_pair if float(s) > threshold]
            for file in tqdm(filter_file, desc="Extracting higher mos samples ..."):
                ori_file = input_dir / file
                new_file = output_dir / Path(file).name
                command = ['cp', str(ori_file), str(new_file)]
                sp.check_call(command, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

            logger.info("Done.")
            logger.info(f"Total extract {len(filter_file)} samples.")

if __name__ == '__main__':
    mos_predict()