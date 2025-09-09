from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)
from typeid.typeid import TypeID


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenResponseSchema(BaseModel):
    username: str | None = None


class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    name: str
    sgc_code: str | None = None
    disabled: bool = False


class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id_: TypeID = Field(..., description="Unique user identifier")
    username: str
    email: str
    hashed_password: str
    full_name: str
    disabled: bool = False
    sgc_code: str
    created_at: datetime
    updated_at: datetime

    @field_validator("id_", mode="before")
    @classmethod
    def validate_id(cls, v: Any) -> TypeID:
        """Validate and convert TypeID."""
        if isinstance(v, TypeID):
            return v
        if isinstance(v, str):
            return TypeID.from_string(v)
        raise ValueError(f"Invalid TypeID format: {v}")

    @field_serializer("id_")
    def serialize_id(self, value: TypeID) -> str:
        """Serialize TypeID to string."""
        return str(value)
