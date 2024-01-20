from pydantic import BaseModel


class InferenceRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class InferenceResponse(BaseModel):
    setosa_probability: float
    versicolor_probability: float
    virginica_probability: float
    target: str
