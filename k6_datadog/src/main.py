import logging
import os
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    query: str


def get_model_and_tokenizer():
    try:
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        logger.info(f"デバイス: {device}. モデルのロードを開始します...")
        model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-2-2b-jpn-it",
            torch_dtype=torch.bfloat16,
            token=os.environ.get("HUGGINGFACE_HUB_TOKEN"),
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "google/gemma-2-2b-jpn-it",
            token=os.environ.get("HUGGINGFACE_HUB_TOKEN"),
        )
        model.to(device)
        logger.info("モデルのロードに成功しました")
        return model, tokenizer, device
    except Exception as e:
        raise RuntimeError(f"モデルのロードに失敗しました: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # モデルのロード
    app.state.model, app.state.tokenizer, app.state.device = get_model_and_tokenizer()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/generate/thread/")
async def generate_thread(query: QueryRequest):
    logger.info(f"リクエスト: {query}")
    try:
        inputs = app.state.tokenizer(query.query, return_tensors="pt").to(
            app.state.device
        )
        streamer = TextIteratorStreamer(app.state.tokenizer, skip_prompt=True)
        generation_kwargs = dict(
            inputs=inputs.input_ids,
            max_new_tokens=256,
            streamer=streamer,
            pad_token_id=app.state.tokenizer.eos_token_id,
        )

        import threading

        def generate_text():
            app.state.model.generate(**generation_kwargs)

        thread = threading.Thread(target=generate_text)
        thread.start()

        async def event_generator():
            try:
                for new_text in streamer:
                    logger.info(f"Response: {new_text}")
                    yield f"data: {new_text}\n\n"
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"ストリームの生成中にエラーが発生しました: {e}",
                )

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"応答の生成に失敗しました: {e}")


@app.post("/generate/")
async def generate(query: QueryRequest):
    logger.info(f"リクエスト: {query}")
    try:
        inputs = app.state.tokenizer(query.query, return_tensors="pt").to(
            app.state.device
        )
        streamer = TextIteratorStreamer(app.state.tokenizer, skip_prompt=True)
        generation_kwargs = dict(
            inputs=inputs.input_ids,
            max_new_tokens=256,
            streamer=streamer,
            pad_token_id=app.state.tokenizer.eos_token_id,
        )

        app.state.model.generate(**generation_kwargs)

        async def event_generator():
            try:
                for new_text in streamer:
                    logger.info(f"Response: {new_text}")
                    yield f"data: {new_text}\n\n"
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"ストリームの生成中にエラーが発生しました: {e}",
                )

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"応答の生成に失敗しました: {e}")


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
