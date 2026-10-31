from datetime import timedelta
from threading import RLock
from time import perf_counter
from typing import Literal

from cachetools import TTLCache
from fastapi import APIRouter, Depends, Query, UploadFile
from fastapi.responses import FileResponse

import st.core.paths as paths
from st.database.dependencies import get_db
from st.features.song import (
    create_song_service,
    to_network_v2,
)
from st.general.export import export_artwork
from st.general.search import SearchObject, song_search_objects
from st.general.search import search as search_objects

from .shared import APIException, admin_required

misc_router = APIRouter()

search_cache = TTLCache(maxsize=100, ttl=timedelta(minutes=15).total_seconds())
search_cache_lock = RLock()


def get_search_objects(service) -> list[SearchObject]:
    with search_cache_lock:
        try:
            return search_cache["songs"]  # pyright: ignore[reportReturnType]
        except KeyError:
            songs = service.get_all()
            objects = song_search_objects(songs)

            search_cache["songs"] = objects
            return objects


@misc_router.get("/search")
async def search(
    q: str | None = Query(None, max_length=30),
    limit: int = Query(10),
    db=Depends(get_db),
):
    if not q:
        return []

    service = create_song_service(db)

    search_results = search_objects(get_search_objects(service), q)[:limit]

    song_results = service.get_many([r.id for r in search_results])
    return [to_network_v2(song) for song in song_results]


@misc_router.get("/covers/{name:path}")
async def get_cover(
    name: str, size: Literal["small", "medium", "large"] = Query("medium")
):
    size_scale = {
        "small": 64,
        "medium": 256,
        "large": 1024,
    }.get(size, 256)

    path = paths.ARTWORK / f"{name}.png"
    if not path.is_relative_to(paths.ARTWORK):
        raise APIException(
            "COVER_NOT_FOUND", "Cover not found", status_code=404
        )

    exported = export_artwork(path, size_scale)
    if exported is None:
        raise APIException(
            "COVER_NOT_FOUND", "Cover not found", status_code=404
        )
    return FileResponse(
        exported,
        media_type="image/webp",
        headers={
            "Cache-Control": f"public, max-age={timedelta(days=7).total_seconds()}, immutable"
        },
    )


@misc_router.post("/covers/{name:path}")
async def add_cover(name: str, file: UploadFile, token=Depends(admin_required)):
    if file.content_type != "image/png":
        raise APIException(
            "INVALID_COVER", "Cover must be a PNG", status_code=400
        )
    if "." in name or ".." in name:
        raise APIException(
            "INVALID_COVER", "Cover name must not contain dots", status_code=400
        )

    path = paths.ARTWORK / f"{name}.png"

    if path.exists():
        raise APIException(
            "COVER_EXISTS", "Cover already exists", status_code=400
        )

    data = await file.read()

    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise APIException(
            "INVALID_COVER",
            "Invalid PNG file",
            status_code=400,
        )

    path.write_bytes(data)
