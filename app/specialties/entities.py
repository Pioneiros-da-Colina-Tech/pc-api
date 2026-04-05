from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin


class SpecialtiesEntity(Entity, TimestampMixin, UUIDMixin):
    """A Desbravadores specialty (especialidade) with code and name."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "specialties"

    code: Mapped[str] = mapped_column(
        sa.String(20), nullable=False, unique=True, index=True
    )
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False)


class UserSpecialtiesEntity(Entity, TimestampMixin, UUIDMixin):
    """Represents a specialty earned by a user."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "user_specialties"

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    specialty_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("specialties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "user_id",
            "specialty_id",
            name="uq_user_specialty",
        ),
    )
