from datetime import date

import sqlalchemy as sa
from pydantic_br import CPFDigits
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.entities import Entity, TimestampMixin, UUIDMixin


class UsersEntity(Entity, TimestampMixin, UUIDMixin):
    document: Mapped[CPFDigits] = mapped_column(
        sa.String(11), nullable=False, unique=True, index=True
    )
    birth_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
