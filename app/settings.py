import multiprocessing
import tomllib
from enum import Enum
from functools import cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


@cache
def pyproject() -> dict:
    """Loads the pyproject.toml file and returns its contents as a dictionary."""
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def get_version() -> str:
    return pyproject()["project"]["version"]


def get_app_name() -> str:
    return pyproject()["project"]["name"]


def get_workers() -> int:
    return (multiprocessing.cpu_count() * 2) + 1


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    pass


class EnvironmentEnum(str, Enum):
    DEV = "development"
    PROD = "production"
    STAGING = "staging"
    TEST = "test"


class ServerSettings(Settings):
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOG_LEVEL: str = "info"
    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.DEV
    WORKERS: int = get_workers()
    SENTRY_DSN: str = ""


class DatabaseSettings(Settings):
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "postgres"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_MAX_OVERFLOW: int = 5
    DATABASE_POOL_RECYCLE: int = 1800  # 30 minutes
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RESET_ON_RETURN: str = "commit"


class AuthSettings(Settings):
    AUTH_SECRET_KEY: str = "secret"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


server_settings = ServerSettings()
database_settings = DatabaseSettings()
auth_settings = AuthSettings()
VERSION = get_version()
APP_NAME = get_app_name()
ROOT = Path(__file__).resolve().parent
