from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin


class MeetingsEntity(Entity, TimestampMixin, UUIDMixin):
    name: Mapped[str] = mapped_column(sa.Text, nullable=False)
    date: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
