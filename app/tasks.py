import json
import httpx
import asyncio
from fastapi import status
from pathlib import Path
from typing import Callable, List, Any
from datetime import datetime, timezone
from typing import Optional
from app.config.settings import settings
from app.utils import is_empty


# If you want to limit the number of requests executing in parallel,
# you can use asyncio.semaphore like so,
# docs: https://devpress.csdn.net/python/630454667e66823466199f3a.html
limit_sem = asyncio.Semaphore(settings.MAX_IN_PARALLEL)


async def response_json(client: httpx.AsyncClient, url: str):
    """Return json data from response object"""
    async with limit_sem:
        response = await client.get(url)
        await asyncio.sleep(1)
        if response.status_code == status.HTTP_307_TEMPORARY_REDIRECT:
            raise ValueError(
                f"{response.url.path} should have '/' in the end of path"
            )
        if response.status_code != status.HTTP_200_OK:
            raise httpx.HTTPError(
                response.text
            )
        return response.json()


async def task(
        url: str,
        parallel_number: int = 10,
        prepare_url: Optional[Callable[[str, int], str]] = None,
):
    """Task Function for call request with parallel process"""
    prepare_url: Callable = prepare_url or (lambda x, _: x)
    async with httpx.AsyncClient() as client:
        tasks: List[Any] = [
            response_json(client, prepare_url(url, _))
            for _ in range(parallel_number)
        ]
        result = await asyncio.gather(*tasks)
    return result


async def common_save(
        data: list,
        path: Optional[str] = None,
        prefix: Optional[str] = None,
) -> None:
    """Common task for save file to local with splitting to parallel files"""
    data_path: Path = (
            Path(f"{settings.BASE_PATH}") / "data" / (path or 'demo')
    )
    data_path.mkdir(parents=True, exist_ok=True)
    if data_path.exists():
        if not is_empty(data_path):
            [
                f.unlink() for f in data_path.glob("*")
                if f.is_file()
            ]
        for idx, _data in enumerate(data):
            with (
                    (
                            data_path / f'{(prefix or "demo")}.{idx}.json'
                    ).open("w", encoding="utf-8")
            ) as f:
                f.write(json.dumps(_data, indent=2))


async def merge_save(
        data: list,
        path: Optional[str] = None,
        prefix: Optional[str] = None,
) -> None:
    """Common task for save file to local with merging to one file"""
    data_path = (Path(f"{settings.BASE_PATH}") / "data" / (path or 'demo'))
    data_path.mkdir(parents=True, exist_ok=True)
    if data_path.exists():
        if not is_empty(data_path):
            [
                f.unlink() for f in data_path.glob("*")
                if f.is_file()
            ]
        with (
                (
                        data_path / f'{(prefix or "demo")}.json'
                ).open("w", encoding="utf-8")
        ) as f:
            f.write(
                json.dumps(
                    sum(data, []),
                    indent=2,
                )
            )


async def delete_files_and_empty_folders(
        filter_dir: Optional[str] = None,
) -> dict:
    """Delete Files and empty Folders.

    :param filter_dir: A directory name that it want to delete.
    """

    data_path: Path = Path(settings.BASE_PATH) / "data"
    del_files: int = 0
    del_folders: int = 0

    if filter_dir:
        data_path: Path = data_path / filter_dir

    for file in filter(lambda x: x.is_file(), data_path.rglob('*')):
        if (
                datetime.fromtimestamp(file.stat().st_ctime, tz=timezone.utc)
                < (
                    datetime.now(tz=timezone.utc) -
                    settings.FILE_RETENTION_TIMEDELTA
                )
        ):
            file.unlink(missing_ok=True)
            del_files += 1

    for folder in filter(lambda x: not x.is_file(), data_path.rglob('*')):
        if is_empty(folder):
            folder.rmdir()
            del_folders += 1

    return {
        'files': del_files,
        'folders': del_folders,
    }
