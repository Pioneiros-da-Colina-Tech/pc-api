from datetime import UTC, datetime
from typing import override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exc import does_not_exist
from app.infra.database.repository import Repository

from .concepts import AttendanceStatus
from .entities import AttendanceEntity
from .schemas import (
    AttendanceSchema,
    RecordAttendanceSchema,
    UpdateAttendanceSchema,
)


class AttendanceRepository(Repository[AttendanceEntity, AttendanceSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=AttendanceEntity)

    @override
    def to_entity(self, schema: AttendanceSchema) -> AttendanceEntity:
        return AttendanceEntity(
            id_=schema.id_,
            meeting_id=schema.meeting_id,
            user_id=schema.user_id,
            attendance_status=schema.attendance_status,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: AttendanceEntity) -> AttendanceSchema:
        return AttendanceSchema(
            id_=entity.id_,
            meeting_id=entity.meeting_id,
            user_id=entity.user_id,
            attendance_status=AttendanceStatus(entity.attendance_status),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def record_attendance(
        self, meeting_id: UUID, data: RecordAttendanceSchema
    ) -> AttendanceSchema:
        record = AttendanceSchema(
            id_=uuid4(),
            meeting_id=meeting_id,
            user_id=data.user_id,
            attendance_status=data.attendance_status,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(record)

    async def update_attendance(
        self, meeting_id: UUID, user_id: UUID, data: UpdateAttendanceSchema
    ) -> AttendanceSchema:
        statement = (
            sa.update(AttendanceEntity)
            .where(
                AttendanceEntity.meeting_id == meeting_id,
                AttendanceEntity.user_id == user_id,
            )
            .values(
                attendance_status=data.attendance_status,
                updated_at=datetime.now(UTC),
            )
            .returning(AttendanceEntity)
        )
        result = await self.context.execute(statement)
        updated = result.scalars().first()
        if updated is None:
            raise does_not_exist("Attendance")
        return self.to_schema(updated)

    async def list_by_meeting(self, meeting_id: UUID) -> list[AttendanceSchema]:
        statement = sa.select(AttendanceEntity).where(
            AttendanceEntity.meeting_id == meeting_id
        )
        result = await self.context.execute(statement)
        return [self.to_schema(e) for e in result.scalars().all()]
