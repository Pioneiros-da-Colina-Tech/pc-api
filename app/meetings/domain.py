from dataclasses import dataclass
from functools import cached_property
from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.domain import ApiDomain
from app.api.schemas import BaseResponseSchema

from .repository import MeetingsRepository
from .schemas import CreateMeetingSchema


@dataclass
class CreateMeetingUseCase(ApiDomain):
    payload: CreateMeetingSchema
    session: AsyncSession

    @cached_property
    def repository(self) -> MeetingsRepository:
        return MeetingsRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        result = await self.repository.create_meeting(self.payload)
        return BaseResponseSchema(
            status=status.HTTP_201_CREATED,
            message="Meeting created successfully",
            data=result,
        )


@dataclass
class ListMeetingsUseCase(ApiDomain):
    session: AsyncSession
    user_id: UUID | None = None

    @cached_property
    def repository(self) -> MeetingsRepository:
        return MeetingsRepository(self.session)

    @override
    async def execute(self) -> BaseResponseSchema:
        if self.user_id:
            result = await self.repository.fetch_meetings_for_user(self.user_id)
        else:
            result = await self.repository.fetch_all()
        return BaseResponseSchema(
            message="Meetings retrieved successfully",
            data=result,
        )
