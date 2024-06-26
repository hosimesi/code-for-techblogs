import asyncio
import time
from enum import Enum

import ffmpeg
import grpc
import numpy as np
from google.protobuf.json_format import MessageToDict
from proto import inference_pb2, inference_pb2_grpc

SIGNED_INT16_MAX = 32768.0


class ASRModel(str, Enum):
    FASTER_WHISPER_LARGE_V3 = "faster-whisper-large-v3"
    FASTER_WHISPER_LARGE_V2 = "faster-whisper-large-v2"
    FASTER_DISTIL_WHISPER_LARGE_V3 = "faster-distil-whisper-large-v3"
    FASTER_DISTIL_WHISPER_LARGE_V2 = "faster-distil-whisper-large-v2"


def load_audio_file(audio_file_path: str, sampling_rate: int = 16000, channels: int = 1) -> list[np.ndarray]:
    # Create an input stream from the audio file
    input_stream = ffmpeg.input(audio_file_path)
    # Convert the audio to raw PCM data with a sample rate of `sampling_rate`
    output_stream = ffmpeg.output(input_stream, "pipe:", format="s16le", acodec="pcm_s16le", ar=sampling_rate)
    # Run the conversion and capture the raw PCM data
    pcm_data, _ = ffmpeg.run(output_stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
    # Convert the raw PCM data to a numpy array of 16-bit signed integers
    audio_data = np.frombuffer(pcm_data, np.int16)
    # Normalize the audio data to the range [-1.0, 1.0]
    audio_data = audio_data.astype(np.float32, order="C") / SIGNED_INT16_MAX
    # Split the audio data into separate channels
    return [audio_data]


async def transcribe(grpc_stub, audio_data, asr_model):
    start = time.time()
    request = inference_pb2.TranscribeRequest(audio_bytes=audio_data.tobytes(), target=asr_model)
    grpc_response = await grpc_stub.transcribe(request)
    response = MessageToDict(grpc_response).get("result", {})
    print(f"Response time: {time.time() - start} seconds")
    print(response)


async def main():
    audio_file_path = "samples/audio.wav"
    audio_data = load_audio_file(audio_file_path)

    grpc_channel = grpc.aio.insecure_channel("localhost:8080")
    grpc_stub = inference_pb2_grpc.ASRInferenceServerStub(grpc_channel)

    await transcribe(grpc_stub, audio_data[0], ASRModel.FASTER_WHISPER_LARGE_V2)
    await transcribe(grpc_stub, audio_data[0], ASRModel.FASTER_WHISPER_LARGE_V3)
    await transcribe(grpc_stub, audio_data[0], ASRModel.FASTER_DISTIL_WHISPER_LARGE_V3)
    await transcribe(grpc_stub, audio_data[0], ASRModel.FASTER_DISTIL_WHISPER_LARGE_V2)


if __name__ == "__main__":
    asyncio.run(main())
