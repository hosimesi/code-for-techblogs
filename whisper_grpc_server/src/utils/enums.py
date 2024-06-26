from enum import Enum


class ASRModel(str, Enum):
    FASTER_WHISPER_LARGE_V3 = "faster-whisper-large-v3"
    FASTER_WHISPER_LARGE_V2 = "faster-whisper-large-v2"
    FASTER_DISTIL_WHISPER_LARGE_V3 = "faster-distil-whisper-large-v3"
    FASTER_DISTIL_WHISPER_LARGE_V2 = "faster-distil-whisper-large-v2"
