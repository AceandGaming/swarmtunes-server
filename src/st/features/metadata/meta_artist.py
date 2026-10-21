from dataclasses import dataclass


@dataclass
class MetaArtist:
    name: str
    name_og: str | None = None
