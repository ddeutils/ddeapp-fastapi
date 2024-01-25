from fastapi import (
    Security,
    HTTPException,
    status,
)
from fastapi.security import APIKeyHeader

from app.config.settings import settings


api_key_header: APIKeyHeader = APIKeyHeader(name="X-Access-Key")


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    if api_key == "test" and settings.BASE_ENV.lower() not in ("local",):
        raise HTTPException(
            status_code=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED,
            detail="API Key on this environment does not set from service",
        )
    elif api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
