import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from core import paths
from database.dependencies import get_db
from features.artist import create_or_get
from features.share import ShareManager
from features.song import (
    Song,
    SongType,
    create_song_service,
    to_network_v2,
)
from features.song.audio_refrence import AudioReferenceType

from .shared import APIException, CachedJSONResponse

log = logging.getLogger()


song_router = APIRouter()


@song_router.get("/")
def get_songs(
    ids: list[UUID] | None = Query(None, alias="id"),
    title: str | None = Query(None),
    type: SongType | None = Query(None),
    offset: int = 0,
    limit: int = 50,
    lite: bool = False,
    db=Depends(get_db),
):
    if limit > 100:
        limit = 100

    service = create_song_service(db)

    query = service.query()
    if ids:
        query = query.filter(Song.id.in_(ids))
    if title:
        query = query.filter(Song.title == title)
    if type:
        query = query.filter(Song.type == type)

    query = query.offset(offset).limit(limit)

    songs = query.all()

    return CachedJSONResponse(
        [to_network_v2(song, lite) for song in songs],
        cache_for=timedelta(hours=1),
    )


@song_router.get("/{id}")
def get_song(id: UUID, db=Depends(get_db)):
    service = create_song_service(db)

    song = service.get(id)
    if not song:
        raise APIException("SONG_NOT_FOUND", "Song not found", status_code=404)

    return CachedJSONResponse(to_network_v2(song), cache_for=timedelta(hours=1))


@song_router.get("/{id}/audio")
def get_song_audio(id: UUID, db=Depends(get_db)):
    service = create_song_service(db)

    song = service.get(id)
    if not song:
        raise APIException("SONG_NOT_FOUND", "Song not found", status_code=404)

    audios = [
        ref
        for ref in song.audio_references
        if ref.type == AudioReferenceType.GOOGLE_DRIVE
        or ref.type == AudioReferenceType.MANUAL
    ]

    if not song.playable or not audios:
        raise APIException(
            "SONG_NOT_PLAYABLE", "Audio file not available", status_code=406
        )
    audio = audios[0]

    path = paths.AUDIO / str(audio.id)
    if not path.exists():
        log.error(f"Failed to retreve audio file at {path} for song {song}")
        raise APIException(
            "SONG_AUDIO_NOT_FOUND",
            "Failed to retreve audio file",
            status_code=500,
        )

    return FileResponse(
        path,
        media_type="audio/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": f"public, max-age={timedelta(weeks=5).total_seconds()}, immutable",
        },
    )


@song_router.get("/{id}/gdrive")
def get_song_gdrive(id: UUID, db=Depends(get_db)):
    service = create_song_service(db)

    song = service.get(id)
    if not song:
        raise APIException("SONG_NOT_FOUND", "Song not found", status_code=404)

    audios = [
        ref
        for ref in song.audio_references
        if ref.type == AudioReferenceType.GOOGLE_DRIVE
    ]

    audio = audios[0]

    return RedirectResponse(
        "https://drive.google.com/uc?export=download&id=" + audio.external_id
    )
