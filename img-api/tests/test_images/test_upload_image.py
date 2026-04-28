def test_400__upload_unsupported_format(client):
    response = client.post(
        "/images/upload",
        data={"title": "Bad", "width": "50", "height": "50"},
        files={"file": ("file.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400


def test_400__unsupported_format(client):
    response = client.post(
        "/images/upload",
        data={"title": "Corrupt", "width": "50", "height": "50"},
        files={"file": ("corrupt.csv", b"not-image-bytes", "text/csv")},
    )
    assert response.status_code == 400


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
