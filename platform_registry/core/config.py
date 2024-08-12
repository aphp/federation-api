import os
from typing import Literal, Annotated, Any

from pydantic import (
    PostgresDsn,
    computed_field,
    AnyUrl, BeforeValidator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl

env = os.environ


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env",
                                      env_ignore_empty=True,
                                      extra="ignore")
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str

    OPENAPI_URL: str

    JWT_SECRET_KEY: str     # secrets.token_urlsafe(32)
    JWT_ALGORITHM: str
    JWT_TOKEN_EXPIRE_MINUTES: int

    DOMAIN: str
    ENVIRONMENT: Literal["dev", "production"]
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    DB_HOST: str
    DB_NAME: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str

    ACCESS_KEY_LIFESPAN_DAYS: int

    @computed_field
    @property
    def database_url(self) -> PostgresDsn:
        return MultiHostUrl.build(scheme="postgresql+psycopg",
                                  host=self.DB_HOST,
                                  path=self.DB_NAME,
                                  port=self.DB_PORT,
                                  username=self.DB_USER,
                                  password=self.DB_PASSWORD)

    @computed_field
    @property
    def server_host(self) -> str:
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"


settings = Settings()
