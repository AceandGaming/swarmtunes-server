from dataclasses import dataclass, field
from datetime import datetime, timezone
from abc import ABC
from typing import Optional
from core.database import Base
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

@dataclass(kw_only=True)
class IDObject(ABC):
    @property
    def enabled(self):
        return self.disabled_at is not None

    id: str
    hidden: bool = False
    date_created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    disabled_at: Optional[datetime] = None

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

class SQLIDObject(Base):
    __abstract__ = True
    id: Mapped[str] = mapped_column(String, primary_key=True)
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    date_created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)