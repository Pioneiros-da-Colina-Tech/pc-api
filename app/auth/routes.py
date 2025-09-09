from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas import BaseResponseSchema

from .dependencies import get_auth_repository
from .domain import (
    DeleteUserUseCase,
    DisableUserUseCase,
    EnableUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    LoginUserUseCase,
    RegisterUserUseCase,
    SearchUsersUseCase,
)
from .repository import AuthRepository
from .schemas import TokenSchema, UserSchema

router = APIRouter()


@router.get("/users", response_model=BaseResponseSchema)
async def list_users(
    limit: int = 100,
    offset: int = 0,
    include_disabled: bool = False,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """List users with pagination."""
    return await ListUsersUseCase(
        limit, offset, include_disabled, auth_repo
    ).execute()


@router.get("/users/{user_id}", response_model=BaseResponseSchema)
async def get_user(
    user_id: str,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Get a user by ID."""
    return await GetUserUseCase(user_id, auth_repo).execute()


@router.get("/users/search", response_model=BaseResponseSchema)
async def search_users(
    q: str,
    limit: int = 50,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Search users by username, email, or full name."""
    return await SearchUsersUseCase(q, limit, auth_repo).execute()


@router.post("/register", response_model=BaseResponseSchema)
async def register_user(
    user_data: UserSchema,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Register a new user."""
    return await RegisterUserUseCase(user_data, auth_repo).execute()


@router.post("/token", response_model=TokenSchema)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Login a user and return a token."""
    return await LoginUserUseCase(form_data, auth_repo).execute()


@router.put("/users/{user_id}/disable", response_model=BaseResponseSchema)
async def disable_user(
    user_id: str,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Disable a user account."""
    return await DisableUserUseCase(user_id, auth_repo).execute()


@router.put("/users/{user_id}/enable", response_model=BaseResponseSchema)
async def enable_user(
    user_id: str,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Enable a user account."""
    return await EnableUserUseCase(user_id, auth_repo).execute()


@router.delete("/users/{user_id}", response_model=BaseResponseSchema)
async def delete_user(
    user_id: str,
    hard_delete: bool = False,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Delete a user account (soft delete by default)."""
    return await DeleteUserUseCase(user_id, hard_delete, auth_repo).execute()
