from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from database.types import UTCDateTime

if TYPE_CHECKING:
    from features.user.user import User


class PlaybackState(Base):
    __tablename__ = "playback_states"

    @property
    def current_song(self):
        return UUID(self.queue[0]) if self.queue else None

    @property
    def playing(self):
        return self.paused_at is None

    @property
    def current_time(self):
        if self.paused_at:
            return (
                self.paused_at - self.updated_at
            ).total_seconds() + self.position
        else:
            now = datetime.now(timezone.utc)
            return (now - self.updated_at).total_seconds() + self.position

    user_id = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    user: Mapped["User"] = relationship("User", back_populates="playback_state")

    position: Mapped[float] = mapped_column(default=0.0)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime)
    paused_at: Mapped[datetime | None] = mapped_column(UTCDateTime)

    shuffle_active: Mapped[bool] = mapped_column(default=False)

    queue: Mapped[list[str]] = mapped_column(JSON, default=list)
    loaded_songs: Mapped[list[str]] = mapped_column(JSON, default=list)
