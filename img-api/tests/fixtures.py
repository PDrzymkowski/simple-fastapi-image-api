import pytest
import io
from PIL import Image as PilImage

__all__ = ["make_image_file", "sample_image"]

@pytest.fixture()
def make_image_file():
    def _make_image_file(width: int = 100, height: int = 100) -> io.BytesIO:
        buf = io.BytesIO()
        PilImage.new("RGB", (width, height), color="red").save(buf, format="JPEG")
        buf.seek(0)
        return buf

    yield _make_image_file

@pytest.fixture
def sample_image(client, make_image_file):
    response = client.post(
        "/images/upload",
        data={"title": "Sample Image", "width": "50", "height": "50"},
        files={"file": ("sample.jpg", make_image_file(), "image/jpeg")},
    )
    assert response.status_code == 201
    return response.json()
