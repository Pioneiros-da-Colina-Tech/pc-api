from dataclasses import dataclass

from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from typeid import TypeID

from app.api.exc.exceptions import (
    FieldError,
    already_exists,
    does_not_exist,
    inactive_user,
    unauthenticated,
    validation_error,
)
from app.api.schemas import BaseResponseSchema

from .repository import AuthRepository
from .schemas import LoginRequestSchema, TokenSchema, UserSchema
from .utils import create_access_token, get_password_hash, verify_password


@dataclass
class RegisterUserUseCase:
    user_data: UserSchema
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        if await self.auth_repo.user_exists(
            username=self.user_data.username, email=self.user_data.email
        ):
            raise already_exists(
                "User",
                (
                    FieldError(name="username", detail=self.user_data.username),
                    FieldError(name="email", detail=self.user_data.email),
                ),
            )

        hashed_password = get_password_hash(self.user_data.password)
        user = await self.auth_repo.create_user(self.user_data, hashed_password)

        return BaseResponseSchema(
            status=201,
            message="User registered successfully",
            data={"user_id": str(user.id_), "username": user.username},
        )


@dataclass
class LoginUserUseCase:
    login_data: LoginRequestSchema
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        form_data = OAuth2PasswordRequestForm(
            username=self.login_data.login, password=self.login_data.password
        )

        user = await self.auth_repo.get_user_by_username(form_data.username)
        logger.info(user)

        if not user or not verify_password(
            form_data.password, user.hashed_password
        ):
            raise unauthenticated()

        if user.disabled:
            raise inactive_user()

        access_token = create_access_token(
            data={"sub": str(user.id_), "username": user.username}
        )

        return BaseResponseSchema(
            status=200,
            message="User logged in successfully",
            data=TokenSchema(access_token=access_token, token_type="bearer"),
        )


@dataclass
class GetUserUseCase:
    user_id: str
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        try:
            user_type_id = TypeID.from_string(self.user_id)
        except ValueError:
            raise validation_error(
                message="Invalid user ID format",
                fields=[
                    FieldError(name="user_id", detail="Invalid TypeID format")
                ],
            )

        user = await self.auth_repo.get_user_by_id(user_type_id)

        if not user:
            raise does_not_exist("User")

        user_data = user.model_dump()
        del user_data["hashed_password"]

        return BaseResponseSchema(
            status=200,
            message="User retrieved successfully",
            data=user_data,
        )


@dataclass
class ListUsersUseCase:
    limit: int
    offset: int
    include_disabled: bool
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        users = await self.auth_repo.list_users(
            limit=self.limit,
            offset=self.offset,
            include_disabled=self.include_disabled,
        )
        total_count = await self.auth_repo.count_users(
            include_disabled=self.include_disabled
        )

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
                    "limit": self.limit,
                    "offset": self.offset,
                    "has_more": self.offset + self.limit < total_count,
                },
            },
        )


@dataclass
class DisableUserUseCase:
    user_id: str
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        try:
            user_type_id = TypeID.from_string(self.user_id)
        except ValueError:
            raise validation_error(
                message="Invalid user ID format",
                fields=[
                    FieldError(name="user_id", detail="Invalid TypeID format")
                ],
            )

        success = await self.auth_repo.disable_user(user_type_id)

        if not success:
            raise does_not_exist("User")

        return BaseResponseSchema(
            status=200,
            message="User disabled successfully",
            data={"user_id": self.user_id},
        )


@dataclass
class EnableUserUseCase:
    user_id: str
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        try:
            user_type_id = TypeID.from_string(self.user_id)
        except ValueError:
            raise validation_error(
                message="Invalid user ID format",
                fields=[
                    FieldError(name="user_id", detail="Invalid TypeID format")
                ],
            )

        success = await self.auth_repo.enable_user(user_type_id)

        if not success:
            raise does_not_exist("User")

        return BaseResponseSchema(
            status=200,
            message="User enabled successfully",
            data={"user_id": self.user_id},
        )


@dataclass
class DeleteUserUseCase:
    user_id: str
    hard_delete: bool
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        try:
            user_type_id = TypeID.from_string(self.user_id)
        except ValueError:
            raise validation_error(
                message="Invalid user ID format",
                fields=[
                    FieldError(name="user_id", detail="Invalid TypeID format")
                ],
            )

        if self.hard_delete:
            success = await self.auth_repo.hard_delete_user(user_type_id)
            message = "User permanently deleted"
        else:
            success = await self.auth_repo.soft_delete_user(user_type_id)
            message = "User deleted successfully"

        if not success:
            raise does_not_exist("User")

        return BaseResponseSchema(
            status=200,
            message=message,
            data={"user_id": self.user_id},
        )


@dataclass
class SearchUsersUseCase:
    query: str
    limit: int
    auth_repo: AuthRepository

    async def execute(self) -> BaseResponseSchema:
        if not self.query.strip():
            raise validation_error(
                message="Search query cannot be empty",
                fields=[
                    FieldError(name="query", detail="Query string is required")
                ],
            )

        users = await self.auth_repo.search_users(
            self.query.strip(), limit=self.limit
        )

        users_data = []
        for user in users:
            user_data = user.model_dump()
            del user_data["hashed_password"]
            users_data.append(user_data)

        return BaseResponseSchema(
            status=200,
            message="Search completed successfully",
            data={
                "query": self.query,
                "results": users_data,
                "count": len(users_data),
            },
        )
