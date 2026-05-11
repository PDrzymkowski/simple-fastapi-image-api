import os

os.environ.setdefault("DB_URL", "postgresql://postgres:postgres@localhost:5432/test")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_REGION", "eu-west-1")
os.environ.setdefault("S3_BUCKET_NAME", "test-bucket")

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.app import app
from app.db import get_db
from app.models import BaseModel

TEST_DB_URL = os.environ["DB_URL"]


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
    Session = sessionmaker(test_db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture()
def s3():
    with mock_aws():
        client = boto3.client("s3", region_name="eu-west-1")
        client.create_bucket(
            Bucket="test-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
        )
        yield client


@pytest.fixture()
def client(db, s3):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


from .fixtures import *  # noqa
