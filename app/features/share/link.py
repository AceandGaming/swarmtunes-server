from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID

from nanoid import generate
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base
from database.types import StringValueEnum, UTCDateTime


class ShareLinkType(StrEnum):
    SONG = "song"
    PLAYLIST = "playlist"


class ShareLink(Base):
    __tablename__ = "share_links"

    link: Mapped[str] = mapped_column(
        primary_key=True, default=lambda: generate(size=10)
    )
    type: Mapped[ShareLinkType] = mapped_column(StringValueEnum(ShareLinkType))
    external_id: Mapped[UUID]

    expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
