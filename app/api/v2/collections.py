from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from database.dependencies import get_db
from features.album import create_album_service, to_network_v2
from features.song import to_network_v2 as to_network_v2_song

from .shared import APIException, CachedJSONResponse

collections_router = APIRouter()


@collections_router.get("/")
def get_albums(ids: list[UUID] = Query(..., alias="id"), db=Depends(get_db)):
    service = create_album_service(db)

    albums = service.get_many(ids)

    return CachedJSONResponse(
        [to_network_v2(album) for album in albums],
        cache_for=timedelta(hours=1),
    )


@collections_router.get("/{id}")
def get_album(id: UUID, db=Depends(get_db)):
    service = create_album_service(db)

    album = service.get(id)
    if not album:
        raise APIException(
            "ALBUM_NOT_FOUND", "Album not found", status_code=404
        )

    return CachedJSONResponse(
        to_network_v2(album),
        cache_for=timedelta(hours=1),
    )


@collections_router.get("/{id}/songs")
def get_songs(id: UUID, lite: bool = False, db=Depends(get_db)):
    service = create_album_service(db)

    album = service.get(id)
    if not album:
        raise APIException(
            "ALBUM_NOT_FOUND", "Album not found", status_code=404
        )

    return [to_network_v2_song(song, lite) for song in album.songs]
