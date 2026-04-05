from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

# --- Classes ---


class CreateClassesSchema(BaseModel):
    name: str = Field(examples=["Amigo"], min_length=2, max_length=100)
    age: int = Field(examples=[10], ge=1, le=99)


class UpdateClassesSchema(BaseModel):
    name: str | None = Field(
        default=None, examples=["Amigo"], min_length=2, max_length=100
    )
    age: int | None = Field(default=None, examples=[10], ge=1, le=99)


class ClassesSchema(CreateClassesSchema):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    created_at: datetime = Field(examples=[datetime(2024, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])


# --- ClassesRequirement ---


class CreateClassesRequirementSchema(BaseModel):
    section: str = Field(examples=["I. GERAIS"], min_length=1, max_length=100)
    order_num: int = Field(examples=[1], ge=1)
    description: str = Field(examples=["Ter, no mínimo, 10 anos de idade."])


class UpdateClassesRequirementSchema(BaseModel):
    section: str | None = Field(
        default=None, examples=["I. GERAIS"], min_length=1, max_length=100
    )
    order_num: int | None = Field(default=None, examples=[1], ge=1)
    description: str | None = Field(
        default=None, examples=["Ter, no mínimo, 10 anos de idade."]
    )


class ClassesRequirementSchema(CreateClassesRequirementSchema):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    class_id: UUID = Field(
        examples=[UUID("123e4567-e89b-12d3-a456-426614174000")]
    )
    created_at: datetime = Field(examples=[datetime(2024, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2024, 1, 1)])
