from fastapi import APIRouter, Depends, Query, HTTPException
from database.dependencies import get_db
from features.song import create_song_service, Song, SongType, to_network_v1
from uuid import UUID

song_router = APIRouter()

@song_router.get("/songs")
def get_songs(ids: list[UUID] = Query(None), filters: str = Query(None), maxResults: int = Query(100), db = Depends(get_db)):
    service = create_song_service(db)

    songs = []
    if ids:
        songs = service.get_many(ids)
        if len(songs) != len(ids):
            raise HTTPException(404, detail="Song not found")
    elif filters:
        # This is a hack because the filters are not implemented (and probably won't be)
        if filters.startswith("title"):
            songs = service.query().filter(Song.type == SongType.MASHUP).all()
        elif filters.startswith("original"):
            songs = service.query().filter(Song.type == SongType.ORIGINAL).all()
    else:
        songs = service.get_all()[:maxResults]

    return [to_network_v1(song) for song in songs]

@song_router.get("/songs/{id}/share")
def share_song():
    # TODO
    pass