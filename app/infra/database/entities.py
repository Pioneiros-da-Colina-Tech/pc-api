from datetime import UTC, datetime
from typing import Any, ClassVar, NewType, final, override
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from typeid import TypeID

from app.api.utils import to_snake

from .adapter import metadata

Text = NewType("Text", str)


@final
class GUID(sa.types.TypeDecorator[UUID]):
    impl = sa.UUID()
    cache_ok = True

    @override
    def process_bind_param(
        self, value: UUID | str | None, dialect: sa.engine.Dialect
    ) -> str | None:
        return str(value) if value is not None else None

    @override
    def process_result_value(
        self, value: str | UUID | None, dialect: sa.engine.Dialect
    ) -> UUID | None:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return UUID(value)


@final
class UID(sa.types.TypeDecorator[TypeID]):
    """Custom GUID type for SQLAlchemy."""

    impl = sa.Text()
    cache_ok = True

    @override
    def process_bind_param(
        self, value: TypeID | str | None, dialect: sa.engine.Dialect
    ) -> str | None:
        if value is None:
            return None
        return str(value)

    @override
    def process_result_value(
        self, value: str | None, dialect: sa.engine.Dialect
    ) -> TypeID | None:
        if value is None:
            return None
        return TypeID.from_string(value)


class Entity(DeclarativeBase):
    """Base class for all ORM entities, using shared metadata."""

    type_annotation_map: ClassVar[dict[Any, Any]] = {
        str: sa.String(255),
        Text: sa.Text(),
        datetime: sa.TIMESTAMP(timezone=True),
        UUID: GUID(),
        TypeID: UID(),
    }

    metadata: ClassVar[sa.MetaData] = metadata

    @declared_attr.directive
    def __tablename__(cls):
        """Return the table name for the entity."""
        return to_snake(cls.__name__).lower().removesuffix("_entity")


class TimestampMixin:
    """Mixin class to add created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)


class UUIDMixin:
    """Mixin class to add uuid column."""

    id_: Mapped[UUID] = mapped_column(
        "id", primary_key=True, nullable=False, unique=True, index=True
    )


class TypeIDMixin:
    """Mixin class to add type_id column."""

    id_: Mapped[TypeID] = mapped_column(
        "id", primary_key=True, nullable=False, unique=True, index=True
    )


class VarCharMixin:
    """Mixin class to add varchar column."""

    id_: Mapped[str] = mapped_column(
        "id", primary_key=True, nullable=False, unique=True, index=True
    )
