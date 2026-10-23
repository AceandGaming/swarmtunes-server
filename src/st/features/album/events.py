from sqlalchemy import event
from sqlalchemy.orm import Session
from st.features.artwork.collection import get_album_artwork
from .album import Album

def refresh_album_metadata(album: Album) -> None:
    album.seconds = sum(song.seconds or 0 for song in album.songs)
    album.artworks = {
        artwork.type: artwork.name
        for artwork in get_album_artwork(album)
    }

@event.listens_for(Session, "before_flush")
def update_album_metadata(session, flush_context, instances):
    albums_to_refresh = set()

    for obj in session.new | session.dirty:
        if isinstance(obj, Album):
            if obj not in session.deleted:
                albums_to_refresh.add(obj)

    for album in albums_to_refresh:
        refresh_album_metadata(album)