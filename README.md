# Simple Image API

FastAPI service for uploading and retrieving images stored in S3.

## Stack

- Python 3.13, FastAPI, SQLAlchemy, PostgreSQL, S3, Pillow

## Setup

```bash
cp .env.example .env  # fill in DB_URL, AWS_* vars
poetry install
uvicorn app.app:app --reload
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/images/upload` | Upload image (multipart: `file`, `title`, `width`, `height`) |
| `GET` | `/images/{id}` | Get image by ID |
| `GET` | `/images` | List images (`page`, `size`, `title` query params) |

## Tests

Requires a running PostgreSQL instance. Tests use [moto](https://github.com/getmoto/moto) to mock AWS S3.

```bash
# create test DB (first time only)
createdb test

# run all tests
cd img-api && pytest

# run specific suite
pytest tests/test_images/test_upload_image.py

# with output
pytest -v
```
