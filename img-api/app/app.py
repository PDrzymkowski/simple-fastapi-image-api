from fastapi import FastAPI
from .routes import router as image_router
app = FastAPI(title="Simple Image API")
app.include_router(image_router)
