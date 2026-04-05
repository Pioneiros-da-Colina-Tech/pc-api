from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import does_not_exist
from app.api.schemas import BaseResponseSchema
from app.auth.repository import UserRepository

from .repository import SpecialtiesRepository, UserSpecialtiesRepository
from .schemas import (
    CreateSpecialtySchema,
    CreateUserSpecialtySchema,
    UpdateSpecialtySchema,
)


@dataclass
class CreateSpecialtyUseCase(ApiDomain):
    payload: CreateSpecialtySchema
    session: AsyncSession

    @cached_property
    def repository(self) -> SpecialtiesRepository:
        return SpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.create_specialty(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Specialty created successfully",
            data=result,
        )


@dataclass
class ListSpecialtiesUseCase(ApiDomain):
    query: str | None
    page: int
    page_size: int
    session: AsyncSession

    @cached_property
    def repository(self) -> SpecialtiesRepository:
        return SpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        items, total = await self.repository.search(
            query=self.query,
            page=self.page,
            page_size=self.page_size,
        )
        return BaseResponseSchema(
            status=status.HTTP_200_OK,
            message="Specialties retrieved successfully",
            data={
                "items": items,
                "total": total,
                "page": self.page,
                "page_size": self.page_size,
            },
        )


@dataclass
class GetSpecialtyUseCase(ApiDomain):
    id_: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> SpecialtiesRepository:
        return SpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.get(id_=self.id_)
        return BaseResponseSchema(
            message="Specialty retrieved successfully",
            data=result,
        )


@dataclass
class UpdateSpecialtyUseCase(ApiDomain):
    id_: UUID
    payload: UpdateSpecialtySchema
    session: AsyncSession

    @cached_property
    def repository(self) -> SpecialtiesRepository:
        return SpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.update_specialty(
            self.payload, id_=self.id_
        )
        return BaseResponseSchema(
            message="Specialty updated successfully",
            data=result,
        )


@dataclass
class DeleteSpecialtyUseCase(ApiDomain):
    id_: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> SpecialtiesRepository:
        return SpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        await self.repository.delete(id_=self.id_)
        return BaseResponseSchema(
            message="Specialty deleted successfully",
            data=None,
        )


# --- User Specialties ---


@dataclass
class AssignSpecialtyToUserUseCase(ApiDomain):
    user_id: UUID
    payload: CreateUserSpecialtySchema
    session: AsyncSession

    @cached_property
    def users_repository(self) -> UserRepository:
        return UserRepository(self.session)

    @cached_property
    def specialties_repository(self) -> SpecialtiesRepository:
        return SpecialtiesRepository(self.session)

    @cached_property
    def repository(self) -> UserSpecialtiesRepository:
        return UserSpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        # Check if user exists
        if not await self.users_repository.exists(id_=self.user_id):
            raise does_not_exist("User")

        # Check if specialty exists
        if not await self.specialties_repository.exists(
            id_=self.payload.specialty_id
        ):
            raise does_not_exist("Specialty")

        result = await self.repository.create_user_specialty(
            self.user_id, self.payload
        )
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Specialty assigned to user successfully",
            data=result,
        )


@dataclass
class ListUserSpecialtiesUseCase(ApiDomain):
    user_id: UUID
    session: AsyncSession

    @cached_property
    def users_repository(self) -> UserRepository:
        return UserRepository(self.session)

    @cached_property
    def repository(self) -> UserSpecialtiesRepository:
        return UserSpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        # Check if user exists
        if not await self.users_repository.exists(id_=self.user_id):
            raise does_not_exist("User")

        result = await self.repository.fetch_user_specialties(self.user_id)
        return BaseResponseSchema(
            message="User specialties retrieved successfully",
            data=result,
        )


@dataclass
class RemoveSpecialtyFromUserUseCase(ApiDomain):
    user_id: UUID
    user_specialty_id: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> UserSpecialtiesRepository:
        return UserSpecialtiesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.repository.exists(
            id_=self.user_specialty_id, user_id=self.user_id
        ):
            raise does_not_exist("UserSpecialty")

        await self.repository.delete(id_=self.user_specialty_id)
        return BaseResponseSchema(
            message="Specialty removed from user successfully",
            data=None,
        )
