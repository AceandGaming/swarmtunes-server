from sqlalchemy import event
from sqlalchemy.orm import Session
from st.features.artwork.collection import get_playlist_artwork
from .playlist import Playlist

def refresh_playlist_metadata(playlist: Playlist) -> None:
    playlist.seconds = sum(item.song.seconds or 0 for item in playlist.songs)
    playlist.artworks = {
        artwork.type: artwork.name
        for artwork in get_playlist_artwork(playlist)
    }

@event.listens_for(Session, "before_flush")
def update_playlist_metadata(session, flush_context, instances):
    playlists_to_refresh = set()

    for obj in session.new | session.dirty:
        if isinstance(obj, Playlist):
            if obj not in session.deleted:
                playlists_to_refresh.add(obj)

    for playlist in playlists_to_refresh:
        refresh_playlist_metadata(playlist)