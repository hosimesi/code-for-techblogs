from src.models.lgbm import LocalLGBM
from src.models.lr import LocalLogisticRegression

model_candidtates = {
    "lr": LocalLogisticRegression,
    "lgbm": LocalLGBM,
}


def get_model_candidates(model_name: str):
    return model_candidtates[model_name]
