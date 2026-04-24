import pytest
import io
from PIL import Image as PilImage

__all__ = ["make_image_file", "sample_image"]

def make_image_file(width: int = 100, height: int = 100) -> io.BytesIO:
    buf = io.BytesIO()
    PilImage.new("RGB", (width, height), color="red").save(buf, format="JPEG")
    buf.seek(0)
    return buf

@pytest.fixture
def sample_image(client):
    response = client.post(
        "/images",
        data={"title": "Sample Image", "width": "50", "height": "50"},
        files={"file": ("sample.jpg", make_image_file(), "image/jpeg")},
    )
    assert response.status_code == 201
    return response.json()
