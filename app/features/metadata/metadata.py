from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .meta_artist import MetaArtist


class MetadataSource(Enum):
    JSON = "json"
    ID3 = "id3"
    MANUAL = "manual"
    YOUTUBE = "youtube"


@dataclass
class Metadata:
    source: MetadataSource
    title: str
    title_og: Optional[str]
    artists: list[MetaArtist]
    singers: list[MetaArtist]
    date: datetime
    disc: Optional[int]
    hash: Optional[str]  # audio hash
    seconds: float
