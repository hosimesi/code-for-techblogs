from src.models import (
    FasterDistilWhisperLargeV2Model,
    FasterDistilWhisperLargeV3Model,
    FasterWhisperLargeV2Model,
    FasterWhisperLargeV3Model,
)
from src.models.base_asr_model import BaseASRModel
from src.utils.enums import ASRModel

ALL_MODELS: dict[ASRModel, BaseASRModel] = {
    ASRModel.FASTER_WHISPER_LARGE_V2: FasterWhisperLargeV2Model(device="cpu", compute_type="int8"),
    ASRModel.FASTER_WHISPER_LARGE_V3: FasterWhisperLargeV3Model(device="cpu", compute_type="int8"),
    ASRModel.FASTER_DISTIL_WHISPER_LARGE_V2: FasterDistilWhisperLargeV2Model(device="cpu", compute_type="int8"),
    ASRModel.FASTER_DISTIL_WHISPER_LARGE_V3: FasterDistilWhisperLargeV3Model(device="cpu", compute_type="int8"),
}
