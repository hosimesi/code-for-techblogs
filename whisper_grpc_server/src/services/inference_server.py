import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import grpc
import numpy as np
from src.models.model_info import ALL_MODELS
from src.proto import inference_pb2, inference_pb2_grpc
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def serve(bind_address: str) -> None:
    logger.info("Starting new server.")
    server = grpc.aio.server(
        ThreadPoolExecutor(max_workers=50),
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ],
    )
    inference_pb2_grpc.add_ASRInferenceServerServicer_to_server(ASRInferenceServer(), server)
    # Create health check and set its return value to SERVING.
    server.add_insecure_port(bind_address)
    logger.info("The server started successfully.")
    await server.start()
    await server.wait_for_termination()


class ASRInferenceServer(inference_pb2_grpc.ASRInferenceServerServicer):
    def __init__(self) -> None:
        """Initialization of all models used in the production environment."""
        self.models = ALL_MODELS

    async def _extract_audio_from_request(self, audio_bytes: bytes) -> np.ndarray:
        audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
        return audio_array

    async def transcribe(self, request: Any, context: Any) -> inference_pb2.TranscribeResponse:
        """Use a asr model to transcribe the audio data."""
        try:
            audio_array = await self._extract_audio_from_request(audio_bytes=request.audio_bytes)
        except Exception:
            logger.error(traceback.format_exc())

        target: str = request.target
        if target not in self.models:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"target not found: {target}")
            logger.error(f"target not found: {target}")
            return inference_pb2.TranscribeResponse()
        try:
            transcription = self.models[target].transcribe(audio_array=audio_array)
        except Exception:
            logger.error(traceback.format_exc())

        return inference_pb2.TranscribeResponse(result={target: inference_pb2.ASRResult(transcription=transcription)})
