from pydantic import BaseModel


class ExtractConfig(BaseModel):
    kind: str
    id: str
    selfLink: str
    name: str
    bucket: str
    generation: str
    metageneration: str
    contentType: str
    timeCreated: str
    updated: str
    storageClass: str
    timeStorageClassUpdated: str
    size: str
    md5Hash: str
    mediaLink: str
    contentLanguage: str
    crc32c: str
    etag: str


class ExtractedConfig(BaseModel):
    train_gcs_path: str
    valid_gcs_path: str
    test_gcs_path: str


class TransformedConfig(BaseModel):
    train_gcs_path: str
    valid_gcs_path: str
    test_gcs_path: str
    target_model_name: str
