from uuid import UUID

from pydantic import BaseModel

from .concepts import Role


class RoleSchema(BaseModel):
    id_: str
    label: str


class ScreenSchema(BaseModel):
    id_: str
    label: str


class RoleScreenSchema(BaseModel):
    role_id: str
    screen_id: str


class UserRoleSchema(BaseModel):
    user_id: UUID
    role_id: str


class AssignRoleSchema(BaseModel):
    user_id: UUID
    role_id: Role


class RevokeRoleSchema(BaseModel):
    user_id: UUID
    role_id: Role


class UserPermissionsSchema(BaseModel):
    """Aggregated permissions returned to the frontend."""

    roles: list[str]
    screens: list[str]
