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


@page_router.get("/discover-ids")
async def discover_ids(db=Depends(get_db)):
    album_service = create_album_service(db)
    song_service = create_song_service(db)

    setlists: list[str] = [
        album_id
        for (album_id,) in (
            album_service.query()
            .filter(Album.type == AlbumType.DATE_SETLIST)
            .order_by(Album.date)
            .with_entities(Album.id)
            .all()
        )
    ]
    discs: list[str] = [
        album_id
        for (album_id,) in (
            album_service.query()
            .filter(Album.type == AlbumType.DISC_COLLECTION)
            .order_by(Album.disc)
            .with_entities(Album.id)
            .all()
        )
    ]
    originals: list[str] = [
        song_id
        for (song_id,) in (
            song_service.query()
            .filter(Song.type == SongType.ORIGINAL)
            .order_by(Song.date_released)
            .with_entities(Song.id)
            .all()
        )
    ]
    mashups: list[str] = [
        song_id
        for (song_id,) in (
            song_service.query()
            .filter(Song.type == SongType.MASHUP)
            .order_by(Song.date_released)
            .with_entities(Song.id)
            .all()
        )
    ]

    return CachedJSONResponse(
        {
            "setlists": setlists,
            "discs": discs,
            "originals": originals,
            "mashups": mashups,
        },
        cache_for=timedelta(minutes=10),
    )
