from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
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
    app.add_exception_handler(APIError, api_error_handler)  # pyright: ignore[reportArgumentType]]
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
