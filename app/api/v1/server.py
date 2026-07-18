from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

import core.paths as paths
from database.dependencies import get_db
from external.emotes import get_emote as emote_get_emote
from features.share import ShareLinkType, ShareManager
from features.song import create_song_service
from features.song import to_network_v1 as song_to_network
from general.embed import create_song_embed
from general.export import export_artwork
from general.search import search_songs

from .album import album_router
from .auth import auth_router
from .file import file_router
from .playlist import playlist_router
from .song import song_router

share = APIRouter()


v1_router = APIRouter()
v1_router.include_router(song_router, prefix="/songs")
v1_router.include_router(album_router, prefix="/albums")
v1_router.include_router(file_router, prefix="/files")
v1_router.include_router(auth_router)
v1_router.include_router(playlist_router, prefix="/playlists")


@v1_router.get("/")
@v1_router.head("/")
async def root(
    song: UUID | None = Query(None),
    s: str | None = Query(None),
    p: str | None = Query(None),
    db=Depends(get_db),
):
    if song:
        service = create_song_service(db)
        link_song = service.get(song)
        if link_song is None:
            raise HTTPException(404, detail="Song not found")
        return HTMLResponse(create_song_embed(link_song))

    code = s or p
    if code:
        manager = ShareManager(db)
        link = manager.get(code)

        if link is None:
            raise HTTPException(404, detail="Link not found")

        # if link.type == ShareLinkType.PLAYLIST:
        #     service = create_playlist_service(db)
        #     playlist = service.get(link.external_id)
        #     if playlist is None:
        #         raise HTTPException(404, detail="Playlist not found")
        #     return playlist_to_network(playlist)

        if link.type == ShareLinkType.SONG:
            service = create_song_service(db)
            link_song = service.get(link.external_id)
            if link_song is None:
                raise HTTPException(404, detail="Song not found")
            return HTMLResponse(create_song_embed(link_song))

        raise HTTPException(500, detail="Unsupported link type")

    return {
        "message": "Welcome to the SwarmTunes API!",
        "status": "ok",
        "current-path": "SQLite :)",
    }


@v1_router.get("/search")
async def search(
    query=Query(""), maxResults: int = Query(10), db=Depends(get_db)
):
    service = create_song_service(db)
    songs = service.get_all()
    return [
        song_to_network(song)
        for song in search_songs(songs, query)[:maxResults]
        if song.enabled
    ]


@v1_router.get("/covers/{name:path}")
async def get_cover(name: str):
    path = paths.ARTWORK / f"{name}.png"
    if not path.is_relative_to(paths.ARTWORK):
        raise HTTPException(status_code=404, detail="cover not found")

    exported = export_artwork(path)
    if exported is None:
        raise HTTPException(status_code=404, detail="cover not found")
    return FileResponse(
        exported,
        media_type="image/webp",
        headers={"Cache-Control": "public, max-age=604800"},
    )


@v1_router.get("/emotes/{name}")
async def get_emote(name: str, scale: int = Query(1)):
    emote = emote_get_emote(name)
    if not emote:
        raise HTTPException(404, detail="Emote not found")
    return RedirectResponse(emote + "/" + str(scale) + "x.webp")
