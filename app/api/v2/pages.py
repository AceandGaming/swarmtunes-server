from datetime import timedelta

from fastapi import APIRouter, Depends

from database.dependencies import get_db
from features.album import Album, AlbumType, create_album_service
from features.album import to_network_v2 as to_network_v2_album
from features.song import Song, SongType, create_song_service
from features.song import to_network_v2 as to_network_v2_song

from .shared import CachedJSONResponse

page_router = APIRouter()


@page_router.get("/discover")
async def discover(db=Depends(get_db)):
    album_service = create_album_service(db)
    song_service = create_song_service(db)

    setlists = (
        album_service.query().filter(Album.type == AlbumType.DATE_SETLIST).all()
    )
    discs = (
        album_service.query()
        .filter(Album.type == AlbumType.DISC_COLLECTION)
        .all()
    )
    originals = (
        song_service.query().filter(Song.type == SongType.ORIGINAL).all()
    )
    mashups = song_service.query().filter(Song.type == SongType.MASHUP).all()

    return CachedJSONResponse(
        {
            "setlists": [to_network_v2_album(album) for album in setlists],
            "discs": [to_network_v2_album(album) for album in discs],
            "originals": [to_network_v2_song(song) for song in originals],
            "mashups": [to_network_v2_song(song) for song in mashups],
        },
        cache_for=timedelta(days=1),
    )
