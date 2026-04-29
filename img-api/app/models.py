import uuid
import pendulum
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    pass


class Image(BaseModel):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    created_at = Column(DateTime, default=lambda: pendulum.now(pendulum.UTC))

    key = Column(String, nullable=False)
    """Key to the file in the in external storage"""

    url = Column(String, nullable=False)

    title = Column(String, nullable=False)

    width = Column(Integer, nullable=False)

    height = Column(Integer, nullable=False)
