import json

from .consts import (
    BEDROCK_EMBEDDING_MODEL_ID,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_NORMALIZE,
)


def embed_text(text: str, bedrock_runtime_client) -> list[float]:
    body = {
        "inputText": text,
        "dimensions": EMBEDDING_DIMENSIONS,
        "normalize": EMBEDDING_NORMALIZE,
    }

    response = bedrock_runtime_client.invoke_model(
        modelId=BEDROCK_EMBEDDING_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response.get("body").read())
    return response_body["embedding"]
