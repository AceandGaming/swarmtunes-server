from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database.dependencies import get_db
from features.artist import create_or_get
from features.share import ShareManager
from features.song import Song, SongType, create_song_service, to_network_v1

from .shared import admin_required

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

    return JSONResponse(
        [to_network_v1(song) for song in songs],
        headers={"Cache-Control": "public, max-age=3600"},
    )


@song_router.get("/{id}/share")
def share_song(id: UUID, db=Depends(get_db)):
    service = create_song_service(db)
    song = service.get(id)
    if song is None:
        raise HTTPException(404, detail="Song not found")

    manager = ShareManager(db)

    link = manager.share(song)
    return {"link": link.link}


class SongPostRequest(BaseModel):
    title: str
    titleOriginal: Optional[str]
    artists: list[str]
    singers: list[str]
    type: str
    dateReleased: str
    disc: Optional[int]
    customArtwork: Optional[str]


@song_router.post("/")
def create_song(
    req: SongPostRequest,
    token=Depends(admin_required),
    db=Depends(get_db),
):
    artists = [create_or_get(db, a, a) for a in req.artists]
    singers = [create_or_get(db, a, a) for a in req.singers]

    type = getattr(SongType, req.type.upper())
    if type is None:
        raise HTTPException(400, detail="Invalid type")

    try:
        date = datetime.fromisoformat(req.dateReleased)
    except ValueError:
        raise HTTPException(400, detail="Invalid date")

    song = Song(
        title=req.title,
        title_original=req.titleOriginal or None,
        artists=artists,
        singers=singers,
        type=type,
        date_released=date,
        disc=req.disc,
        custom_artwork=req.customArtwork or None,
    )

    db.add(song)
    db.flush()
    db.refresh(song)
    return to_network_v1(song)


class SongPatchRequest(BaseModel):
    title: Optional[str] = None
    titleOriginal: Optional[str] = None
    artists: Optional[list[str]] = None
    singers: Optional[list[str]] = None
    type: Optional[str] = None
    dateReleased: Optional[str] = None
    disc: Optional[int] = None
    customArtwork: Optional[str] = None


@song_router.patch("/{id}")
def patch_song(
    req: SongPatchRequest,
    id: UUID,
    token=Depends(admin_required),
    db=Depends(get_db),
):
    service = create_song_service(db)
    song = service.get(id)

    if song is None:
        raise HTTPException(404, detail="Song not found")

    if req.title is not None:
        song.title = req.title
    if req.titleOriginal is not None:
        song.title_original = req.titleOriginal or None
    if req.artists is not None:
        song.artists = [create_or_get(db, a, a) for a in req.artists]
    if req.singers is not None:
        song.singers = [create_or_get(db, a, a) for a in req.singers]
    if req.type is not None:
        song.type = getattr(SongType, req.type.upper())
    if req.dateReleased is not None:
        try:
            date = datetime.fromisoformat(req.dateReleased)
        except ValueError:
            raise HTTPException(400, detail="Invalid date")
        song.date_released = date
    if req.disc is not None:
        song.disc = req.disc
    if req.customArtwork is not None:
        song.custom_artwork = req.customArtwork or None

    return to_network_v1(song)
