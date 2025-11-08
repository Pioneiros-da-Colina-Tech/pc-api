from datetime import date as dt
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateMeetingSchema(BaseModel):
    name: str = Field(examples=["Meeting 1"], min_length=2, max_length=100)
    date: dt = Field(examples=[dt(2023, 1, 1)])


class MeetingsSchema(CreateMeetingSchema):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    created_at: datetime = Field(examples=[datetime(2023, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2023, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2023, 1, 1)])
