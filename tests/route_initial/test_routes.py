import pytest
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
from app.config.settings import settings

DEMO_DATA_KEYS = {
    'id', 'type', 'create_date', 'value',
}


@pytest.mark.asyncio
async def test_route_demo_data(client: AsyncClient):
    response = await client.get(
        f"http://127.0.0.1:8080{settings.API_V1_STR}/demo/data/",
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 20
    assert all(set(data.keys()) == DEMO_DATA_KEYS for data in response.json())


@pytest.mark.asyncio
async def test_route_demo_data_limit(client: AsyncClient):
    response = await client.get(
        f"http://127.0.0.1:8080{settings.API_V1_STR}/demo/data/?limit=2",
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert all(set(data.keys()) == DEMO_DATA_KEYS for data in response.json())


@patch(
    target='app.tasks.httpx.AsyncClient.get',
    return_value=Response(
        status_code=200,
        json={'message': 'Hello World'},
    ),
)
def test_route_demo_task(mocker: AsyncMock, app: FastAPI):
    app_client = TestClient(app)
    response = app_client.get(
        f"http://127.0.0.1:8080{settings.API_V1_STR}/demo/task/"
    )
    assert mocker.called
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10
    assert response.json() == [{"message": "Hello World"}] * 10


@patch(
    target='app.tasks.httpx.AsyncClient.get',
    return_value=Response(
        status_code=200,
        json=[{'message': 'Hello World'}],
    ),
)
def test_route_demo_job_deps_raise(mocker: AsyncMock, app: FastAPI):
    app_client = TestClient(app)
    response = app_client.post(
        f"http://127.0.0.1:8080{settings.API_V1_STR}/demo/demo-job/"
    )
    assert not mocker.called
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': 'Json decoder error from parsing data to ADFObject.'
    }

