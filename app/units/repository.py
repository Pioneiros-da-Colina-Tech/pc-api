from datetime import UTC, datetime
from typing import Any, override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exc import does_not_exist
from app.infra.database.repository import Repository

from app.auth.entities import UsersEntity

from .concepts import UnitRole
from .entities import UnitEntity, UnitMemberEntity
from .schemas import (
    AddUnitMemberSchema,
    CreateUnitSchema,
    UnitMemberSchema,
    UnitMemberWithUserSchema,
    UnitSchema,
    UpdateUnitSchema,
)


class UnitRepository(Repository[UnitEntity, UnitSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=UnitEntity)

    @override
    def to_entity(self, schema: UnitSchema) -> UnitEntity:
        return UnitEntity(
            id_=schema.id_,
            name=schema.name,
            age=schema.age,
            class_id=schema.class_id,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: UnitEntity) -> UnitSchema:
        return UnitSchema(
            id_=entity.id_,
            name=entity.name,
            age=entity.age,
            class_id=entity.class_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_unit(self, data: CreateUnitSchema) -> UnitSchema:
        unit = UnitSchema(
            id_=uuid4(),
            name=data.name,
            age=data.age,
            class_id=data.class_id,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(unit)

    async def update_unit(
        self, data: UpdateUnitSchema, **filters: Any
    ) -> UnitSchema:
        statement = (
            sa.update(UnitEntity)
            .filter_by(**filters)
            .values(
                **data.model_dump(exclude_unset=True),
                updated_at=datetime.now(UTC),
            )
            .returning(UnitEntity)
        )
        result = await self.context.execute(statement)
        updated = result.scalars().first()
        if updated is None:
            raise does_not_exist("Unit")
        return self.to_schema(updated)


class UnitMemberRepository(Repository[UnitMemberEntity, UnitMemberSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=UnitMemberEntity)

    @override
    def to_entity(self, schema: UnitMemberSchema) -> UnitMemberEntity:
        return UnitMemberEntity(
            unit_id=schema.unit_id,
            user_id=schema.user_id,
            club_year_id=schema.club_year_id,
            role=schema.role,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: UnitMemberEntity) -> UnitMemberSchema:
        return UnitMemberSchema(
            unit_id=entity.unit_id,
            user_id=entity.user_id,
            club_year_id=entity.club_year_id,
            role=UnitRole(entity.role),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def add_member(
        self, unit_id: UUID, data: AddUnitMemberSchema
    ) -> UnitMemberSchema:
        member = UnitMemberSchema(
            unit_id=unit_id,
            user_id=data.user_id,
            club_year_id=data.club_year_id,
            role=data.role,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(member)

    async def remove_member(
        self, unit_id: UUID, user_id: UUID, club_year_id: str
    ) -> None:
        statement = sa.delete(UnitMemberEntity).where(
            UnitMemberEntity.unit_id == unit_id,
            UnitMemberEntity.user_id == user_id,
            UnitMemberEntity.club_year_id == club_year_id,
        )
        _ = await self.context.execute(statement)

    async def list_members(
        self, unit_id: UUID, club_year_id: str | None = None
    ) -> list[UnitMemberWithUserSchema]:
        statement = (
            sa.select(
                UnitMemberEntity,
                UsersEntity.name.label("user_name"),
                UsersEntity.document.label("user_document"),
                UsersEntity.codigo_sgc.label("user_codigo_sgc"),
            )
            .join(UsersEntity, UsersEntity.id_ == UnitMemberEntity.user_id)
            .where(UnitMemberEntity.unit_id == unit_id)
        )
        if club_year_id is not None:
            statement = statement.where(
                UnitMemberEntity.club_year_id == club_year_id
            )
        result = await self.context.execute(statement)
        rows = result.all()
        return [
            UnitMemberWithUserSchema(
                unit_id=row.UnitMemberEntity.unit_id,
                user_id=row.UnitMemberEntity.user_id,
                club_year_id=row.UnitMemberEntity.club_year_id,
                role=UnitRole(row.UnitMemberEntity.role),
                created_at=row.UnitMemberEntity.created_at,
                updated_at=row.UnitMemberEntity.updated_at,
                deleted_at=row.UnitMemberEntity.deleted_at,
                user_name=row.user_name,
                user_document=row.user_document,
                user_codigo_sgc=row.user_codigo_sgc,
            )
            for row in rows
        ]
