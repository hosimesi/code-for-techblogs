import logging
import os

from google.cloud import storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def download_from_gcs(bucket_name: str, blob_name: str, save_path: str) -> None:
    logger.info(f"Downloading {blob_name} from {bucket_name} to {save_path}.")
    storage_client = storage.Client(os.getenv("GCP_PROJECT_ID"))
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(save_path)
    logger.info(f"Blob {blob_name} downloaded to {save_path}.")


def upload_to_gcs(bucket_name: str, blob_name: str, file_path: str) -> None:
    logger.info(f"Uploading {file_path} to {blob_name} in {bucket_name}.")
    storage_client = storage.Client(os.getenv("GCP_PROJECT_ID"))
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    logger.info(f"File {file_path} uploaded to {blob_name} in {bucket_name}.")
