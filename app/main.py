from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger
from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.exc import APIError, api_error_handler
from app.api.routes import router
from app.api.secure import secure_middleware
from app.infra.database.adapter import create_session_adapter
from app.settings import (
    VERSION,
    EnvironmentEnum,
    server_settings,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI"""
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(create_session_adapter(app))
        yield


async def integrity_error_handler(_: Request, exc: IntegrityError) -> ORJSONResponse:
    cause = exc.orig
    if isinstance(cause, ForeignKeyViolation):
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Related record not found",
                "detail": str(cause).split("\n")[0],
                "fields": [],
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            },
        )
    if isinstance(cause, UniqueViolation):
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Record already exists",
                "detail": str(cause).split("\n")[0],
                "fields": [],
                "status_code": status.HTTP_409_CONFLICT,
            },
        )
    return ORJSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "message": "Database integrity error",
            "detail": str(cause).split("\n")[0] if cause else None,
            "fields": [],
            "status_code": status.HTTP_409_CONFLICT,
        },
    )


def get_app() -> FastAPI:
    app = FastAPI(
        title="NG-SEC FIDC's Core",
        description="NG-SEC FIDC's Core API",
        version=VERSION,
        contact={
            "name": "Pioneiros da colina",
            "email": "dev@rezendevitor.gmail.com",
            "url": "https://clubes.adventistas.org/br/aps/14062/pioneiros-da-colina/",
        },
        openapi_url="/openapi.json"
        if server_settings.ENVIRONMENT != EnvironmentEnum.PROD
        else None,
        docs_url="/docs"
        if server_settings.ENVIRONMENT != EnvironmentEnum.PROD
        else None,
        redoc_url="/redoc"
        if server_settings.ENVIRONMENT != EnvironmentEnum.PROD
        else None,
        lifespan=lifespan,
    )
    app.add_exception_handler(APIError, api_error_handler)  # pyright: ignore[reportArgumentType]
    app.add_exception_handler(IntegrityError, integrity_error_handler)  # pyright: ignore[reportArgumentType]
    app.add_middleware(BaseHTTPMiddleware, dispatch=secure_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
    app.include_router(router=router)
    return app


app = get_app()

if __name__ == "__main__":
    from granian.constants import Interfaces, Loops
    from granian.log import LogLevels
    from granian.server import Server

    logger.info(
        f"Listening on {server_settings.SERVER_HOST}:{server_settings.SERVER_PORT}"
    )
    logger.info(f"Environment: {server_settings.ENVIRONMENT}")
    logger.debug(f"Workers: {server_settings.WORKERS}")
    logger.debug(f"ASGI Server: {Server.__name__}")

    Server(
        "app.main:app",
        address=server_settings.SERVER_HOST,
        port=server_settings.SERVER_PORT,
        interface=Interfaces.ASGI,
        log_access=True,
        log_level=LogLevels.info,
        workers=server_settings.WORKERS,
        loop=Loops.uvloop,
    ).serve()
