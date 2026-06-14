from fastapi import APIRouter, Depends
from database.dependencies import get_db

v1_router = APIRouter()


@v1_router.get("/")
async def root(db=Depends(get_db)):
    return {
        "message": "Welcome to the SwarmTunes API! Note: This api is deprecated and will be removed in the future.", 
        "status": "ok",
        # "songs": len(DataSystem.songs.items),
        # "albums": len(DataSystem.albums.items),
        # "playlists": len(DataSystem.playlists.items),
        # "users": len(DataSystem.users.items),
        # "emotes": len(emotes.emotes),
        "current-path": "/"
    }