import cProfile
import logging
import os
import uuid

import torch
import yappi
from fastapi import Depends, FastAPI, HTTPException, Request
from memory_profiler import profile
from pydantic import BaseModel
from transformers import pipeline

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    query: str


def get_pipeline():
    try:
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
        return pipe
    except Exception as e:
        raise RuntimeError(f"モデルのロードに失敗しました: {e}")


app = FastAPI()


@app.post("/generate/")
@profile
def generate(query: QueryRequest, pipe=Depends(get_pipeline)):
    try:
        outputs = pipe(
            query.query,
            return_full_text=False,
            max_new_tokens=256,
        )
        assistant_response = outputs[0]["generated_text"].strip()
        return {"assistant_response": assistant_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"応答の生成に失敗しました: {e}")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.middleware("http")
async def cprofile_middleware(request: Request, call_next):
    profile_target_paths = ["/generate/"]

    if request.url.path in profile_target_paths:
        request_id = uuid.uuid4()
        profile_filename = f"profile_{request_id}.pstats"

        profiler = cProfile.Profile()
        profiler.enable()

        response = await call_next(request)

        profiler.disable()
        profiler.dump_stats(profile_filename)

        return response
    else:
        response = await call_next(request)
        return response


yappi.set_clock_type("cpu")


@app.middleware("http")
async def yappi_middleware(request: Request, call_next):
    profile_target_paths = ["/generate/"]

    if request.url.path in profile_target_paths:
        request_id = uuid.uuid4()
        func_profile_filename = f"func_profile_{request_id}.pstats"
        thread_profile_filename = f"thread_profile_{request_id}.pstats"

        yappi.clear_stats()
        yappi.start()
        response = await call_next(request)

        yappi.stop()
        func_stats = yappi.get_func_stats()
        func_stats.print_all()
        func_stats.save(func_profile_filename, type="pstat")

        thread_stats = yappi.get_thread_stats()
        thread_stats.print_all()
        with open(thread_profile_filename, "w") as f:
            thread_stats.print_all(out=f)
        return response
    else:
        response = await call_next(request)
        return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
