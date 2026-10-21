from fastapi import APIRouter

from .auth import auth_router
from .collections import collections_router
from .misc import misc_router
from .pages import page_router
from .playlist import playlist_router
from .song import song_router

v2_router = APIRouter()

v2_router.include_router(song_router, prefix="/songs")
v2_router.include_router(collections_router, prefix="/collections")
v2_router.include_router(playlist_router, prefix="/playlists")
v2_router.include_router(auth_router)
v2_router.include_router(misc_router)
v2_router.include_router(page_router)
