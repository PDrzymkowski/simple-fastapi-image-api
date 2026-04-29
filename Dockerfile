FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.3.2
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --only main
COPY img-api/ ./

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]