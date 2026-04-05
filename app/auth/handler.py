from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from app.infra.database.adapter import SessionContext
from app.settings import auth_settings

from .repository import UserRepository
from .schemas import AuthTokenDataSchema, AuthTokenResponseSchema, UserSchema

SECRET_KEY = auth_settings.AUTH_SECRET_KEY
ALGORITHM = auth_settings.AUTH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = auth_settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES

security = HTTPBearer()

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def sign_jwt(document: str) -> AuthTokenResponseSchema:
    """Create a signed JWT token for the given document."""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": document}, expires_delta=access_token_expires
    )
    return AuthTokenResponseSchema(
        access_token=access_token, token_type="bearer"
    )


async def decode_token(token: str) -> AuthTokenDataSchema:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        document: str | None = payload.get("sub")
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return AuthTokenDataSchema(document=document)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: SessionContext,
) -> UserSchema:
    """
    Extract and validate the current user from JWT token.

    Args:
        credentials: HTTP Authorization credentials containing the Bearer token
        session: Database session context

    Returns:
        UserSchema: The current authenticated user

    Raises:
        HTTPException: If token is invalid or user doesn't exist
    """

    token_data = await decode_token(credentials.credentials)
    repository = UserRepository(session)

    try:
        user = await repository.get(document=token_data.document)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_document(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """
    Extract just the user document from JWT token without database lookup.
    Useful when you only need the user identifier.

    Args:
        credentials: HTTP Authorization credentials containing the Bearer token

    Returns:
        str: The user document (CPF) from the token

    Raises:
        HTTPException: If token is invalid
    """
    token_data = await decode_token(credentials.credentials)
    return token_data.document


CurrentUser = Annotated[UserSchema, Depends(get_current_user_from_token)]
CurrentUserDocument = Annotated[str, Depends(get_current_user_document)]
AuthDependency = Annotated[HTTPAuthorizationCredentials, Depends(security)]
