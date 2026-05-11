import io
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
from fastapi.testclient import TestClient
from PIL import Image as PilImage

from app.app import app
from app.db import get_db


def test_400__unsupported_format(client):
    response = client.post(
        "/images/upload",
        data={"title": "Bad", "width": "50", "height": "50"},
        files={"file": ("file.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400


def test_invalid_image_data__400(client):
    response = client.post(
        "/images/upload",
        data={"title": "Corrupt", "width": "50", "height": "50"},
        files={"file": ("corrupt.jpg", b"not-image-bytes", "image/jpeg")},
    )
    assert response.status_code == 400


def test_422__missing_title(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"width": "50", "height": "50"},
        files={"file": ("photo.jpg", make_image_file(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_422__title_too_long(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"title": "a" * 256, "width": "50", "height": "50"},
        files={"file": ("photo.jpg", make_image_file(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_422__width_exceeds_max(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"title": "Too wide", "width": "4097", "height": "50"},
        files={"file": ("photo.jpg", make_image_file(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_422__height_exceeds_max(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"title": "Too tall", "width": "50", "height": "4097"},
        files={"file": ("photo.jpg", make_image_file(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_413__file_too_large(client):
    big_data = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/images/upload",
        data={"title": "Big", "width": "50", "height": "50"},
        files={"file": ("big.jpg", big_data, "image/jpeg")},
    )
    assert response.status_code == 413


def test_422__missing_dimensions(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"title": "No dims"},
        files={"file": ("photo.jpg", make_image_file(), "image/jpeg")},
    )
    assert response.status_code == 422


def test_500__s3_cleanup_on_db_failure(db, s3, make_image_file):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with patch.object(db, "commit", side_effect=Exception("DB failure")):
            with TestClient(app) as test_client:
                response = test_client.post(
                    "/images/upload",
                    data={"title": "Test", "width": "50", "height": "50"},
                    files={"file": ("photo.jpg", make_image_file(), "image/jpeg")},
                )
        assert response.status_code == 500
        objects = s3.list_objects(Bucket="test-bucket")
        assert "Contents" not in objects
    finally:
        app.dependency_overrides.clear()


def test_503__s3_upload_failure(client, make_image_file):
    with patch("app.routes.upload_image_to_s3", side_effect=ClientError({}, "PutObject")):
        response = client.post(
            "/images/upload",
            data={"title": "S3 fail", "width": "50", "height": "50"},
            files={"file": ("photo.jpg", make_image_file(), "image/jpeg")},
        )
    assert response.status_code == 503


@pytest.mark.parametrize(
    "img_format, content_type, filename",
    [
        ("PNG", "image/png", "photo.png"),
        ("WEBP", "image/webp", "photo.webp"),
        ("GIF", "image/gif", "photo.gif"),
    ],
)
def test_201__supported_formats(client, img_format, content_type, filename):
    buf = io.BytesIO()
    PilImage.new("RGB", (100, 100), color="blue").save(buf, format=img_format)
    buf.seek(0)
    response = client.post(
        "/images/upload",
        data={"title": "Format test", "width": "50", "height": "50"},
        files={"file": (filename, buf, content_type)},
    )
    assert response.status_code == 201


def test_201__happy_path(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"title": "My Photo", "width": "50", "height": "50"},
        files={"file": ("photo.jpg", make_image_file(100, 100), "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "My Photo"
    assert body["width"] <= 50
    assert body["height"] <= 50
    assert body["url"].startswith("https://")
    assert "id" in body


def test_201__stored_dimensions_match_resized_file(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"title": "Dims check", "width": "40", "height": "30"},
        files={"file": ("photo.jpg", make_image_file(200, 100), "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["width"] <= 40
    assert body["height"] <= 30
    assert body["width"] * 100 // body["height"] == 200 * 100 // 100