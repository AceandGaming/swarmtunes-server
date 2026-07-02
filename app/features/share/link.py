from datetime import datetime, timezone
from enum import Enum
from uuid import UUID

from nanoid import generate
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base
from database.types import UTCDateTime


class ShareLinkType(Enum):
    SONG = "song"
    PLAYLIST = "playlist"


class ShareLink(Base):
    __tablename__ = "share_links"

    link: Mapped[str] = mapped_column(primary_key=True, default=lambda: generate(size=10))
    type: Mapped[ShareLinkType] = mapped_column(SqlAlchemyEnum(ShareLinkType))
    external_id: Mapped[UUID]

    expires_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime, default=lambda: datetime.now(timezone.utc), nullable=True
    )
