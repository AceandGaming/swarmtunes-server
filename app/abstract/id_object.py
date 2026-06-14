from datetime import datetime, timezone
from typing import Optional
from database.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID

class IDObject(Base):
    __abstract__ = True
    @property
    def enabled(self):
        return self.disabled_at is not None
    @property
    def str_id(self):
        return str(self.id)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    hidden: Mapped[bool] = mapped_column(default=False)
    date_created: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    disabled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    def __hash__(self):
        return hash(self.id)
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def disable(self):
        self.disabled_at = datetime.now(timezone.utc)
    def enable(self):
        self.disabled_at = None