from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin


class MeetingScoreEntity(Entity, TimestampMixin, UUIDMixin):
    """Per-user score record for a single meeting."""

    meeting_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    presenca: Mapped[int] = mapped_column(sa.SmallInteger, nullable=False)
    pontualidade: Mapped[int] = mapped_column(sa.SmallInteger, nullable=False)
    uniforme: Mapped[int] = mapped_column(sa.SmallInteger, nullable=False)
    modestia: Mapped[int] = mapped_column(sa.SmallInteger, nullable=False)

    __table_args__ = (
        sa.UniqueConstraint("meeting_id", "user_id", name="uq_meeting_score"),
    )


class BonusScoreEntity(Entity, TimestampMixin, UUIDMixin):
    """Manual bonus points assigned to a user or an entire unit."""

    user_id: Mapped[UUID | None] = mapped_column(
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    unit_id: Mapped[UUID | None] = mapped_column(
        sa.ForeignKey("unit.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    points: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    year: Mapped[str] = mapped_column(sa.String(4), nullable=False)
    semester: Mapped[int] = mapped_column(sa.SmallInteger, nullable=False)
