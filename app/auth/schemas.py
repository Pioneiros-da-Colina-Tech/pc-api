from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Form
from pydantic import BaseModel, Field
from pydantic_br import CPFDigits


class BaseUserSchema(BaseModel):
    document: CPFDigits = Field(examples=["12345678901"])
    birth_date: date = Field(examples=[date(1990, 1, 1)])


class CreateUserSchema(BaseUserSchema):
    name: str = Field(examples=["João Silva"], min_length=2, max_length=255)


class UserSchema(BaseUserSchema):
    id_: UUID = Field(examples=[UUID("123e4567-e89b-12d3-a456-426614174000")])
    name: str | None = Field(default=None, examples=["João Silva"])
    codigo_sgc: str | None = Field(default=None, examples=["12345"])
    created_at: datetime = Field(examples=[datetime(2023, 1, 1)])
    updated_at: datetime | None = Field(examples=[datetime(2023, 1, 1)])
    deleted_at: datetime | None = Field(examples=[datetime(2023, 1, 1)])


class UserWithUnitSchema(UserSchema):
    """UserSchema enriched with current unit assignment (nullable)."""

    unit_id: UUID | None = None
    unit_name: str | None = None
    unit_role: str | None = None


class UpdateUserSchema(BaseModel):
    name: str = Field(examples=["João Silva"], min_length=2, max_length=255)
    codigo_sgc: str | None = Field(default=None, examples=["12345"])


class AuthTokenResponseSchema(BaseModel):
    """Token response schema for API responses."""

    access_token: str
    token_type: str


class AuthTokenDataSchema(BaseModel):
    document: str


class AuthJwtPayloadSchema(BaseModel):
    """JWT payload schema for API responses."""

    sub: str
    iat: int
    exp: int


AuthLoginForm = Annotated[BaseUserSchema, Form()]
AuthLoginRequestForm = Annotated[BaseUserSchema, Depends()]
