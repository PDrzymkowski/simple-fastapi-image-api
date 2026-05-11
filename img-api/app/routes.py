import logging
import uuid

from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException, Query
from sqlalchemy.orm.session import Session
from PIL import UnidentifiedImageError
from .db import get_db
from .models import Image
from .schemas import ImageResponse, ImageListResponse
from .services import upload_image_to_s3, delete_image_from_s3
from .utils import resize_image, detect_image_format

router = APIRouter(prefix="/images", tags=["images"])

logger = logging.getLogger(__name__)


@router.post("/upload", status_code=201, response_model=ImageResponse)
def upload_image(
    file: UploadFile = File(...),
    title: str = Form(...),
    width: int = Form(..., gt=0),
    height: int = Form(..., gt=0),
    db: Session = Depends(get_db),
):
    data = file.file.read()
    try:
        pil_format, content_type, extension = detect_image_format(data)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image data")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid image format")

    try:
        resized_data, actual_w, actual_h = resize_image(
            data=data, width=width, height=height, img_format=pil_format
        )
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image data")
    file_key = f"images/{uuid.uuid4()}.{extension}"

    try:
        url = upload_image_to_s3(
            data=resized_data, key=file_key, content_type=content_type
        )
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {e}")
        raise HTTPException(status_code=503, detail="Failed to upload file to S3")

    try:
        image = Image(
            title=title, key=file_key, url=url, width=actual_w, height=actual_h
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        return image
    except Exception as e:
        logger.error(f"DB commit failed, deleting S3 object {file_key}: {e}")
        delete_image_from_s3(file_key)
        raise HTTPException(status_code=500, detail="Failed to save image metadata")


@router.get("/{image_id}", response_model=ImageResponse)
def get_image(image_id: uuid.UUID, db: Session = Depends(get_db)):
    image = db.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
    else:
        return image


@router.get("", response_model=ImageListResponse)
def list_images(
    title: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Image)
    if title is not None:
        query = query.filter(Image.title.ilike(f"%{title}%"))
    total = query.count()
    offset = (page - 1) * size
    items = query.order_by(Image.created_at.desc()).offset(offset).limit(size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
    }