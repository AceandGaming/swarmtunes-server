from abstract.id_object import IDObject
from features.collection import SongCollection
from dataclasses import dataclass

@dataclass(eq=False, kw_only=True)
class Playlist(IDObject, SongCollection):
    protected: bool = False
