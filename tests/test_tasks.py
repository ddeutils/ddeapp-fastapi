import json
from pathlib import Path
import pytest
from unittest.mock import patch
from httpx import AsyncClient, Response
from app.tasks import (
    delete_files_and_empty_folders,
    response_json,
    task,
    common_save,
    merge_save,
)
from app.config.settings import settings


@pytest.mark.asyncio
async def test_tasks_delete_files_and_empty_folders():
    data_path = Path(settings.BASE_PATH) / "data" / "tests"
    data_path.mkdir(exist_ok=True)

    test_path = data_path / "tasks"
    test_path.mkdir(exist_ok=True)

    test_empty_path = data_path / "tasks_empty"
    test_empty_path.mkdir(exist_ok=True)

    (test_path / "test_file.txt").write_text("test")

    rs = await delete_files_and_empty_folders("tasks")
    assert rs == {'files': 0, 'folders': 0}

    rs = await delete_files_and_empty_folders()
    assert rs == {'files': 0, 'folders': 1}

    (test_path / "test_file.txt").unlink(missing_ok=True)
    test_path.rmdir()
    data_path.rmdir()


@pytest.mark.asyncio
async def test_tasks_response_json(client: AsyncClient):
    rs = await response_json(client, 'http://127.0.0.1:8080/health/')
    assert rs == {'message': 'Hello World'}


@pytest.mark.asyncio
@patch(
    target='app.tasks.httpx.AsyncClient.get',
    return_value=Response(
        status_code=200,
        json={'message': 'Hello World'},
    ),
)
async def test_tasks_task(client: AsyncClient):
    rs = await task(
        'http://127.0.0.1:8080/health/',
        parallel_number=2,
    )
    assert rs == [{'message': 'Hello World'}, {'message': 'Hello World'}]


@pytest.mark.asyncio
async def test_common_save():
    await common_save(
        data=[
            [{"id": 1, "content": "foo"}],
            [{"id": 2, "content": "bar"}],
        ],
        path="tests_common",
        prefix="test_common",
    )
    data_path: Path = Path(settings.BASE_PATH) / "data" / "tests_common"
    assert (data_path / "test_common.0.json").exists()
    assert (
            json.loads(
                (data_path / "test_common.0.json").read_text(encoding="utf-8")
            ) == [{"id": 1, "content": "foo"}]
    )
    assert (data_path / "test_common.1.json").exists()
    assert (
            json.loads(
                (data_path / "test_common.1.json").read_text(encoding="utf-8")
            ) == [{"id": 2, "content": "bar"}]
    )

    for f in data_path.glob("*"):
        f.unlink()

    data_path.rmdir()


@pytest.mark.asyncio
async def test_merge_save():
    await merge_save(
        data=[
            [{"id": 1, "content": "foo"}],
            [{"id": 2, "content": "bar"}],
        ],
        path="tests_merge",
        prefix="test_merge",
    )
    data_path: Path = Path(settings.BASE_PATH) / "data" / "tests_merge"
    assert (data_path / "test_merge.json").exists()
    assert (
            json.loads(
                (data_path / "test_merge.json").read_text(encoding="utf-8")
            ) == [{"id": 1, "content": "foo"}, {"id": 2, "content": "bar"}]
    )

    for f in data_path.glob("*"):
        f.unlink()

    data_path.rmdir()
