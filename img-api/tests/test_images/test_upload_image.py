from unittest.mock import patch

from fastapi.testclient import TestClient

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