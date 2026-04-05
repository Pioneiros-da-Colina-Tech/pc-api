from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from .concepts import UnitRole

# --- Unit ---


class CreateUnitSchema(BaseModel):
    name: str = Field(examples=["Águias"], min_length=2, max_length=100)
    age: int = Field(examples=[10], ge=1, le=99)
    class_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )


class UpdateUnitSchema(BaseModel):
    name: str | None = Field(
        default=None, examples=["Águias"], min_length=2, max_length=100
    )
    age: int | None = Field(default=None, examples=[10], ge=1, le=99)
    class_id: UUID | None = Field(
        default=None, examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )


class UnitSchema(BaseModel):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    name: str
    age: int
    class_id: UUID | None
    created_at: datetime = Field(examples=[datetime(2024, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])


# --- UnitMember ---


class AddUnitMemberSchema(BaseModel):
    user_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    club_year_id: str = Field(examples=["2024"])
    role: UnitRole = Field(examples=[UnitRole.MEMBRO])


class UnitMemberSchema(BaseModel):
    unit_id: UUID
    user_id: UUID
    club_year_id: str
    role: UnitRole
    created_at: datetime
    updated_at: datetime | None
    deleted_at: datetime | None
