from fastapi import APIRouter, Depends, HTTPException, Cookie
from database.dependencies import get_db
from features.playlist import create_playlist_service, Playlist
from uuid import UUID

playlist_router = APIRouter()

@playlist_router.get("/playlists/{id}")
def get_playlist(id: UUID, sessionToken: str = Cookie(), db = Depends(get_db)):
    pass