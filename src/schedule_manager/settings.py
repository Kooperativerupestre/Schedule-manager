from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_test_db: str

    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore
