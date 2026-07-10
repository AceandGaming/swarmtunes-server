from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Uuid as SqlAlchemyUuid
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base
from database.types import UTCDateTime


class IDObject(Base):
    __abstract__ = True

    @property
    def enabled(self):
        return self.deleted_at is not None

    @property
    def str_id(self):
        return str(self.id)

    id: Mapped[UUID] = mapped_column(
        SqlAlchemyUuid, primary_key=True, default=uuid4
    )
    date_created: Mapped[datetime] = mapped_column(
        UTCDateTime, default=lambda: datetime.now(timezone.utc)
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def mark_deleted(self):
        self.deleted_at = datetime.now(timezone.utc)
