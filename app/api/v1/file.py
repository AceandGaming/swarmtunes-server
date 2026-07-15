import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, RedirectResponse

import core.paths as paths
from database.dependencies import get_db
from features.song import AudioReferenceType, create_song_service

log = logging.getLogger()

file_router = APIRouter()


@file_router.get("/album/{id}")
def get_album_file(id: UUID, export: bool = Query(False), db=Depends(get_db)):
    raise HTTPException(501, detail="Not implemented")


@file_router.get("/playlist/{id}")
def get_playlist_file(
    id: UUID, export: bool = Query(False), db=Depends(get_db)
):
    raise HTTPException(501, detail="Not implemented")


@file_router.get("/{id}")
def get_file(id: UUID, export: bool = Query(False), db=Depends(get_db)):
    service = create_song_service(db)

    song = service.get(id)
    if song is None:
        raise HTTPException(404, detail="Song not found")

    audios = [
        ref
        for ref in song.audio_references
        if ref.type == AudioReferenceType.GOOGLE_DRIVE
        or ref.type == AudioReferenceType.MANUAL
    ]
    if not audios:
        raise HTTPException(406, detail="Audio file not available")
    audio = audios[0]

    if export:
        return RedirectResponse(
            "https://drive.google.com/uc?export=download&id="
            + audio.external_id
        )

    path = paths.AUDIO / str(audio.id)
    if not path.exists():
        log.error(f"Failed to retreve audio file at {path} for song {song}")
        raise HTTPException(500, detail="Failed to retreve audio file")

    return FileResponse(
        path,
        media_type="audio/ogg",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=86400",
        },
    )
