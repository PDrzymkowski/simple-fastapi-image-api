from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env_file", env_file_encoding="utf-8")

    db_url: str
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = ""


_settings = None

def get_settings():
    global _settings
    if _settings is None:
        settings = Settings()
    return _settings