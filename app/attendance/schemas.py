from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .concepts import AttendanceStatus


class RecordAttendanceSchema(BaseModel):
    user_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    attendance_status: AttendanceStatus = Field(
        examples=[AttendanceStatus.PRESENTE]
    )


class UpdateAttendanceSchema(BaseModel):
    attendance_status: AttendanceStatus = Field(
        examples=[AttendanceStatus.PRESENTE]
    )


class AttendanceSchema(BaseModel):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    meeting_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    user_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    attendance_status: AttendanceStatus
    created_at: datetime = Field(examples=[datetime(2024, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
