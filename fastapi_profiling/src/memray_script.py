import logging
import os

import torch
from transformers import pipeline

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main(query: str):
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    logger.info(f"デバイス: {device}. Starting to load the model...")
    pipe = pipeline(
        "text-generation",
        model="google/gemma-2-2b-jpn-it",
        model_kwargs={"torch_dtype": torch.bfloat16},
        token=os.environ.get("HUGGINGFACE_HUB_TOKEN"),
        device=device,
    )
    logger.info("モデルのロードに成功しました")

    outputs = pipe(
        query,
        return_full_text=False,
        max_new_tokens=256,
    )
    assistant_response = outputs[0]["generated_text"].strip()
    return {"assistant_response": assistant_response}


if __name__ == "__main__":
    query = "こんにちは"
    response = main(query=query)
    logger.info(response)
