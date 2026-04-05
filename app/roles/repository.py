from typing import override
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database.repository import Repository

from .entities import RoleEntity, RoleScreenEntity, ScreenEntity, UserRoleEntity
from .schemas import RoleSchema, RoleScreenSchema, ScreenSchema, UserRoleSchema


class RoleRepository(Repository[RoleEntity, RoleSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=RoleEntity)

    @override
    def to_schema(self, entity: RoleEntity) -> RoleSchema:
        return RoleSchema(id_=entity.id_, label=entity.label)

    @override
    def to_entity(self, schema: RoleSchema) -> RoleEntity:
        return RoleEntity(id_=schema.id_, label=schema.label)


class ScreenRepository(Repository[ScreenEntity, ScreenSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=ScreenEntity)

    @override
    def to_schema(self, entity: ScreenEntity) -> ScreenSchema:
        return ScreenSchema(id_=entity.id_, label=entity.label)

    @override
    def to_entity(self, schema: ScreenSchema) -> ScreenEntity:
        return ScreenEntity(id_=schema.id_, label=schema.label)


class RoleScreenRepository(Repository[RoleScreenEntity, RoleScreenSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=RoleScreenEntity)

    @override
    def to_schema(self, entity: RoleScreenEntity) -> RoleScreenSchema:
        return RoleScreenSchema(
            role_id=entity.role_id, screen_id=entity.screen_id
        )

    @override
    def to_entity(self, schema: RoleScreenSchema) -> RoleScreenEntity:
        return RoleScreenEntity(
            role_id=schema.role_id, screen_id=schema.screen_id
        )

    async def get_screens_for_roles(self, role_ids: list[str]) -> list[str]:
        """Return distinct screen IDs accessible to any of the given roles."""
        if not role_ids:
            return []
        statement = (
            sa.select(RoleScreenEntity.screen_id)
            .where(RoleScreenEntity.role_id.in_(role_ids))
            .distinct()
        )
        result = await self.context.execute(statement)
        return list(result.scalars().all())


class UserRoleRepository(Repository[UserRoleEntity, UserRoleSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=UserRoleEntity)

    @override
    def to_schema(self, entity: UserRoleEntity) -> UserRoleSchema:
        return UserRoleSchema(user_id=entity.user_id, role_id=entity.role_id)

    @override
    def to_entity(self, schema: UserRoleSchema) -> UserRoleEntity:
        return UserRoleEntity(user_id=schema.user_id, role_id=schema.role_id)

    async def get_roles_for_user(self, user_id: UUID) -> list[str]:
        """Return role IDs assigned to a user."""
        statement = sa.select(UserRoleEntity.role_id).where(
            UserRoleEntity.user_id == user_id
        )
        result = await self.context.execute(statement)
        return list(result.scalars().all())

    async def assign(self, user_id: UUID, role_id: str) -> UserRoleSchema:
        schema = UserRoleSchema(user_id=user_id, role_id=role_id)
        return await self.create(schema)

    async def revoke(self, user_id: UUID, role_id: str) -> None:
        statement = sa.delete(UserRoleEntity).where(
            UserRoleEntity.user_id == user_id,
            UserRoleEntity.role_id == role_id,
        )
        _ = await self.context.execute(statement)
