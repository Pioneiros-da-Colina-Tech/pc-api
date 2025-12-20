from datetime import UTC, datetime
from typing import override
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.entities import UsersEntity
from app.auth.schemas import CreateUserSchema, UserSchema
from app.infra.database.repository import Repository


class UserRepository(Repository[UsersEntity, UserSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=UsersEntity)

    @override
    def to_entity(self, schema: UserSchema) -> UsersEntity:
        return UsersEntity(
            id_=schema.id_,
            document=schema.document,
            birth_date=schema.birth_date,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: UsersEntity) -> UserSchema:
        return UserSchema(
            id_=entity.id_,
            document=entity.document,
            birth_date=entity.birth_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_user(self, data: CreateUserSchema) -> UserSchema:
        user_data = UserSchema(
            id_=uuid4(),
            document=data.document,
            birth_date=data.birth_date,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(user_data)
