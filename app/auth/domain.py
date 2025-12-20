from dataclasses import dataclass
from functools import cached_property
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import unauthenticated
from app.api.schemas import BaseResponseSchema

from .handler import sign_jwt
from .repository import UserRepository
from .schemas import BaseUserSchema, CreateUserSchema


@dataclass
class AuthLoginUseCase(ApiDomain):
    payload: BaseUserSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> UserRepository:
        return UserRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        exists = await self.repository.exists(document=self.payload.document)
        if not exists:
            raise unauthenticated()

        user = await self.repository.get(document=self.payload.document)
        if user.birth_date != self.payload.birth_date:
            raise unauthenticated()

        return BaseResponseSchema(
            status=status.HTTP_200_OK,
            message="Login Successful",
            data=await sign_jwt(str(self.payload.document)),
        )


@dataclass
class AuthRegisterUseCase(ApiDomain):
    payload: CreateUserSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> UserRepository:
        return UserRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        exists = await self.repository.exists(document=self.payload.document)
        if exists:
            raise unauthenticated()

        user = await self.repository.create_user(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="User Created",
            data=user,
        )
