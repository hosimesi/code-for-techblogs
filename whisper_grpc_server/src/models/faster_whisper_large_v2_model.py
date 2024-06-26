import os

import numpy as np
from faster_whisper import WhisperModel
from src.models.base_asr_model import BaseASRModel
from src.utils import consts
from src.utils.enums import ASRModel
from src.utils.logging import get_logger

logger = get_logger(__name__)


class FasterWhisperLargeV2Model(BaseASRModel):
    def __init__(
        self,
        device: str = "cpu",
        compute_type: str = "int8",
        cpu_threads: int = 2,
        num_workers: int = 2,
    ):
        dir_name = os.path.join(
            consts.PRETRAINED_MODEL_DIR, ASRModel.FASTER_WHISPER_LARGE_V2.value
        )
        self.model = WhisperModel(
            dir_name,
            device=device,
            compute_type=compute_type,
            cpu_threads=cpu_threads,
            num_workers=num_workers,
        )

    def transcribe(
        self,
        audio_array: np.ndarray,
        language: str = "ja",
        task: str = "transcribe",
        without_timestamps: bool = False,
    ) -> str:
        transcription = ""
        logger.info("Transcribing audio...")
        segments, info = self.model.transcribe(
            audio=audio_array,
            language=language,
            task=task,
            without_timestamps=without_timestamps,
            chunk_length=5,
        )
        logger.info("Transcribing now...")
        for segment in segments:
            logger.info(f"Transcription: {transcription}")
            transcription += segment.text
        return transcription
