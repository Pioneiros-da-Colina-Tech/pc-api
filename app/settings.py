from decouple import config

from app.infra.database.config import ConnectionConfig, PoolConfig

# LOG_LEVEL = config(
#     "LOG_LEVEL",
#     default="info",
#     cast=Choices(["debug", "info", "warning", "error", "critical"], cast=str),
# )
LOCAL = config("LOCAL", default=False, cast=bool)
SERVER_HOST = str(config("SERVER_HOST", default="0.0.0.0", cast=str))
SERVER_PORT = config("SERVER_PORT", default=8000, cast=int)
WORKERS = config("WORKERS", default=5, cast=int)

# JWT Configuration
JWT_SECRET_KEY = str(
    config("JWT_SECRET_KEY", default="your-secret-key-change-this", cast=str)
)
JWT_ALGORITHM = str(config("JWT_ALGORITHM", default="HS256", cast=str))
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int
)

DB_HOST = str(config("DB_HOST", default="localhost", cast=str))
DB_PORT = config("DB_PORT", default=5432, cast=int)
DB_NAME = str(config("DB_NAME", default="", cast=str))
DB_USER = str(config("DB_USER", default="", cast=str))
DB_PASSWORD = str(config("DB_PASSWORD", default="", cast=str))
DB_POOL_SIZE = config("DB_POOL_SIZE", default=3, cast=int)
DATABASE_CONFIG = ConnectionConfig(
    host=DB_HOST,
    port=DB_PORT,
    name=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    pool=PoolConfig(
        size=DB_POOL_SIZE,
    ),
)
