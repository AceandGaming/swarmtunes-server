import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

import core.paths as paths
from database.dependencies import get_db
from features.song import create_song_service

log = logging.getLogger()

file_router = APIRouter(prefix="/files")


@file_router.get("/album/{id}")
def get_album_file(id: UUID, export: bool = Query(False), db=Depends(get_db)):
    pass


@file_router.get("/playlist/{id}")
def get_playlist_file(id: UUID, export: bool = Query(False), db=Depends(get_db)):
    pass


@file_router.get("/{id}")
def get_file(id: UUID, export: bool = Query(False), db=Depends(get_db)):
    service = create_song_service(db)

    song = service.get(id)
    if song is None:
        raise HTTPException(404, detail="Song not found")
    audios = song.get_audio("gdrive")
    if audios is None:
        raise HTTPException(404, detail="Song not found")

    if export:
        pass  # TODO

    path = paths.AUDIO / str(song.id)
    if not path.exists():
        log.error(f"Failed to retreve audio file at {path} for song {song}")
        raise HTTPException(500, detail="Failed to retreve audio file")

    # New server uses ogg. Old clients may not expect ogg
    return FileResponse(
        path, media_type="audio/ogg", headers={"Accept-Ranges": "bytes"}
    )
