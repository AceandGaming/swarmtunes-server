from sqlalchemy import event
from sqlalchemy.orm import Session
from st.features.artwork.song import get_song_artwork
from .song import Song

def refresh_song_metadata(song: Song) -> None:
    song.artworks = {
        artwork.type: artwork.name
        for artwork in get_song_artwork(song)
    }

@event.listens_for(Session, "before_flush")
def update_song_metadata(session, flush_context, instances):
    song_to_refresh = set()

    for obj in session.new | session.dirty:
        if isinstance(obj, Song):
            if obj not in session.deleted:
                song_to_refresh.add(obj)

    for song in song_to_refresh:
        refresh_song_metadata(song)