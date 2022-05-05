import os
from base64 import b64decode
from functools import lru_cache
from typing import Optional

import boto3


@lru_cache
def decrypt(environ_key: str, username: Optional[str] = None) -> str:
    suffix = f"__{username}" if username else ""
    encrypted = os.environ[environ_key + suffix]
    return (
        boto3.client("kms")
        .decrypt(CiphertextBlob=b64decode(encrypted))["Plaintext"]  # needs permission
        .decode("utf-8")
    )
