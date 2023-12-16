from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from app.config.settings import settings
import httpx
import json


def create_app() -> FastAPI:
    """Application Factory"""
    app: FastAPI = FastAPI(
        title="FastAPI Application for DMZ",
        description="Web Application that use FastAPI for DMZ",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
    )

    from .routes.initial.routes import routes as initial

    app.include_router(initial, prefix=settings.API_V1_STR)

    @app.on_event("startup")
    async def startup_event():
        client = httpx.AsyncClient()
        app.state.client = client

    @app.on_event("shutdown")
    async def shutdown_event():
        client = app.state.client
        await client.aclose()

    @app.get("/health/", response_class=JSONResponse)
    async def health():
        return JSONResponse({"message": "Hello World"})

    from app.tasks import delete_files_and_empty_folders
    from app.dependencies import parameters
    from app.models import ADFObject

    @app.delete("/delete/data-files/", response_class=JSONResponse)
    async def delete_files():
        """Delete files which have creation datetime less than configuration
        datetime
        """
        result = await delete_files_and_empty_folders()
        return JSONResponse(
            content={
                "message": "Successful Search and Delete file from local data",
                "files": result["files"],
                "folders": result["folders"],
            },
            status_code=status.HTTP_200_OK,
        )

    @app.post(
        f"{settings.API_V1_STR}/common-temp/",
        response_class=JSONResponse,
    )
    async def common_temp(
        request: Request,
        params: ADFObject = Depends(parameters),
    ):
        await delete_files()

        print(params)

        await delete_files()

        return JSONResponse(
            content={
                "app_path": str(settings.BASE_PATH.absolute()),
            },
            status_code=status.HTTP_200_OK,
        )

    @app.post(
        f"{settings.API_V1_STR}/common/",
        response_class=JSONResponse,
    )
    async def common(
        request: Request,
        params: ADFObject = Depends(parameters),
    ):
        """Common Gateway function that call internal route with path from
        ADF Object.
        """
        if params.p_prcs_obj.strem_nm == "TEST_STREAM":
            return JSONResponse(
                content={
                    "app_path": str(settings.BASE_PATH.absolute()),
                },
                status_code=status.HTTP_200_OK,
            )

        await delete_files()

        internal_route: str = (
            f"{params.p_prcs_obj.src_schm_nm}/{src_tbl}/"
            if (src_tbl := params.p_prcs_obj.src_tbl)
            else f"{params.p_prcs_obj.src_schm_nm}/"
        )

        # Pass the Query if it exists.
        if qry := params.p_prcs_obj.cus_qry:
            internal_route: str = f"{internal_route}?{qry}"

        response: httpx.Response = await request.app.state.client.post(
            (
                f"{settings.BASE_URL}:{request.url.port}{settings.API_V1_STR}/"
                f"{internal_route}"
            ),
            json=json.loads(params.json(by_alias=True)),
            timeout=settings.REQUEST_TIME_OUT,
        )
        if response.status_code != status.HTTP_200_OK:
            return JSONResponse(
                content={"message": f"Common Gateway Error: {response.text}"},
                status_code=response.status_code,
            )
        return JSONResponse(
            content={
                "app_path": str(settings.BASE_PATH.absolute()),
                "result": response.json(),
            },
            status_code=status.HTTP_200_OK,
        )

    return app
