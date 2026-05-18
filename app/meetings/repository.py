from datetime import UTC, datetime
from typing import override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.repository import Repository
from app.meetings.entities import MeetingsEntity
from app.meetings.schemas import CreateMeetingSchema, MeetingsSchema, UpdateMeetingSchema


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

    async def update_meeting(self, meeting_id: UUID, data: UpdateMeetingSchema) -> MeetingsSchema:
        current = await self.get(id_=meeting_id)
        patch = data.model_dump(exclude_unset=True)
        updated = current.model_copy(update={**patch, "updated_at": datetime.now(UTC)})
        return await self.update(updated, id_=meeting_id)

    async def fetch_meetings_for_user(
        self, user_id: UUID
    ) -> list[MeetingsSchema]:
        """Fetch meetings where a specific user has attendance/score records."""
        from app.scores.entities import MeetingScoreEntity

        # Join meetings with scores to get only meetings where user participated
        statement = (
            sa.select(MeetingsEntity)
            .join(
                MeetingScoreEntity,
                MeetingsEntity.id_ == MeetingScoreEntity.meeting_id,
            )
            .where(MeetingScoreEntity.user_id == user_id)
            .distinct()
        )

        result = await self.context.execute(statement)
        return [self.to_schema(entity) for entity in result.scalars().all()]
