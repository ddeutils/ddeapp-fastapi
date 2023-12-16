from fastapi import FastAPI, status
from fastapi.testclient import TestClient
import pytest
from httpx import AsyncClient
from app.config.settings import settings


def test_health(app: FastAPI) -> None:
    client = TestClient(app)
    response = client.get("http://127.0.0.1:8080/health/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_health_async(app: FastAPI, client: AsyncClient) -> None:
    res = await client.get("http://127.0.0.1:8080/health/")
    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_common_async(app: FastAPI, client: AsyncClient):
    response = await client.post(
        f"http://127.0.0.1:8080{settings.API_V1_STR}/common/",
        json={
            "P_PRCS_OBJ": {
                "STREM_NM": "TEST_STREAM",
                "CHK_STREM_F": "0",
                "PRCS_GRP": "TEST_GROUP",
                "PRCS_TYP": "999",
                "PRCS_LOAD_TYP": "T",
                "ASAT_DT": "20220101",
                "PRV_ASAT_DT": "20220101",
                "CALC_ASAT_DT": "20220101",
            },
            "P_LD_ID": "999",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"app_path": str(settings.BASE_PATH.absolute())}


@pytest.mark.asyncio
async def test_common_async_fail(app: FastAPI, client: AsyncClient):
    response = await client.post(
        f"http://127.0.0.1:8080{settings.API_V1_STR}/common/",
        json={
            "P_PRCS_OBJ": {
                "STREM_NM": "TEST_STREAM",
            },
            "P_LD_ID": "999",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Process object does not valid with model.",
    }


@pytest.mark.asyncio
async def test_common_async_data(app: FastAPI, client: AsyncClient):
    response = await client.post(
        f"http://127.0.0.1:8080{settings.API_V1_STR}/common-temp/",
        json={
            "P_PRCS_OBJ": {
                "STREM_NM": "demo",
                "SRC_SCHM_NM": "demo-job",
                "CHK_STREM_F": "0",
                "PRCS_GRP": "TEST_GROUP",
                "PRCS_TYP": "999",
                "PRCS_LOAD_TYP": "T",
                "ASAT_DT": "20220101",
                "PRV_ASAT_DT": "20220101",
                "CALC_ASAT_DT": "20220101",
            },
            "P_LD_ID": "999",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"app_path": str(settings.BASE_PATH.absolute())}
