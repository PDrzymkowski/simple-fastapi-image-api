import uuid

from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException
from sqlalchemy.orm.session import Session

from db import get_db
from models import Image
from schemas import ImageResponse

router = APIRouter(prefix="/images", tags=["images"])
SUPPORTED_FORMATS_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}


@router.post("/upload", status_code=201, response_model=ImageResponse)
def upload_image(
        file: UploadFile = File(...),
        title: str = Form(...),
        width: int = Form(..., gt=0),
        height: int = Form(..., gt=0),
        db: Session = Depends(get_db),
):
    content_type = file.content_type
    try:
        extension = SUPPORTED_FORMATS_MAP[content_type]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid image format")

    data = file.file.read()
    file_key = f"images/{uuid.uuid4()}.{extension}"

    url = "mock"  # TODO upload img to AWS
    image = Image(title=title, key=file_key, url=url, width=width, height=height)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image
