# Simple Image API

FastAPI service for uploading and retrieving images stored in S3.

## Stack

- Python 3.13, FastAPI, SQLAlchemy, PostgreSQL, S3, Pillow

## Running with Docker

```bash
cp .env.example .env  # fill in AWS_* vars
docker compose up --build
```

API available at `http://localhost:8000`. PostgreSQL starts automatically.

## Running locally

```bash
cp .env.example .env  # set DB_URL to your local postgres
poetry install
cd img-api && uvicorn app.app:app --reload
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `DB_URL` | PostgreSQL connection string |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `AWS_REGION` | AWS region (default: `eu-west-1`) |
| `S3_BUCKET_NAME` | S3 bucket for image storage |

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/images/upload` | Upload image (multipart: `file`, `title`, `width`, `height`) |
| `GET` | `/images/{id}` | Get image by ID |
| `GET` | `/images` | List images (`page`, `size`, `title` query params) |

## Tests

Requires a running PostgreSQL instance. S3 is mocked via [moto](https://github.com/getmoto/moto).

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