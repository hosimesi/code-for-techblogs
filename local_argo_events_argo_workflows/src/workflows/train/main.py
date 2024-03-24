import argparse
import logging
from pathlib import Path

import pandas as pd

from src.models.model import get_model_candidates
from src.schemas.schema import TransformedConfig
from src.services.evaluate import evaluate_model
from src.utils.consts import (
    ARTIFACTS_DIR,
    TRAIN_GCS_BUCKET_NAME,
    TRANSFORMED_TEST_FILE_NAME,
    TRANSFORMED_TRAIN_FILE_NAME,
    TRANSFORMED_VALID_FILE_NAME,
)
from src.utils.gcp_controller import download_from_gcs, upload_to_gcs

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_options() -> argparse.Namespace:
    """Parse argument options."""

    description = """
    This script is train step.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-c",
        "--config",
        type=TransformedConfig.parse_raw,
        help="""
            Configurations for train step.
        """,
    )

    return parser.parse_args()


def main() -> None:
    logger.info("Train step started.")

    args = load_options()
    config = args.config
    logger.info(f"config: {config}")

    # Load the data
    download_from_gcs(TRAIN_GCS_BUCKET_NAME, config.train_gcs_path, str(Path(ARTIFACTS_DIR, TRANSFORMED_TRAIN_FILE_NAME)))
    download_from_gcs(TRAIN_GCS_BUCKET_NAME, config.valid_gcs_path, str(Path(ARTIFACTS_DIR, TRANSFORMED_VALID_FILE_NAME)))
    download_from_gcs(TRAIN_GCS_BUCKET_NAME, config.test_gcs_path, str(Path(ARTIFACTS_DIR, TRANSFORMED_TEST_FILE_NAME)))

    # Extract data
    transformed_train_df = pd.read_csv(str(Path(ARTIFACTS_DIR, TRANSFORMED_TRAIN_FILE_NAME)))
    transformed_valid_df = pd.read_csv(str(Path(ARTIFACTS_DIR, TRANSFORMED_VALID_FILE_NAME)))
    transformed_test_df = pd.read_csv(str(Path(ARTIFACTS_DIR, TRANSFORMED_TEST_FILE_NAME)))

    # Train the model
    model = get_model_candidates(config.target_model_name)()
    is_hyperparameter_tuning = False

    if is_hyperparameter_tuning:
        model._fit_with_valid(
            transformed_train_df.drop("target", axis=1),
            transformed_train_df["target"],
            transformed_valid_df.drop("target", axis=1),
            transformed_valid_df["target"],
        )
    else:
        model.fit(transformed_train_df.drop("target", axis=1), transformed_train_df["target"])

    y_pred = model.predict(transformed_test_df.drop("target", axis=1))
    y_proba = model.predict_proba(transformed_test_df.drop("target", axis=1))

    # Metrics
    logloss, accuracy, precision, recall, auc = evaluate_model(y_pred, y_proba, transformed_test_df["target"])
    logger.info(f"Validation logloss: {logloss}, accuracy: {accuracy}, precision: {precision}, recall: {recall}, auc: {auc}")

    BASE_BLOB = Path(config.train_gcs_path).parent

    # Save the model
    model.save_model(str(Path(ARTIFACTS_DIR, f"{config.target_model_name}.pkl")))
    upload_to_gcs(
        TRAIN_GCS_BUCKET_NAME,
        str(Path(BASE_BLOB, f"{config.target_model_name}.pkl")),
        str(Path(ARTIFACTS_DIR, f"{config.target_model_name}.pkl")),
    )

    logger.info("Train step task fineshed.")


if __name__ == "__main__":
    main()
