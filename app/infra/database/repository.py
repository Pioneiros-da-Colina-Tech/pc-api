from dataclasses import dataclass
from typing import Any

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.exc import does_not_exist, validation_error

from .entities import Entity


@dataclass
class Repository[T: Entity, S: BaseModel]:
    """
    Generic repository for database entities.

    This is an agnostic repository that can be used with any entity and schema.
    It provides CRUD operations and common query methods.

    Type Parameters:
        T: The entity type (must inherit from Entity)
        S: The schema type (must inherit from BaseModel)
    """

    context: AsyncSession
    entity: type[T]

    def to_schema(self, entity: T) -> S:
        """Converts an entity to a schema."""
        raise NotImplementedError(entity)

    def to_entity(self, schema: S) -> T:
        """Converts a schema to an entity."""
        raise NotImplementedError(schema)

    async def get(self, **filters: Any) -> S:
        """
        Get a single entity by filters.

        Args:
            **filters: Column name and value pairs to filter by

        Returns:
            The schema representation of the entity

        Raises:
            HTTPException: If entity does not exist

        Example:
            >>> await repository.get(id_=user_id)
            >>> await repository.get(email="user@example.com")
        """
        statement = sa.select(self.entity).filter_by(**filters).limit(1)

        result = await self.context.execute(statement)
        first = result.scalars().first()

        if first is None:
            raise does_not_exist(self.entity.__name__.removesuffix("Entity"))

        return self.to_schema(first)

    async def fetch(self, **filters: Any) -> list[S]:
        """
        Fetch multiple entities by filters.

        Args:
            **filters: Column name and value pairs to filter by

        Returns:
            List of schema representations of the entities

        Example:
            >>> await repository.fetch(active=True)
            >>> await repository.fetch(role="admin", active=True)
        """
        statement = sa.select(self.entity).filter_by(**filters)

        result = await self.context.execute(statement)
        return [self.to_schema(entity) for entity in result.scalars().all()]

    async def fetch_all(self) -> list[S]:
        """
        Fetch all entities without filters.

        Returns:
            List of schema representations of all entities

        Example:
            >>> await repository.fetch_all()
        """
        statement = sa.select(self.entity)

        result = await self.context.execute(statement)
        return [self.to_schema(entity) for entity in result.scalars().all()]

    async def fetch_paginated(
        self, index: int = 0, index_size: int = 10, **filters: Any
    ) -> list[S]:
        """
        Fetch entities with pagination.

        Args:
            index: Page index (0-based)
            index_size: Number of items per page
            **filters: Column name and value pairs to filter by

        Returns:
            List of schema representations of the entities for the requested page

        Example:
            >>> await repository.fetch_paginated(index=0, index_size=20)
            >>> await repository.fetch_paginated(index=1, index_size=10, active=True)
        """
        offset = index * index_size
        statement = (
            sa.select(self.entity)
            .filter_by(**filters)
            .order_by(*self.entity.__mapper__.primary_key)
            .offset(offset)
            .limit(index_size)
        )

        result = await self.context.execute(statement)
        return [self.to_schema(entity) for entity in result.scalars().all()]

    async def create(self, schema: S) -> S:
        """
        Create a new entity.

        Args:
            schema: The schema with data to create the entity

        Returns:
            The created entity as a schema

        Example:
            >>> user_data = UserSchema(name="John", email="john@example.com")
            >>> await repository.create(user_data)
        """
        entity = self.to_entity(schema)
        self.context.add(entity)
        await self.context.flush()
        await self.context.refresh(entity)
        return self.to_schema(entity)

    async def update(self, schema: S, **filters: Any) -> S:
        """
        Update an entity by filters.

        Args:
            schema: The schema with updated data
            **filters: Column name and value pairs to identify the entity

        Returns:
            The updated entity as a schema

        Raises:
            HTTPException: If entity does not exist or multiple entities match

        Example:
            >>> updated_data = UserSchema(name="John Updated", email="john@example.com")
            >>> await repository.update(updated_data, id_=user_id)
        """
        update_values = schema.model_dump(exclude_unset=True)

        statement = (
            sa.update(self.entity)
            .filter_by(**filters)
            .values(**update_values)
            .returning(self.entity)
        )

        result = await self.context.execute(statement)
        updated = result.scalars().first()

        if updated is None:
            raise does_not_exist(self.entity.__name__.removesuffix("Entity"))

        return self.to_schema(updated)

    async def delete(self, **filters: Any) -> None:
        """
        Delete an entity by filters.

        Args:
            **filters: Column name and value pairs to identify the entity

        Raises:
            HTTPException: If entity does not exist or multiple entities match

        Example:
            >>> await repository.delete(id_=user_id)
        """
        # First, check if entity exists and get count
        count_stmt = (
            sa.select(sa.func.count())
            .select_from(self.entity)
            .filter_by(**filters)
        )
        count_result = await self.context.execute(count_stmt)
        count = count_result.scalar_one()

        if count == 0:
            raise does_not_exist(self.entity.__name__.removesuffix("Entity"))

        if count > 1:
            raise validation_error(
                "Multiple entities found, expected only one."
            )

        # Now perform the delete
        statement = sa.delete(self.entity).filter_by(**filters)
        _ = await self.context.execute(statement)

    async def count(self, **filters: Any) -> int:
        """
        Count entities by filters.

        Args:
            **filters: Column name and value pairs to filter by

        Returns:
            The count of matching entities

        Example:
            >>> await repository.count(active=True)
        """
        statement = (
            sa.select(sa.func.count())
            .select_from(self.entity)
            .filter_by(**filters)
        )

        result = await self.context.execute(statement)
        return result.scalar_one()

    async def exists(self, **filters: Any) -> bool:
        """
        Check if an entity exists by filters.

        Args:
            **filters: Column name and value pairs to filter by

        Returns:
            True if entity exists, False otherwise

        Example:
            >>> await repository.exists(email="john@example.com")
        """
        statement = sa.select(
            sa.exists().where(
                sa.and_(
                    *[getattr(self.entity, k) == v for k, v in filters.items()]
                )
            )
        )

        result = await self.context.execute(statement)
        return result.scalar_one()
