import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.database.entity import Entity, TimestampMixin


class UsersEntity(Entity, TimestampMixin):
    username: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(sa.Text, nullable=False)
    disabled: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False
    )
    full_name: Mapped[str] = mapped_column(sa.Text, nullable=True)
    phone_number: Mapped[str] = mapped_column(sa.Text, nullable=True)
    sgc_code: Mapped[str] = mapped_column(sa.Text, nullable=True)
