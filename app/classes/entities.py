from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin


class ClassesEntity(Entity, TimestampMixin, UUIDMixin):
    """A Desbravadores class (e.g. Amigo, Companheiro) with a target age."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "classes"

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    age: Mapped[int] = mapped_column(sa.Integer, nullable=False)


class ClassesRequirementEntity(Entity, TimestampMixin, UUIDMixin):
    """A single requirement belonging to a Classes, organised by section."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "classes_requirements"

    class_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("classes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    order_num: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
