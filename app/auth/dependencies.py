from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.adapter import DatabaseAdapter

from .repository import AuthRepository


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """
    Dependency to provide database session.

    This function creates an AsyncSession from the DatabaseAdapter
    stored in the FastAPI app state and ensures proper cleanup.
    """
    adapter: DatabaseAdapter = request.app.state.session_adapter
    session = await adapter.session.new()

    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_auth_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AuthRepository:
    """
    Dependency to provide AuthRepository with database session.
    """
    return AuthRepository(session)
