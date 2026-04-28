import logging
import uuid

from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm.session import Session

from db import get_db
from models import Image
from schemas import ImageResponse, ImageListResponse
from services import upload_image_to_s3

router = APIRouter(prefix="/images", tags=["images"])
SUPPORTED_FORMATS_MAP = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

logger = logging.getLogger(__name__)


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

    try:
        url = upload_image_to_s3(data=data, key=file_key, content_type=content_type)
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise HTTPException(status_code=503, detail="Failed to upload file to S3")
    else:
        image = Image(title=title, key=file_key, url=url, width=width, height=height)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image

@router.get("/{image_id}", response_model=ImageResponse)
def get_image(image_id: uuid.UUID, db: Session = Depends(get_db)):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
    else:
        return image


@router.get("", response_model=ImageListResponse)
def list_images(    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),):
    query = db.query(Image)

    total = query.count()
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
    }