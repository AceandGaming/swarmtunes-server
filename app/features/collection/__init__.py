from typing import Protocol, TYPE_CHECKING, Optional
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from features.song import Song

class Collection(Protocol):
    title: Mapped[str]
    custom_artwork: Mapped[Optional[str]]
    songs: Mapped[list["Song"]]