from datetime import UTC, datetime
from typing import Any, override
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exc import does_not_exist
from app.infra.database.repository import Repository

from .entities import ClassesEntity, ClassesRequirementEntity
from .schemas import (
    ClassesRequirementSchema,
    ClassesSchema,
    CreateClassesRequirementSchema,
    CreateClassesSchema,
    UpdateClassesRequirementSchema,
    UpdateClassesSchema,
)


class ClassesRepository(Repository[ClassesEntity, ClassesSchema]):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=ClassesEntity)

    @override
    def to_entity(self, schema: ClassesSchema) -> ClassesEntity:
        return ClassesEntity(
            id_=schema.id_,
            name=schema.name,
            age=schema.age,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(self, entity: ClassesEntity) -> ClassesSchema:
        return ClassesSchema(
            id_=entity.id_,
            name=entity.name,
            age=entity.age,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_class(self, data: CreateClassesSchema) -> ClassesSchema:
        class_ = ClassesSchema(
            id_=uuid4(),
            name=data.name,
            age=data.age,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(class_)

    async def update_class(
        self, data: UpdateClassesSchema, **filters: Any
    ) -> ClassesSchema:
        statement = (
            sa.update(ClassesEntity)
            .filter_by(**filters)
            .values(**data.model_dump(exclude_unset=True))
            .returning(ClassesEntity)
        )
        result = await self.context.execute(statement)
        updated = result.scalars().first()
        if updated is None:
            raise does_not_exist("Classes")
        return self.to_schema(updated)


class ClassesRequirementRepository(
    Repository[ClassesRequirementEntity, ClassesRequirementSchema]
):
    def __init__(self, session: AsyncSession):
        super().__init__(context=session, entity=ClassesRequirementEntity)

    @override
    def to_entity(
        self, schema: ClassesRequirementSchema
    ) -> ClassesRequirementEntity:
        return ClassesRequirementEntity(
            id_=schema.id_,
            class_id=schema.class_id,
            section=schema.section,
            order_num=schema.order_num,
            description=schema.description,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
            deleted_at=schema.deleted_at,
        )

    @override
    def to_schema(
        self, entity: ClassesRequirementEntity
    ) -> ClassesRequirementSchema:
        return ClassesRequirementSchema(
            id_=entity.id_,
            class_id=entity.class_id,
            section=entity.section,
            order_num=entity.order_num,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )

    async def create_requirement(
        self, class_id: UUID, data: CreateClassesRequirementSchema
    ) -> ClassesRequirementSchema:
        requirement = ClassesRequirementSchema(
            id_=uuid4(),
            class_id=class_id,
            section=data.section,
            order_num=data.order_num,
            description=data.description,
            created_at=datetime.now(UTC),
            updated_at=None,
            deleted_at=None,
        )
        return await self.create(requirement)

    async def update_requirement(
        self, data: UpdateClassesRequirementSchema, **filters: Any
    ) -> ClassesRequirementSchema:
        statement = (
            sa.update(ClassesRequirementEntity)
            .filter_by(**filters)
            .values(**data.model_dump(exclude_unset=True))
            .returning(ClassesRequirementEntity)
        )
        result = await self.context.execute(statement)
        updated = result.scalars().first()
        if updated is None:
            raise does_not_exist("ClassesRequirement")
        return self.to_schema(updated)
