from pydantic_settings import BaseSettings
from urllib.parse import urlsplit, urlunsplit


class Settings(BaseSettings):
    database_url: str
    model_config = {"env_file": ".env"}

    @staticmethod
    def get_admin_url(database_url: str) -> str:
        r = urlsplit(database_url)
        r._replace(path='/postgres')

        return urlunsplit(r)    
