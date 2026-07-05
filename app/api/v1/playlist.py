import unicodedata
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from core.config import get_config
from database.dependencies import get_db
from features.playlist import Playlist, create_playlist_service, to_network_v1
from features.session import Token
from features.share import ShareManager
from features.song import create_song_service

from .shared import auth_required

playlist_router = APIRouter()


def validate_playlist_name(name: str):
    config = get_config()

    name = unicodedata.normalize("NFKC", name)
    name = "".join(c for c in name if not unicodedata.category(c).startswith("C"))
    name = name.strip()

    if len(name) > config.playlist_max_name_length or len(name) <= 0:
        raise HTTPException(400, detail="Invalid playlist name")
    return name


@playlist_router.get("/")
def get_playlists(
    ids: list[UUID] = Query(None),
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)

    if ids:
        playlists = service.get_many_in_user(token.user, ids)
        if len(playlists) != len(ids):
            raise HTTPException(404, detail="Playlist not found")
    else:
        playlists = token.user.playlists

    return [to_network_v1(playlist) for playlist in playlists]


class NewPlaylistRequest(BaseModel):
    name: str
    songs: list[UUID] = []


@playlist_router.post("/")
def new_playlist(
    req: NewPlaylistRequest, token: Token = Depends(auth_required), db=Depends(get_db)
):
    song_service = create_song_service(db)
    config = get_config()

    if len(token.user.playlists) > config.user_max_playlists:
        raise HTTPException(400, detail="User has reached playlist limit")

    name = validate_playlist_name(req.name)
    songs = song_service.get_many(req.songs)

    playlist = Playlist(
        title=name,
    )
    playlist.user = token.user
    playlist.songs = songs

    db.add(playlist)
    db.flush()
    db.refresh(playlist)
    return to_network_v1(playlist)


@playlist_router.delete("/{id}")
def delete_playlist(id: UUID, token: Token = Depends(auth_required), db=Depends(get_db)):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")
    if playlist.protected:
        raise HTTPException(403, detail="Playlist is protected")

    service.delete(playlist)


class PlaylistSongUpdateRequest(BaseModel):
    songs: list[UUID]


@playlist_router.patch("/{id}/add")
def add_songs(
    id: UUID,
    req: PlaylistSongUpdateRequest,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")

    songs_service = create_song_service(db)
    songs = songs_service.get_many(req.songs)
    if len(songs) != len(req.songs):
        raise HTTPException(404, detail="Song not found")

    for song in songs:
        playlist.add_song(song)

    return {"success": True}


@playlist_router.patch("/{id}/remove")
def remove_songs(
    id: UUID,
    req: PlaylistSongUpdateRequest,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")

    songs_service = create_song_service(db)
    songs = songs_service.get_many(req.songs)
    if len(songs) != len(req.songs):
        raise HTTPException(404, detail="Song not found")

    for song in songs:
        playlist.remove_song(song)

    return {"success": True}


class PatchPlaylistRequest(BaseModel):
    name: Optional[str]


@playlist_router.patch("/{id}")
def patch_playlist(
    id: UUID,
    req: PatchPlaylistRequest,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")

    if req.name:
        validate_playlist_name(req.name)
        playlist.title = req.name


@playlist_router.get("/{id}/share")
def share_playlist(id: UUID, token: Token = Depends(auth_required), db=Depends(get_db)):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")

    manager = ShareManager(db)

    link = manager.share(playlist)
    return {"link": link.link}


@playlist_router.post("/shared")
def add_shared_playlist(id: UUID, token: Token = Depends(auth_required), db=Depends(get_db)):
    pass
