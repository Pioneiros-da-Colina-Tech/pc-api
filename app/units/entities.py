from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin


class UnitEntity(Entity, TimestampMixin, UUIDMixin):
    """A Desbravadores unit, bound to a class and with a defined member age."""

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    age: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    class_id: Mapped[UUID | None] = mapped_column(
        sa.ForeignKey("classes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )


class UnitMemberEntity(Entity, TimestampMixin):
    """
    Membership of a user in a unit for a specific club year.
    Composite PK: (unit_id, user_id, club_year_id).
    """

    unit_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("unit.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    club_year_id: Mapped[str] = mapped_column(
        sa.ForeignKey("club_year.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(sa.String(50), nullable=False)
