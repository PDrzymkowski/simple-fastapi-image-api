import os
import pytest
from models import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_REGION", "eu-east-1")
os.environ.setdefault("S3_BUCKET_NAME", "test-bucket")

TEST_DB_URL = os.environ["DATABASE_URL"]

@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_engine(TEST_DB_URL)
    BaseModel.metadata.create_all(engine)
    yield engine
    BaseModel.metadata.drop_all(engine)

@pytest.fixture(autouse=True)
def clean_tables(test_db_engine):
    yield
    with test_db_engine.connect() as db_conn:
        db_conn.execute(text("TRUNCATE TABLE images CASCADE"))
        db_conn.commit()

@pytest.fixture()
def db(test_db_engine):
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.close()

