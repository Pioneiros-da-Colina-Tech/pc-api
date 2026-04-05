from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# --- Specialties ---


class CreateSpecialtySchema(BaseModel):
    code: str = Field(
        examples=["EN-001"], min_length=2, max_length=20, description="MD code"
    )
    name: str = Field(examples=["Acampamento"], min_length=2, max_length=200)


class UpdateSpecialtySchema(BaseModel):
    code: str | None = Field(
        default=None,
        examples=["EN-001"],
        min_length=2,
        max_length=20,
        description="MD code",
    )
    name: str | None = Field(
        default=None, examples=["Acampamento"], min_length=2, max_length=200
    )


class SpecialtySchema(CreateSpecialtySchema):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    created_at: datetime = Field(examples=[datetime(2024, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])


# --- UserSpecialties ---


class CreateUserSpecialtySchema(BaseModel):
    specialty_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )


class UserSpecialtySchema(BaseModel):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    user_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    specialty_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    created_at: datetime = Field(examples=[datetime(2024, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])


