from uuid import UUID
from pydantic import BaseModel

class ImageResponse(BaseModel):
    id: UUID
    title: str
    url: str
    width: int
    height: int

class ImageListResponse(BaseModel):
    items: list[ImageResponse]
    total: int
    page: int
    size: int