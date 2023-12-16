from fastapi import APIRouter, Depends, Request, Query, BackgroundTasks, status
from fastapi.responses import JSONResponse
from time import time

from app.models import ADFObject
from app.dependencies import parameters
from app.tasks import (
    task,
    merge_save,
)
from app.routes.initial.tasks import generate_data
from app.config.settings import settings
from app.logger import get_logger


logger = get_logger(__name__)


routes = APIRouter(
    tags=['initial']
)


@routes.get(
    "/demo/task/",
    response_description="Async task request with httpx",
    response_class=JSONResponse,
)
async def get_demo_task(request: Request):
    """Demo Task that parallel call health route"""
    start = time()
    result = await task(
        url=f"{settings.BASE_URL}:{request.url.port}/health/",
    )
    logger.info(f"Task usage time: {time() - start}")
    return result


@routes.get(
    "/demo/data/",
    response_class=JSONResponse
)
async def get_demo_data(
        limit: int = Query(default=20),
):
    return JSONResponse(
        content=[await generate_data() for _ in range(limit)],
        status_code=status.HTTP_200_OK,
    )


@routes.post(
    '/demo/demo-job/',
    response_class=JSONResponse
)
async def start_demo_job(
        bg: BackgroundTasks,
        params: ADFObject = Depends(parameters),
        limit: int = Query(default=100),
        parallel: int = Query(default=1),
):
    """Demo job function"""
    # Request Data from internal route
    data = await task(
        url=(
            f"{params.p_prcs_obj.server_nm}?limit={limit}"
        ),
        parallel_number=parallel
    )
    # print("Job Parameters:", params.dict(by_alias=True))
    # Save data from request to local storage
    bg.add_task(
        merge_save,
        data=data,
        path=(
            f"{params.p_prcs_obj.pth}/{params.p_prcs_obj.tgt_tbl}/"
            f"{params.p_prcs_obj.asat_dt}"
        ),
        prefix=params.p_prcs_obj.tgt_tbl
    )
    return JSONResponse(
        content={'data': data},
        status_code=status.HTTP_200_OK,
    )
