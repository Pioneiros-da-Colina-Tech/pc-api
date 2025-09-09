from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typeid import TypeID

from app.api.schemas import BaseResponseSchema

from .dependencies import get_auth_repository
from .repository import AuthRepository
from .schemas import TokenSchema, UserSchema

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


@router.post("/register", response_model=BaseResponseSchema)
async def register_user(
    user_data: UserSchema,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Register a new user."""
    # Check if user already exists
    if await auth_repo.user_exists(
        username=user_data.username, email=user_data.email
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists",
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create the user
    user = await auth_repo.create_user(user_data, hashed_password)

    return BaseResponseSchema(
        status=201,
        message="User registered successfully",
        data={"user_id": str(user.id_), "username": user.username},
    )


@router.post("/token", response_model=TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Authenticate user and return access token."""
    # Get user by username
    user = await auth_repo.get_user_by_username(form_data.username)

    if not user or not verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # In a real implementation, you would create a JWT token here
    # For now, returning a placeholder
    return TokenSchema(access_token="placeholder_token", token_type="bearer")


@router.get("/users/{user_id}", response_model=BaseResponseSchema)
async def get_user(
    user_id: str,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Get a user by ID."""
    try:
        user_type_id = TypeID.from_string(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    user = await auth_repo.get_user_by_id(user_type_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Remove sensitive information
    user_data = user.model_dump()
    del user_data["hashed_password"]

    return BaseResponseSchema(
        status=200,
        message="User retrieved successfully",
        data=user_data,
    )


@router.get("/users", response_model=BaseResponseSchema)
async def list_users(
    limit: int = 100,
    offset: int = 0,
    include_disabled: bool = False,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """List users with pagination."""
    users = await auth_repo.list_users(
        limit=limit, offset=offset, include_disabled=include_disabled
    )
    total_count = await auth_repo.count_users(include_disabled=include_disabled)

    # Remove sensitive information
    users_data = []
    for user in users:
        user_data = user.model_dump()
        del user_data["hashed_password"]
        users_data.append(user_data)

    return BaseResponseSchema(
        status=200,
        message="Users retrieved successfully",
        data={
            "users": users_data,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count,
            },
        },
    )


@router.put("/users/{user_id}/disable", response_model=BaseResponseSchema)
async def disable_user(
    user_id: str,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Disable a user account."""
    try:
        user_type_id = TypeID.from_string(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    success = await auth_repo.disable_user(user_type_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return BaseResponseSchema(
        status=200,
        message="User disabled successfully",
        data={"user_id": user_id},
    )


@router.put("/users/{user_id}/enable", response_model=BaseResponseSchema)
async def enable_user(
    user_id: str,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Enable a user account."""
    try:
        user_type_id = TypeID.from_string(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    success = await auth_repo.enable_user(user_type_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return BaseResponseSchema(
        status=200,
        message="User enabled successfully",
        data={"user_id": user_id},
    )


@router.delete("/users/{user_id}", response_model=BaseResponseSchema)
async def delete_user(
    user_id: str,
    hard_delete: bool = False,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Delete a user account (soft delete by default)."""
    try:
        user_type_id = TypeID.from_string(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    if hard_delete:
        success = await auth_repo.hard_delete_user(user_type_id)
        message = "User permanently deleted"
    else:
        success = await auth_repo.soft_delete_user(user_type_id)
        message = "User deleted successfully"

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return BaseResponseSchema(
        status=200,
        message=message,
        data={"user_id": user_id},
    )


@router.get("/users/search", response_model=BaseResponseSchema)
async def search_users(
    q: str,
    limit: int = 50,
    auth_repo: AuthRepository = Depends(get_auth_repository),
):
    """Search users by username, email, or full name."""
    if not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty",
        )

    users = await auth_repo.search_users(q.strip(), limit=limit)

    # Remove sensitive information
    users_data = []
    for user in users:
        user_data = user.model_dump()
        del user_data["hashed_password"]
        users_data.append(user_data)

    return BaseResponseSchema(
        status=200,
        message="Search completed successfully",
        data={
            "query": q,
            "results": users_data,
            "count": len(users_data),
        },
    )
