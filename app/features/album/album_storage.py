from .album import Album

class AlbumStorage:
    @property
    def albums(self):
        return self._albums.copy()

    _albums = []

    def Add(self, *albums: Album):
        for album in albums:
            self._albums.append(album)

    def Remove(self, *albums: Album):
        for album in albums:
            self._albums.remove(album)