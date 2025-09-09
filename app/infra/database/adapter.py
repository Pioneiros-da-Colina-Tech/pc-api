from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import cached_property
from typing import Any

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async
from fastapi import Request

from .config import DatabaseConfig


@dataclass
class DatabaseAdapter:
    config: DatabaseConfig
    debug: bool = False

    @cached_property
    def engine(self) -> sa_async.AsyncEngine:
        return sa_async.create_async_engine(
            self.config.make_uri(is_asyncio=True),
            pool_size=self.config.connection.pool.size,
            echo=self.debug,
            pool_recycle=self.config.connection.pool.recycle,
            max_overflow=self.config.connection.pool.max_overflow,
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
        else:
            _ = await client.begin_nested()

    async def in_atomic(self, client: sa_async.AsyncConnection) -> bool:
        """
        Check if the connection is in a transaction.
        """
        return client.in_transaction() or client.in_nested_transaction()

    @cached_property
    def session(self) -> "SessionAdapter":
        """
        Create a session adapter for the database connection.
        """
        return SessionAdapter(provider=self, debug=self.debug)


@dataclass
class SessionAdapter:
    """
    Session adapter for SQLAlchemy.
    """

    provider: DatabaseAdapter
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
            await client.begin()
        else:
            await client.begin_nested()

    async def in_atomic(self, client: sa_async.AsyncSession) -> bool:
        """
        Check if the session is in a transaction.
        """
        return client.in_transaction()


# FastAPI Integration #

metadata = sa.MetaData()


class AsyncSessionManager:
    """
    Async context manager for database sessions.

    Provides an alternative pattern to the dependency injection approach.
    Usage:
        async with AsyncSessionManager(adapter) as session:
            # Use session here
            result = await session.execute(text("SELECT 1"))
            # Session is automatically committed and closed
    """

    def __init__(self, adapter: DatabaseAdapter):
        self.adapter = adapter
        self.session: sa_async.AsyncSession | None = None

    async def __aenter__(self) -> sa_async.AsyncSession:
        self.session = await self.adapter.session.new()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type is None:
                    await self.session.commit()
                else:
                    await self.session.rollback()
            finally:
                await self.session.close()
                self.session = None


async def create_session_adapter(
    provider: DatabaseAdapter,
) -> sa_async.AsyncSession:
    """
    Create a session adapter.
    """
    return await SessionAdapter(provider).new()


def get_session_adapter(request: Request) -> DatabaseAdapter:
    """
    Get the session adapter.
    """
    return request.app.state.session_adapter
