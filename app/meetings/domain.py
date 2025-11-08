from dataclasses import dataclass
from functools import cached_property
from typing import override

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
            message="Meeting created successfully inside domain",
            data=result,
        )
