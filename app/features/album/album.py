from features.collection import SongCollection
from dataclasses import dataclass

@dataclass(kw_only=True)
class Album(SongCollection):
    id: int

    def __hash__(self) -> int:
        return self.id
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.id == value.id