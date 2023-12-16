import warnings
import os
import pytest
import pytest_asyncio
from fastapi import FastAPI
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from typing import AsyncGenerator
from app.config import settings


@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    yield


@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from app.app import create_app

    return create_app()


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncGenerator:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url=f"{settings.BASE_URL}:8080",
            headers={"Content-Type": "application/json"}
        ) as _client:
            yield _client
