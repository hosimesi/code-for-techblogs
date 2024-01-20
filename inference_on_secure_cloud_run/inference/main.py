
import logging
import os

import numpy as np
from fastapi import FastAPI, HTTPException, status
from inference.schemas.inference import InferenceRequest, InferenceResponse
from inference.services.model import get_model

app = FastAPI()
logger = logging.getLogger(__name__)
model = get_model(destination_file_name=os.path.join("inference", "artifacts", "model.pkl"))


@app.post("/inference/", status_code=status.HTTP_200_OK, response_model=InferenceResponse)
async def inference(
    request: InferenceRequest,
) -> InferenceResponse:
    try:
        data = np.array([request.sepal_length, request.sepal_width, request.petal_length, request.petal_width]).reshape(1, -1)
        proba = model.predict_proba(data)[0]
        target = model.predict(data)[0]
        target_map = {0: "setosa", 1: "versicolor", 2: "virginica"}
        return InferenceResponse(
            setosa_probability=proba[0],
            versicolor_probability=proba[1],
            virginica_probability=proba[2],
            target=target_map[target]
        )
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve)) from ve


@app.get("/")
async def health_check() -> dict[str, str]:
    logger.info("Health check")
    return {"Hello": "World"}
