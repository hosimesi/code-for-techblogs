import logging
import pickle
from functools import lru_cache

from google.cloud import storage
from inference.shared.consts import GCS_BUCKET_NAME, GCS_PATH

logger = logging.getLogger(__name__)

def download_from_gcs(destination_file_name: str) -> None:
    """Download model from GCS bucket."""
    client = storage.Client()
    try:
        bucket = client.get_bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(GCS_PATH)
        blob.download_to_filename(destination_file_name)
    except Exception as e:
        raise ValueError(f"Failed to download model from GCS: {e}") from e


@lru_cache(maxsize=3)
def get_model(destination_file_name: str) -> object:
    """Get model from GCS bucket."""
    download_from_gcs(destination_file_name)

    logger.info(f"Downloaded model from GCS to {destination_file_name}")

    with open(destination_file_name, "rb") as f:
        model = pickle.load(f)

    logger.info("Loaded model")
    return model
