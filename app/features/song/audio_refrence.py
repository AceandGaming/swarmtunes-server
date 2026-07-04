from datetime import datetime, timezone
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy import Uuid as SqlAlchemyUuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from database.types import StringValueEnum, UTCDateTime

if TYPE_CHECKING:
    from .song import Song


class AudioReferenceType(StrEnum):
    GOOGLE_DRIVE = "gdrive"
    YOUTUBE = "youtube"


class SongAudioReference(Base):
    __tablename__ = "song_audio_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_created: Mapped[UTCDateTime] = mapped_column(
        UTCDateTime, default=datetime.now(timezone.utc)
    )
    song_id: Mapped[UUID] = mapped_column(
        SqlAlchemyUuid, ForeignKey("songs.id", ondelete="CASCADE")
    )

    type: Mapped[AudioReferenceType] = mapped_column(StringValueEnum(AudioReferenceType))
    external_id: Mapped[str] = mapped_column(index=True)
    audio_hash: Mapped[str | None] = mapped_column(index=True)

    song: Mapped["Song"] = relationship(back_populates="audio_references")

    __table_args__ = (
        Index("ix_audio_type_external_id", "type", "external_id"),
        UniqueConstraint("type", "external_id", name="uq_audio_type_external_id"),
    )
