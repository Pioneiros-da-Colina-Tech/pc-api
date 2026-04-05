from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, VarCharMixin


class RoleEntity(Entity, VarCharMixin):
    """Lookup table for all possible roles in the system."""

    label: Mapped[str] = mapped_column(sa.String(100), nullable=False)


class ScreenEntity(Entity, VarCharMixin):
    """Lookup table for all screens/sections in the application."""

    label: Mapped[str] = mapped_column(sa.String(100), nullable=False)


class RoleScreenEntity(Entity):
    """
    Many-to-many join between roles and screens they can access.

    Intentionally inherits only from Entity (not UUIDMixin / VarCharMixin)
    so no extra `id_` column is introduced.  The composite PK is formed by
    (role_id, screen_id) below, matching the role_screen migration exactly.
    """

    role_id: Mapped[str] = mapped_column(
        sa.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    screen_id: Mapped[str] = mapped_column(
        sa.ForeignKey("screen.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )


class UserRoleEntity(Entity, TimestampMixin):
    """Many-to-many join between users and roles."""

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role_id: Mapped[str] = mapped_column(
        sa.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
