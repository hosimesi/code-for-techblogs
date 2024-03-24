import argparse
import json
import logging
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OrdinalEncoder, StandardScaler

from src.schemas.schema import ExtractedConfig, TransformedConfig
from src.utils.consts import (
    ARTIFACTS_DIR,
    CATEGORICAL_FEATURES,
    EXTRACTED_TEST_FILE_NAME,
    EXTRACTED_TRAIN_FILE_NAME,
    EXTRACTED_VALID_FILE_NAME,
    NUMERICAL_FEATURES,
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
    This script is transform step.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-c",
        "--config",
        type=ExtractedConfig.parse_raw,
        help="""
            Configurations for transform step.
        """,
    )

    return parser.parse_args()


def main() -> None:
    logger.info("Transform step started.")

    args = load_options()
    config = args.config
    logger.info(f"config: {config}")

    # Load the data
    download_from_gcs(TRAIN_GCS_BUCKET_NAME, config.train_gcs_path, str(Path(ARTIFACTS_DIR, EXTRACTED_TRAIN_FILE_NAME)))
    download_from_gcs(TRAIN_GCS_BUCKET_NAME, config.valid_gcs_path, str(Path(ARTIFACTS_DIR, EXTRACTED_VALID_FILE_NAME)))
    download_from_gcs(TRAIN_GCS_BUCKET_NAME, config.test_gcs_path, str(Path(ARTIFACTS_DIR, EXTRACTED_TEST_FILE_NAME)))

    # Preprocessing for categorical columns
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),  # fill missing values with most frequent ones
            ("to_string", FunctionTransformer(lambda x: x.astype(str))),  # convert to string
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
            ),  # encode to numerical values
        ]
    )

    # Preprocessing for numerical columns
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),  # fill missing values with median
            ("scaler", StandardScaler()),  # standard scaling
        ]
    )

    # Define preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    BASE_BLOB = Path(config.train_gcs_path).parent

    for extracted_file_name, transformed_file_name in zip(
        [EXTRACTED_TRAIN_FILE_NAME, EXTRACTED_VALID_FILE_NAME, EXTRACTED_TEST_FILE_NAME],
        [TRANSFORMED_TRAIN_FILE_NAME, TRANSFORMED_VALID_FILE_NAME, TRANSFORMED_TEST_FILE_NAME], strict=False,
    ):
        extracted_df = pd.read_csv(str(Path(ARTIFACTS_DIR, extracted_file_name)))

        logger.info(f"Loaded {extracted_file_name} shape: {extracted_df.shape}")

        extracted_features = extracted_df.drop("target", axis=1)
        extracted_target = extracted_df["target"]

        if extracted_file_name == EXTRACTED_TRAIN_FILE_NAME:
            transformed = preprocessor.fit_transform(extracted_features)
        else:
            transformed = preprocessor.transform(extracted_features)

        transformed_df = pd.DataFrame(transformed, columns=extracted_features.columns)
        transformed_df["target"] = extracted_target.copy()

        transformed_df.to_csv(str(Path(ARTIFACTS_DIR, transformed_file_name)), index=False)
        upload_to_gcs(
            TRAIN_GCS_BUCKET_NAME, str(Path(BASE_BLOB, transformed_file_name)), str(Path(ARTIFACTS_DIR, transformed_file_name))
        )
        logger.info(f"Uploaded {transformed_file_name} to GCS.")

    # Save the config
    transformed_configs = []
    for target_model_name in ("lr", "lgbm"):
        transformed_configs.append(
            TransformedConfig(
                train_gcs_path=str(Path(BASE_BLOB, TRANSFORMED_TRAIN_FILE_NAME)),
                valid_gcs_path=str(Path(BASE_BLOB, TRANSFORMED_VALID_FILE_NAME)),
                test_gcs_path=str(Path(BASE_BLOB, TRANSFORMED_TEST_FILE_NAME)),
                target_model_name=target_model_name,
            ).model_dump()
        )

    # save artifact
    with open(str(Path(ARTIFACTS_DIR, "transformed_configs.json")), "w") as f:
        json.dump(transformed_configs, f, indent=4)

    logger.info("Transform step task fineshed.")


if __name__ == "__main__":
    main()
