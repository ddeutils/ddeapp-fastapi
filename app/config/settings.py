import os
import pathlib
import secrets
from datetime import timedelta
from typing import (
    Union,
)
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "DEFP FastAPI Application")
    BASE_PATH: pathlib.Path = pathlib.Path(__file__).parent.parent.parent
    BASE_URL: AnyHttpUrl = "http://127.0.0.1"
    BASE_ENV: str = os.getenv("API_ENV", "local")

    API_V1_STR: str = "/api/v1"
    API_KEY: str = os.getenv("API_KEY", "test")

    SECRET_KEY: str = secrets.token_urlsafe(32)

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g:
    # '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    FIRST_SUPERUSER: EmailStr = os.getenv(
        "FIRST_SUPERUSER",
        "admin@example.com",
    )
    FIRST_SUPERUSER_PASSWORD: str = os.getenv(
        "FIRST_SUPERUSER_PASSWORD",
        "P@ssw0rD",
    )

    # Task Configuration
    MAX_IN_PARALLEL: int = 10
    FILE_RETENTION_TIMEDELTA: timedelta = timedelta(days=5)
    REQUEST_TIME_OUT: int = 200

    class Config:
        # For get configuration from `.env` file.
        # env_file = pathlib.Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True


settings = Settings()
