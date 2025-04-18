from datetime import datetime

from sqlalchemy import (
    VARCHAR,
    LargeBinary,
    DateTime,
    text,
    ForeignKey,
    UUID,
    INTEGER,
)
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy.orm import Mapped, mapped_column

from utils.db import Base, intpk


class BaseClass(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text('CURRENT_TIMESTAMP')
    )


class Action(BaseClass):
    __tablename__ = 'action'

    id: Mapped[intpk]
    action_name: Mapped[str] = mapped_column(VARCHAR(255))

    def __str__(self):
        return f'{self.id}: {self.action_name}'


class Secret(BaseClass):
    __tablename__ = 'secret'

    secret_key: Mapped[str] = mapped_column(
        UUID,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()")
    )
    secret: Mapped[str] = mapped_column(LargeBinary(255))
    passphrase: Mapped[str | None] = mapped_column(VARCHAR(255), default=None)
    ttl_seconds: Mapped[int] = mapped_column(INTEGER)
    is_accessed: Mapped[bool] = mapped_column(default=False)

    def __str__(self):
        return f'{self.secret_key}: {self.ttl_seconds} {self.created_at}'


class Log(BaseClass):
    __tablename__ = 'log'

    id: Mapped[intpk]
    action_id: Mapped[str] = mapped_column(ForeignKey('action.id'))
    secret_key: Mapped[str] = mapped_column(UUID)
    from_ip: Mapped[str] = mapped_column(CIDR)

    def __str__(self):
        return f'{self.id}: {self.action_id} {self.secret_key} {self.from_ip}'
