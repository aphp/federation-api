import logging
from typing import Annotated, Any

from pydantic import PostgresDsn, computed_field, AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl

logger = logging.getLogger(__name__)


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None,
                                      env_ignore_empty=True,
                                      extra="ignore")
    PROJECT_NAME: str = "Platform Registry"
    DESCRIPTION_MD: str = "**Platform Registry** API"
    VERSION: str = "1.1-dev"

    OPENAPI_URL: str = "/openapi.json"

    JWT_SECRET_KEY: str     # secrets.token_urlsafe(32)
    JWT_ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    DB_HOST: str
    DB_NAME: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str

    ACCESS_KEY_LIFESPAN_DAYS: int

    @computed_field
    @property
    def database_url(self) -> PostgresDsn:
        return MultiHostUrl.build(scheme="postgresql+psycopg",
                                  host=self.DB_HOST,
                                  path=self.DB_NAME,
                                  port=int(self.DB_PORT),
                                  username=self.DB_USER,
                                  password=self.DB_PASSWORD)

settings = Settings()
