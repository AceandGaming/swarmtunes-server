from database.database import Base
from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from .relationships import song_artists, song_singers

class SQLArtist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    songs_artist = relationship(
        "SQLSong",
        secondary=song_artists,
        back_populates="artists"
    )

    songs_singer = relationship(
        "SQLSong",
        secondary=song_singers,
        back_populates="singers"
    )