import logging
from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

from sqlalchemy.orm import Session
from st.core import paths
from st.database.dependencies import get_db
from st.database.relationships import PlaylistSong
from st.features.artist import create_or_get
from st.features.artist.api import NetworkArtistV2
from st.features.playlist.playlist import Playlist
from st.features.session.token import Token
from st.features.song import (
    Song,
    SongType,
    create_song_service,
    to_network_v2,
)
from st.features.song.api import NetworkSongV2
from st.features.song.audio_refrence import AudioReferenceType
from pydantic import BaseModel

from .shared import APIException, CachedJSONResponse, admin_required, auth_required

log = logging.getLogger()


song_router = APIRouter()


@song_router.get("/")
def get_songs(
    ids: list[UUID] | None = Query(None, alias="id"),
    title: str | None = Query(None),
    type: SongType | None = Query(None),
    offset: int = 0,
    limit: int = 50,
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
        [to_network_v2(song) for song in songs],
        cache_for=timedelta(hours=1),
    )


class SongBatchRequest(BaseModel):
    ids: list[UUID]


@song_router.post("/batch")
def get_batched_songs(request: SongBatchRequest, db=Depends(get_db)):
    serivce = create_song_service(db)
    songs = serivce.get_many(request.ids)

    return [to_network_v2(song) for song in songs]  # No cache because it's POST


@song_router.get("/{id}")
def get_song(id: UUID, db=Depends(get_db)):
    service = create_song_service(db)

    song = service.get(id)
    if not song:
        raise APIException("SONG_NOT_FOUND", "Song not found", status_code=404)

    return CachedJSONResponse(to_network_v2(song), cache_for=timedelta(hours=1))

class UpdateSongRequestArtist(BaseModel):
    name: str
    originalName: str | None

class UpdateSongRequest(BaseModel):
    title: str
    titleOriginal: str | None

    artists: list[UpdateSongRequestArtist]
    singers: list[UpdateSongRequestArtist]
    type: Literal["original", "collab", "cover", "mashup"]

    dateReleased: str
    seconds: float

    customArtwork: str | None


@song_router.put("/{id}")
def update_song(id: UUID, req: UpdateSongRequest, db=Depends(get_db), token=Depends(admin_required)):
    service = create_song_service(db)
    song = service.get(id)
    if song is None:
        raise APIException("SONG_NOT_FOUND", "Song not found", status_code=404)

    try:
        date = datetime.fromisoformat(req.dateReleased)
    except ValueError:
        raise APIException("INVALID_DATE", "Invalid date", status_code=400)
    try:
        type = SongType(req.type)
    except ValueError:
        raise APIException("INVALID_AUDIO_TYPE", "Invalid audio type", status_code=400)


    song.title = req.title
    song.title_original = req.titleOriginal or None

    song.artists = [create_or_get(db, a.name, a.originalName or None) for a in req.artists]
    song.singers = [create_or_get(db, s.name, s.originalName or None) for s in req.singers]

    song.type = type

    song.date_released = date
    #song.seconds = req.seconds

    song.custom_artwork = req.customArtwork

    db.flush()


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


@song_router.get("/{id}/playlists")
def get_playlists_with_song(id: UUID, token: Token = Depends(auth_required), db: Session = Depends(get_db)):
    return [
        playlist_id
        for (playlist_id,) in (
            db.query(PlaylistSong.playlist_id)
            .join(PlaylistSong.song)
            .join(PlaylistSong.playlist)
            .filter(
                Playlist.user_id == token.user.id,
                Song.id == id,
            )
            .all()
        )
    ]