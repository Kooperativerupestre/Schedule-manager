from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse, urlunparse

ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    database_url: str
    test_database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    redis_url: str = "redis://localhost:6379"

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        extra="ignore",
    )

    @staticmethod
    def get_admin_url(database_url: str, admin_db: str = "postgres") -> str:
        parsed = urlparse(database_url)
        admin_parsed = parsed._replace(path=f"/{admin_db}")
        return urlunparse(admin_parsed)


settings = Settings()  # type: ignore
