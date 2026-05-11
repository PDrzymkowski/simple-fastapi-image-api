import boto3
from functools import lru_cache
from .config import settings

__all__ = ["upload_image_to_s3", "delete_image_from_s3"]


@lru_cache(maxsize=1)
def _get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )


def upload_image_to_s3(data: bytes, key: str, content_type: str) -> str:
    """Uploads image to AWS S3.

    :param data: Image data in bytes
    :param key: Key to AWS S3
    :param content_type: Type of content
    :return: Image URL in S3
    """
    _get_s3_client().put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return f"{settings.s3_url}/{key}"


def delete_image_from_s3(key: str) -> None:
    """Delete image from AWS S3.

    :param key: Key of the object to delete.
    """
    _get_s3_client().delete_object(Bucket=settings.s3_bucket_name, Key=key)