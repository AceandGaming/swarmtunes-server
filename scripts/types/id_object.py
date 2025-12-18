from dataclasses import dataclass

@dataclass
class IDObject:
    id: str

    def __hash__(self):
        return hash(self.id)
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id