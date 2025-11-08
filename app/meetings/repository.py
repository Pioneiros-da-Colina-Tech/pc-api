from datetime import UTC, datetime
from typing import override
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.repository import Repository
from app.meetings.entities import MeetingsEntity
from app.meetings.schemas import CreateMeetingSchema, MeetingsSchema


class MeetingsRepository(Repository[MeetingsEntity, MeetingsSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=MeetingsEntity)

    @override
    def to_entity(self, schema: MeetingsSchema) -> MeetingsEntity:
        return MeetingsEntity(
            id_=schema.id_,
            name=schema.name,
            date=schema.date,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: MeetingsEntity) -> MeetingsSchema:
        return MeetingsSchema(
            id_=entity.id_,
            name=entity.name,
            date=entity.date,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_meeting(self, data: CreateMeetingSchema) -> MeetingsSchema:
        meeting_data = MeetingsSchema(
            id_=uuid4(),
            name=data.name,
            date=data.date,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(meeting_data)
