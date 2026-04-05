from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import aclosing, asynccontextmanager
from dataclasses import dataclass
from functools import cached_property
from typing import Annotated, Any

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from fastapi import Depends, FastAPI, Request

from app.settings import database_settings

from .config import ConnectionConfig, DatabaseConfig, PoolConfig


@dataclass
class SessionAdapter:
    """
    Session adapter for SQLAlchemy.
    """

    provider: "DatabaseAdapter"
    debug: bool = False

    async def new(self) -> sa_async.AsyncSession:
        """
        Create a new session.
        """
        return sa_async.AsyncSession(bind=self.provider.engine)

    async def is_closed(self, client: sa_async.AsyncSession) -> bool:
        """
        Check if the session is closed.
        """
        return client.is_active

    async def release(self, client: sa_async.AsyncSession) -> None:
        """
        Release the session.
        """
        await client.close()

    async def aclose(self) -> None:
        """
        Close the session.
        """
        await self.provider.aclose()

    async def commit(self, client: sa_async.AsyncSession) -> None:
        """
        Commit the session.
        """
        await client.commit()

    async def rollback(self, client: sa_async.AsyncSession) -> None:
        """
        Rollback the session.
        """
        await client.rollback()

    async def begin(self, client: sa_async.AsyncSession) -> None:
        """
        Begin the session.
        """
        if not client.in_transaction():
            _ = await client.begin()
        else:
            _ = await client.begin_nested()


@dataclass
class DatabaseAdapter:
    config: DatabaseConfig

    @cached_property
    def engine(self) -> sa_async.AsyncEngine:
        return sa_async.create_async_engine(
            self.config.make_uri(is_asyncio=True),
            pool_size=self.config.connection.pool.size,
            echo=self.config.connection.echo,
            pool_recycle=self.config.connection.pool.recycle,
            max_overflow=self.config.connection.pool.max_overflow,
            pool_pre_ping=self.config.connection.pool.pre_ping,
            pool_timeout=self.config.connection.pool.pool_timeout,
            pool_reset_on_return=self.config.connection.pool.pool_reset_on_return,
            connect_args={
                "keepalives": 1,
                "keepalives_idle": 300,
                "keepalives_interval": 30,
                "keepalives_count": 3,
                "connect_timeout": 30,
                "application_name": "ram-ng-sec-fidc-api",
            },
        )

    async def new(self):
        return await self.engine.connect()

    async def is_closed(self, client: sa_async.AsyncConnection) -> bool:
        return client.closed

    async def release(self, client: sa_async.AsyncConnection) -> None:
        return await client.close()

    async def aclose(self) -> None:
        await self.engine.dispose()

    async def _do_with_transaction(
        self,
        client: sa_async.AsyncConnection,
        callback: Callable[[sa_async.AsyncTransaction], Awaitable[Any]],
    ) -> None:
        if not client.in_transaction():
            return
        trx = (
            client.get_transaction()
            if not client.in_nested_transaction()
            else client.get_nested_transaction()
        )
        if trx and trx.is_valid:
            await callback(trx)

    async def commit(self, client: sa_async.AsyncConnection) -> None:
        await self._do_with_transaction(
            client, sa_async.AsyncTransaction.commit
        )

    async def rollback(self, client: sa_async.AsyncConnection) -> None:
        await self._do_with_transaction(
            client, sa_async.AsyncTransaction.rollback
        )

    async def begin(self, client: sa_async.AsyncConnection) -> None:
        if not client.in_transaction():
            _ = await client.begin()
        _ = await client.begin_nested()

    @cached_property
    def session(self) -> SessionAdapter:
        """
        Create a session adapter for the database connection.
        """
        return SessionAdapter(provider=self, debug=self.config.connection.echo)


# FastAPI Integration #

metadata = sa.MetaData()


@asynccontextmanager
async def create_session_adapter(
    app: FastAPI,
) -> AsyncGenerator[None]:
    """
    Create a session adapter.
    """
    config = DatabaseConfig(
        connection=ConnectionConfig(
            host=database_settings.DATABASE_HOST,
            port=database_settings.DATABASE_PORT,
            user=database_settings.DATABASE_USER,
            password=database_settings.DATABASE_PASSWORD,
            name=database_settings.DATABASE_NAME,
            pool=PoolConfig(size=database_settings.DATABASE_POOL_SIZE),
        )
    )
    async with aclosing(DatabaseAdapter(config=config)) as adapter:
        app.state.session_adapter = adapter
        yield


def get_session_adapter(request: Request) -> DatabaseAdapter:
    """
    Get the session adapter.
    """
    return request.app.state.session_adapter


async def get_session(
    adapter: Annotated[DatabaseAdapter, Depends(get_session_adapter)],
) -> AsyncGenerator[sa_async.AsyncSession]:
    """
    Get a new database session for the request.

    This dependency creates a new session per request and ensures it's properly
    committed and closed after the request completes.
    """
    session = await adapter.session.new()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


SessionContext = Annotated[sa_async.AsyncSession, Depends(get_session)]
