from dataclasses import dataclass
from functools import cached_property
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.exc import already_exists
from app.api.schemas import BaseResponseSchema

from .repository import ClubYearRepository
from .schemas import CreateClubYearSchema


@dataclass
class CreateClubYearUseCase(ApiDomain):
    payload: CreateClubYearSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> ClubYearRepository:
        return ClubYearRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if await self.repository.exists(id_=self.payload.id_):
            raise already_exists("ClubYear")
        result = await self.repository.create_club_year(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Club year created successfully",
            data=result,
        )


@dataclass
class ListClubYearsUseCase(ApiDomain):
    session: AsyncSession

    @cached_property
    def repository(self) -> ClubYearRepository:
        return ClubYearRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.fetch_all()
        return BaseResponseSchema(
            message="Club years retrieved successfully",
            data=result,
        )


@dataclass
class GetClubYearUseCase(ApiDomain):
    id_: str
    session: AsyncSession

    @cached_property
    def repository(self) -> ClubYearRepository:
        return ClubYearRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.get(id_=self.id_)
        return BaseResponseSchema(
            message="Club year retrieved successfully",
            data=result,
        )


@dataclass
class DeleteClubYearUseCase(ApiDomain):
    id_: str
    session: AsyncSession

    @cached_property
    def repository(self) -> ClubYearRepository:
        return ClubYearRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        await self.repository.delete(id_=self.id_)
        return BaseResponseSchema(
            message="Club year deleted successfully",
            data=None,
        )
