import os
import pathlib
import secrets
from datetime import timedelta
from typing import (
    List,
    Union,
)
from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    validator
)


class Settings(BaseSettings):
    PROJECT_NAME: str = os.environ.get(
        'PROJECT_NAME', 'DEFP FastAPI Application'
    )
    BASE_PATH: pathlib.Path = pathlib.Path(__file__).parent.parent.parent
    BASE_URL: AnyHttpUrl = 'http://127.0.0.1'
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g:
    # '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
            cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    FIRST_SUPERUSER: EmailStr = os.environ.get(
        'FIRST_SUPERUSER',
        'admin@example.com'
    )
    FIRST_SUPERUSER_PASSWORD: str = os.environ.get(
        'FIRST_SUPERUSER_PASSWORD',
        'P@ssw0rD'
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
