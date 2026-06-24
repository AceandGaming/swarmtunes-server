from fastapi import APIRouter, Depends, Query
from database.dependencies import get_db
from .song import song_router
from .album import album_router
from .file import file_router
from .auth import auth_router
from .playlist import playlist_router
from general.search import search_songs
from features.song import create_song_service, to_network_v1

v1_router = APIRouter()
v1_router.include_router(song_router, prefix="/songs")
v1_router.include_router(album_router, prefix="/albums")
v1_router.include_router(file_router, prefix="/files")
v1_router.include_router(auth_router)
v1_router.include_router(playlist_router, prefix="/playlists")

@v1_router.get("/")
@v1_router.head("/")
async def root():
    return {
        "message": "Welcome to the SwarmTunes API!", 
        "status": "ok",
        "current-path": "/api/v1"
    }

@v1_router.get("/search")
async def search(query = Query(""), db = Depends(get_db)):
    service = create_song_service(db)
    songs = service.get_all()
    return [to_network_v1(song) for song in search_songs(songs, query)]

@v1_router.get("/covers/{name:path}")
async def get_cover(name: str):
    pass

@v1_router.get("/emotes/{name}")
async def get_emote(name: str):
    pass