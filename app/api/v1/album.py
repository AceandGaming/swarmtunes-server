from uuid import UUID

from database.dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from features.album import create_album_service, to_network_v1

album_router = APIRouter()


@album_router.get("/")
def get_albums(ids: list[UUID] = Query(None), db=Depends(get_db)):
    service = create_album_service(db)

    if ids:
        albums = service.get_many(ids)
        if len(albums) != len(ids):
            raise HTTPException(404, detail="Album not found")
    else:
        albums = service.get_all()

    return [to_network_v1(album) for album in albums]
