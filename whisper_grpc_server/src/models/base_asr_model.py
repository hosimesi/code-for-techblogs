from abc import abstractmethod

import numpy as np


class BaseASRModel:
    @abstractmethod
    def transcribe(
        self,
        audio_array: np.ndarray,
        language: str = "ja",
        task: str = "transcribe",
        without_timestamps: bool = True,
    ) -> str:
        raise NotImplementedError
