import unicodedata
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from core.config import get_config
from database.dependencies import get_db
from features.playlist import Playlist, create_playlist_service, to_network_v2
from features.session import Token
from features.song import create_song_service
from features.song import to_network_v2 as to_network_v2_song

from .shared import APIException, auth_required

playlist_router = APIRouter()


def validate_playlist_title(name: str):
    config = get_config()

    name = unicodedata.normalize("NFKC", name)
    name = "".join(
        c for c in name if not unicodedata.category(c).startswith("C")
    )
    name = name.strip()

    if len(name) > config.playlist_max_name_length or len(name) <= 0:
        APIException("INVALID_PLAYLIST_NAME", "Invalid playlist name")
    return name


@playlist_router.get("/")
def get_playlists(
    ids: list[UUID] = Query(None, alias="id"),
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)

    if ids:
        playlists = service.get_many_in_user(token.user, ids)
    else:
        playlists = service.get_of_user(token.user)

    return [to_network_v2(playlist) for playlist in playlists]


@playlist_router.get("/{id}")
def get_playlist(
    id: UUID, token: Token = Depends(auth_required), db=Depends(get_db)
):
    service = create_playlist_service(db)

    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise APIException("PLAYLIST_NOT_FOUND", "Playlist not found", 404)

    return to_network_v2(playlist)


class NewPlaylistRequest(BaseModel):
    title: str
    songIds: list[UUID] = []


@playlist_router.post("/")
def new_playlist(
    req: NewPlaylistRequest,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    song_service = create_song_service(db)
    config = get_config()

    if len(token.user.playlists) > config.user_max_playlists:
        raise APIException(
            "PLAYLIST_LIMIT_REACHED", "User has reached playlist limit"
        )

    title = validate_playlist_title(req.title)
    songs = song_service.get_many(req.songIds)

    playlist = Playlist(
        title=title,
        user=token.user,
    )
    for song in songs:
        playlist.add_song(song)

    db.add(playlist)
    db.flush()
    db.refresh(playlist)
    return to_network_v2(playlist)


@playlist_router.delete("/{id}")
def delete_playlist(
    id: UUID, token: Token = Depends(auth_required), db=Depends(get_db)
):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise APIException(
            "PLAYLIST_NOT_FOUND", "Playlist not found", status_code=404
        )
    if playlist.protected:
        raise APIException(
            "PLAYLIST_IS_PROTECTED", "Playlist is protected", status_code=403
        )

    service.delete(playlist)


@playlist_router.get("/{id}/songs")
def get_songs(
    id: UUID,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)

    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise APIException(
            "PLAYLIST_NOT_FOUND", "Playlist not found", status_code=404
        )

    return [
        {
            "songId": str(item.song.id),
            "dateAdded": str(item.date_added),
        }
        for item in playlist.songs
    ]


class PlaylistSongUpdateRequest(BaseModel):
    songIds: list[UUID]


@playlist_router.post("/{id}/songs")
def add_songs(
    id: UUID,
    req: PlaylistSongUpdateRequest,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise APIException(
            "PLAYLIST_NOT_FOUND", "Playlist not found", status_code=404
        )

    songs_service = create_song_service(db)
    songs = songs_service.get_many(req.songIds)

    for song in songs:
        playlist.add_song(song)


@playlist_router.post("/{id}/songs/remove")
def remove_songs(
    id: UUID,
    req: PlaylistSongUpdateRequest,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise APIException(
            "PLAYLIST_NOT_FOUND", "Playlist not found", status_code=404
        )

    songs_service = create_song_service(db)
    songs = songs_service.get_many(req.songIds)

    for song in songs:
        playlist.remove_song(song)


@playlist_router.delete("/{id}/songs/{song_id}")
def remove_song(
    id: UUID,
    song_id: UUID,
    token: Token = Depends(auth_required),
    db=Depends(get_db),
):
    service = create_playlist_service(db)
    playlist = service.get_in_user(token.user, id)
    if not playlist:
        raise APIException(
            "PLAYLIST_NOT_FOUND", "Playlist not found", status_code=404
        )

    songs_service = create_song_service(db)
    song = songs_service.get(song_id)
    if not song:
        raise APIException("SONG_NOT_FOUND", "Song not found", status_code=404)

    playlist.remove_song(song)


class PatchPlaylistRequest(BaseModel):
    title: Optional[str]


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
        raise APIException(
            "PLAYLIST_NOT_FOUND", "Playlist not found", status_code=404
        )

    if req.title:
        playlist.title = validate_playlist_title(req.title)

    return to_network_v2(playlist)
