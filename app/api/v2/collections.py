from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from database.dependencies import get_db
from features.album import Album, AlbumType, create_album_service, to_network_v2

from .shared import APIException, CachedJSONResponse

collections_router = APIRouter()


@collections_router.get("/")
def get_albums(
    ids: list[UUID] | None = Query(None, alias="id"),
    type: AlbumType | None = Query(None),
    offset: int = 0,
    limit: int = 50,
    db=Depends(get_db),
):
    if limit > 100:
        limit = 100

    service = create_album_service(db)

    query = service.query()
    if ids:
        query = query.filter(Album.id.in_(ids))

    if type:
        query = query.filter(Album.type == type)

    query = query.offset(offset).limit(limit)

    albums = query.all()

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


class AlbumBatchRequest(BaseModel):
    ids: list[UUID]


@collections_router.post("/batch")
def get_batched_albums(request: AlbumBatchRequest, db=Depends(get_db)):
    serivce = create_album_service(db)
    albums = serivce.get_many(request.ids)

    return [to_network_v2(album) for album in albums]


@collections_router.get("/{id}/songs")
def get_songs(id: UUID, db=Depends(get_db)):
    service = create_album_service(db)

    album = service.get(id)
    if not album:
        raise APIException(
            "ALBUM_NOT_FOUND", "Album not found", status_code=404
        )

    return CachedJSONResponse(
        [str(song.id) for song in album.songs],
        cache_for=timedelta(days=1),
    )
