from pathlib import Path
from typing import Literal

from loguru import logger
from tqdm import tqdm

import torch
import librosa

MOSModelType = Literal["UTMOS"]


def batch_mos_predict(
    files: list[Path],
    model_type: MOSModelType,
    pos: int,
):
    results = {}
    if model_type == "UTMOS":
        logger.info(f"Loading {model_type} model.")
        predictor = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
        for file in tqdm(files, position=pos):
            wave, sr = librosa.load(file, sr=None, mono=True)
            result = predictor(torch.from_numpy(wave).unsqueeze(0), sr)
            results[str(file)] = result.item()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    return results
