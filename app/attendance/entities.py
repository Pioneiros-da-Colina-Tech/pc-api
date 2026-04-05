from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin


class AttendanceEntity(Entity, TimestampMixin, UUIDMixin):
    """Attendance record for a user in a meeting."""

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
    attendance_status: Mapped[str] = mapped_column(
        sa.String(20), nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "meeting_id", "user_id", name="uq_attendance_meeting_user"
        ),
    )
