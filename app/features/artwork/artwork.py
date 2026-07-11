from core.paths import ARTWORK

class Artwork:
    def __init__(self, type: str, name: str):
        self.type = type
        self.name = name

    def get_path(self):
        return ARTWORK / f"{self.type}/{self.name}.png"