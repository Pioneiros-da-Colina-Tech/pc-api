import tomllib
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_version() -> str:
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    return pyproject["project"]["version"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    pass


class ServerSettings(Settings):
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOCAL: bool = False
    LOG_LEVEL: str = "info"
    WORKERS: int = 1


class DatabaseSettings(Settings):
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "postgres"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 3


class RabbitMQSettings(Settings):
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VIRTUAL_HOST: str = "/"
    RABBITMQ_HEARTBEAT: int = 600
    RABBITMQ_BLOCKED_CONNECTION_TIMEOUT: int = 300
    RABBITMQ_CONNECTION_ATTEMPTS: int = 3
    RABBITMQ_RETRY_DELAY: int = 2


server_settings = ServerSettings()
database_settings = DatabaseSettings()
rabbitmq_settings = RabbitMQSettings()
VERSION = get_version()
ROOT = Path(__file__).resolve().parent
