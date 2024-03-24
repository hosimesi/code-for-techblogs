import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.schemas.schema import ExtractConfig, ExtractedConfig
from src.utils.consts import (
    ARGO_GCS_BUCKET_NAME,
    ARTIFACTS_DIR,
    EXTRACTED_TEST_FILE_NAME,
    EXTRACTED_TRAIN_FILE_NAME,
    EXTRACTED_VALID_FILE_NAME,
    ORIGINAL_FILE_NAME,
    TRAIN_GCS_BUCKET_NAME,
)
from src.utils.gcp_controller import download_from_gcs, upload_to_gcs

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_options() -> argparse.Namespace:
    """Parse argument options."""

    description = """
    This script is extract step.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-c",
        "--config",
        type=ExtractConfig.parse_raw,
        help="""
            Configurations for extract step.
        """,
    )

    return parser.parse_args()


def main() -> None:
    logger.info("Extract step started.")

    args = load_options()
    config = args.config
    logger.info(f"config: {config}")

    gcs_path = config.name

    # Load the data
    download_from_gcs(ARGO_GCS_BUCKET_NAME, gcs_path, str(Path(ARTIFACTS_DIR, ORIGINAL_FILE_NAME)))

    # Read the data
    df = pd.read_csv(str(Path(ARTIFACTS_DIR, ORIGINAL_FILE_NAME)))

    # Extract data
    X = df.drop(["Survived", "PassengerId", "Cabin", "Name", "Ticket"], axis=1)
    y = df["Survived"]

    # divide the data into training, validation, and test data
    X_train, X_valid_test, y_train, y_valid_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

    # divide the training data into training and validation data
    X_valid, X_test, y_valid, y_test = train_test_split(
        X_valid_test, y_valid_test, test_size=0.5, random_state=42, stratify=y_valid_test
    )

    X_train["target"] = y_train
    extracted_train_df = X_train.copy()

    logger.info(f"Extracted train shape: {extracted_train_df.shape}")

    X_valid["target"] = y_valid
    extracted_valid_df = X_valid.copy()

    logger.info(f"Extracted valid shape: {extracted_valid_df.shape}")

    X_test["target"] = y_test
    extracted_test_df = X_test.copy()

    logger.info(f"Extracted test shape: {extracted_test_df.shape}")

    BASE_BLOB = "train_workflows"

    # Save the data and upload to GCS
    for extracted_df, file_name in zip(
        [extracted_train_df, extracted_valid_df, extracted_test_df],
        [EXTRACTED_TRAIN_FILE_NAME, EXTRACTED_VALID_FILE_NAME, EXTRACTED_TEST_FILE_NAME], strict=False,
    ):
        extracted_df.to_csv(str(Path(ARTIFACTS_DIR, file_name)), index=False)
        upload_to_gcs(TRAIN_GCS_BUCKET_NAME, str(Path(BASE_BLOB, file_name)), str(Path(ARTIFACTS_DIR, file_name)))
        logger.info(f"Uploaded {file_name} to GCS.")

    # Save the config
    extracted_config = ExtractedConfig(
        train_gcs_path=str(Path(BASE_BLOB, EXTRACTED_TRAIN_FILE_NAME)),
        valid_gcs_path=str(Path(BASE_BLOB, EXTRACTED_VALID_FILE_NAME)),
        test_gcs_path=str(Path(BASE_BLOB, EXTRACTED_TEST_FILE_NAME)),
    )

    # save artifact
    with open(str(Path(ARTIFACTS_DIR, "extracted_config.json")), "w") as f:
        json.dump(extracted_config.model_dump(), f, indent=4)

    logger.info("Extract step task fineshed.")


if __name__ == "__main__":
    main()
