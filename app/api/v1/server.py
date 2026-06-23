from fastapi import APIRouter, Depends
from database.dependencies import get_db
from .song import song_router


v1_router = APIRouter()
v1_router.include_router(song_router, prefix="/songs")

@v1_router.get("/")
@v1_router.head("/")
async def root():
    return {
        "message": "Welcome to the SwarmTunes API!", 
        "status": "ok",
        "current-path": "/api/v1"
    }