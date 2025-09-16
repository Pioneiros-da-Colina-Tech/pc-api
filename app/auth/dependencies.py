from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.adapter import DatabaseAdapter

from .repository import AuthRepository
from .schemas import User
from .utils import extract_user_id_from_token, oauth2_scheme


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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_repo: AuthRepository = Depends(get_auth_repository),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = extract_user_id_from_token(token)
    if user_id is None:
        raise credentials_exception

    user = await auth_repo.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user
