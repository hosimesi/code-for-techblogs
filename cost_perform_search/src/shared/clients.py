from functools import lru_cache

import boto3
from botocore.config import Config

from .consts import AWS_PROFILE, AWS_REGION


@lru_cache(maxsize=1)
def _session() -> boto3.Session:
    profile = (AWS_PROFILE or "").strip()
    if profile:
        return boto3.Session(profile_name=profile, region_name=AWS_REGION)
    return boto3.Session(region_name=AWS_REGION)


def create_client(service_name: str) -> boto3.client:
    return _session().client(
        service_name=service_name,
        config=Config(retries={"max_attempts": 10, "mode": "standard"}),
    )
