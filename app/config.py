from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
    )