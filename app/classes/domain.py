from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import does_not_exist
from app.api.schemas import BaseResponseSchema

from .repository import ClassesRepository, ClassesRequirementRepository
from .schemas import (
    CreateClassesRequirementSchema,
    CreateClassesSchema,
    UpdateClassesRequirementSchema,
    UpdateClassesSchema,
)


@dataclass
class CreateClassesUseCase(ApiDomain):
    payload: CreateClassesSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.create_class(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Classes created successfully",
            data=result,
        )


@dataclass
class ListClassesUseCase(ApiDomain):
    session: AsyncSession

    @cached_property
    def repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.fetch_all()
        return BaseResponseSchema(
            message="Classes retrieved successfully",
            data=result,
        )


@dataclass
class GetClassesUseCase(ApiDomain):
    id_: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.get(id_=self.id_)
        return BaseResponseSchema(
            message="Classes retrieved successfully",
            data=result,
        )


@dataclass
class UpdateClassesUseCase(ApiDomain):
    id_: UUID
    payload: UpdateClassesSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.update_class(self.payload, id_=self.id_)
        return BaseResponseSchema(
            message="Classes updated successfully",
            data=result,
        )


@dataclass
class DeleteClassesUseCase(ApiDomain):
    id_: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        await self.repository.delete(id_=self.id_)
        return BaseResponseSchema(
            message="Classes deleted successfully",
            data=None,
        )


# --- Requirements ---


@dataclass
class CreateClassesRequirementUseCase(ApiDomain):
    class_id: UUID
    payload: CreateClassesRequirementSchema
    session: AsyncSession

    @cached_property
    def class_repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @cached_property
    def repository(self) -> ClassesRequirementRepository:
        return ClassesRequirementRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.class_repository.exists(id_=self.class_id):
            raise does_not_exist("Classes")
        result = await self.repository.create_requirement(
            self.class_id, self.payload
        )
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Requirement created successfully",
            data=result,
        )


@dataclass
class ListClassesRequirementsUseCase(ApiDomain):
    class_id: UUID
    session: AsyncSession

    @cached_property
    def class_repository(self) -> ClassesRepository:
        return ClassesRepository(self.session)

    @cached_property
    def repository(self) -> ClassesRequirementRepository:
        return ClassesRequirementRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.class_repository.exists(id_=self.class_id):
            raise does_not_exist("Classes")
        result = await self.repository.fetch(class_id=self.class_id)
        return BaseResponseSchema(
            message="Requirements retrieved successfully",
            data=result,
        )


@dataclass
class UpdateClassesRequirementUseCase(ApiDomain):
    class_id: UUID
    requirement_id: UUID
    payload: UpdateClassesRequirementSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> ClassesRequirementRepository:
        return ClassesRequirementRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.repository.exists(
            id_=self.requirement_id, class_id=self.class_id
        ):
            raise does_not_exist("ClassesRequirement")
        result = await self.repository.update_requirement(
            self.payload, id_=self.requirement_id
        )
        return BaseResponseSchema(
            message="Requirement updated successfully",
            data=result,
        )


@dataclass
class DeleteClassesRequirementUseCase(ApiDomain):
    class_id: UUID
    requirement_id: UUID
    session: AsyncSession

    @cached_property
    def repository(self) -> ClassesRequirementRepository:
        return ClassesRequirementRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if not await self.repository.exists(
            id_=self.requirement_id, class_id=self.class_id
        ):
            raise does_not_exist("ClassesRequirement")
        await self.repository.delete(id_=self.requirement_id)
        return BaseResponseSchema(
            message="Requirement deleted successfully",
            data=None,
        )
