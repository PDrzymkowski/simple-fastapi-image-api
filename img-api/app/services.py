import boto3
from .config import settings

__all__ = ["upload_image_to_s3", "delete_image_from_s3"]

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)


def upload_image_to_s3(data: bytes, key: str, content_type: str) -> str:
    """
    Uploads image to AWS S3.

    :param data: Image data in bytes
    :param key: Key to AWS S3
    :param content_type: Type of content
    :return: Image URL in S3
    """
    s3.put_object(
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
    s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)
