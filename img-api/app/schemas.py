from uuid import UUID
from pydantic import BaseModel

class ImageResponse(BaseModel):
    id: UUID
    title: str
    url: str
    width: str
    height: str
