from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from database.dependencies import get_db
from features.share import ShareManager
from features.song import Song, SongType, create_song_service, to_network_v1

song_router = APIRouter()


@song_router.get("/")
def get_songs(
    ids: list[UUID] = Query(None),
    filters: str = Query(None),
    maxResults: int = Query(100),
    db=Depends(get_db),
):
    service = create_song_service(db)

    songs = []
    if ids:
        songs = service.get_many(ids, preserve_order=True)
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


@song_router.get("/{id}/share")
def share_song(id: UUID, db=Depends(get_db)):
    service = create_song_service(db)
    song = service.get(id)
    if song is None:
        raise HTTPException(404, detail="Song not found")

    manager = ShareManager(db)

    link = manager.share(song)
    return {"link": link.link}
