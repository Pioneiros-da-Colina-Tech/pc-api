from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import already_exists, does_not_exist, validation_error
from app.api.schemas import BaseResponseSchema
from app.classes.repository import ClassesRepository
from app.club_year.repository import ClubYearRepository

from .repository import UnitMemberRepository, UnitRepository
from .schemas import AddUnitMemberSchema, CreateUnitSchema, UpdateUnitSchema


@dataclass
class CreateUnitUseCase(ApiDomain):
    payload: CreateUnitSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> UnitRepository:
        return UnitRepository(self.session)

    @cached_property
    def class_repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        class_ = await self.class_repository.get(id_=self.payload.class_id)
        if class_.age != self.payload.age:
            raise validation_error(
                "Unit age must match the class age",
                detail=f"Class '{class_.name}' requires age {class_.age}, got {self.payload.age}",
            )
        result = await self.repository.create_unit(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Unit created successfully",
            data=result,
        )


@dataclass
class ListUnitsUseCase(ApiDomain):
    session: AsyncSession

    @cached_property
    def repository(self) -> UnitRepository:
        return UnitRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.fetch_all()
        return BaseResponseSchema(
            message="Units retrieved successfully",
            data=result,
        )


@dataclass
class GetUnitUseCase(ApiDomain):
    id_: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> UnitRepository:
        return UnitRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.get(id_=self.id_)
        return BaseResponseSchema(
            message="Unit retrieved successfully",
            data=result,
        )


@dataclass
class UpdateUnitUseCase(ApiDomain):
    id_: UUID
    payload: UpdateUnitSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> UnitRepository:
        return UnitRepository(self.session)

    @cached_property
    def class_repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        current = await self.repository.get(id_=self.id_)

        new_age = (
            self.payload.age if self.payload.age is not None else current.age
        )
        new_class_id = (
            self.payload.class_id
            if self.payload.class_id is not None
            else current.class_id
        )

        if new_class_id is not None:
            class_ = await self.class_repository.get(id_=new_class_id)
            if class_.age != new_age:
                raise validation_error(
                    "Unit age must match the class age",
                    detail=f"Class '{class_.name}' requires age {class_.age}, got {new_age}",
                )

        result = await self.repository.update_unit(self.payload, id_=self.id_)
        return BaseResponseSchema(
            message="Unit updated successfully",
            data=result,
        )


@dataclass
class DeleteUnitUseCase(ApiDomain):
    id_: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> UnitRepository:
        return UnitRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        await self.repository.delete(id_=self.id_)
        return BaseResponseSchema(
            message="Unit deleted successfully",
            data=None,
        )


# --- Members ---


@dataclass
class AddUnitMemberUseCase(ApiDomain):
    unit_id: UUID
    payload: AddUnitMemberSchema
    session: AsyncSession

    @cached_property
    def unit_repository(self) -> UnitRepository:
        return UnitRepository(self.session)

    @cached_property
    def repository(self) -> UnitMemberRepository:
        return UnitMemberRepository(self.session)

    @cached_property
    def club_year_repository(self) -> ClubYearRepository:
        return ClubYearRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.unit_repository.exists(id_=self.unit_id):
            raise does_not_exist("Unit")
        if not await self.club_year_repository.exists(id_=self.payload.club_year_id):
            raise does_not_exist(f"ClubYear '{self.payload.club_year_id}'")
        if await self.repository.exists(
            unit_id=self.unit_id,
            user_id=self.payload.user_id,
            club_year_id=self.payload.club_year_id,
        ):
            raise already_exists("UnitMember")
        result = await self.repository.add_member(self.unit_id, self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Member added to unit successfully",
            data=result,
        )


@dataclass
class ListUnitMembersUseCase(ApiDomain):
    unit_id: UUID
    club_year_id: str | None
    session: AsyncSession

    @cached_property
    def unit_repository(self) -> UnitRepository:
        return UnitRepository(self.session)

    @cached_property
    def repository(self) -> UnitMemberRepository:
        return UnitMemberRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.unit_repository.exists(id_=self.unit_id):
            raise does_not_exist("Unit")
        result = await self.repository.list_members(
            self.unit_id, self.club_year_id
        )
        return BaseResponseSchema(
            message="Members retrieved successfully",
            data=result,
        )


@dataclass
class RemoveUnitMemberUseCase(ApiDomain):
    unit_id: UUID
    user_id: UUID
    club_year_id: str
    session: AsyncSession

    @cached_property
    def repository(self) -> UnitMemberRepository:
        return UnitMemberRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.repository.exists(
            unit_id=self.unit_id,
            user_id=self.user_id,
            club_year_id=self.club_year_id,
        ):
            raise does_not_exist("UnitMember")
        await self.repository.remove_member(
            self.unit_id, self.user_id, self.club_year_id
        )
        return BaseResponseSchema(
            message="Member removed from unit successfully",
            data=None,
        )
