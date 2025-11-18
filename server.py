from typing import Literal
from pydantic import BaseModel
from scripts.types import *
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import scripts.embed as embeds
import scripts.api.emotes as emotes
import time, math
import scripts.paths as paths
from scripts.download import DownloadMissingSongs
import scripts.filters as Filter
from scripts.export import ExportSong, ExportAlbum
from scripts.cover import GetCover as ResizeCover
from scripts.cover import GetCoverPathFromSong
import asyncio
import re
import os
from scripts.search import SearchSongs
from scripts.share import ShareManager
from scripts.id_manager import IDManager
from scripts.session_manager import SessionManager
from scripts.data_system import DataSystem
from scripts.serializer import *

def InitializeServer():
    global app, auth
    startTime = time.time()

    allow_origins = [
        "https://swarmtunes.com",
    ]
    if os.getenv("DATA_PATH") is not None: #dev only
        allow_origins = ["*"]
    print("Starting server...")
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["token-expired"],
    )
    auth = OAuth2PasswordBearer(tokenUrl="login")

    print("FastAPI started")
    print("Loading data")
    IDManager.Load()
    ShareManager.Load()
    print(f"Server started in {math.floor((time.time() - startTime) * 1000)} miliseconds")
    return app, auth

def VailidateUser(token: str) -> User:
    user = SessionManager.GetUser(token)
    if not user:
        raise HTTPException(401, detail="Invalid token", headers={"token-expired": "true"})
    return user
def VailidateAdmin(token: str) -> User:
    user = VailidateUser(token)
    if not user.validAdmin:
        raise HTTPException(403, detail="Not admin")
    return user
def VailidatePlaylist(token: str, id: str) -> Playlist:
    user = VailidateUser(token)
    playlist = DataSystem.playlists.Get(id)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")
    if playlist.userId != user.id:
        raise HTTPException(403, detail="Playlist not owned by user")
    return playlist

async def ResyncServer():
    print("Downloading new files...")
    await DownloadMissingSongs()
    print("Downloading new files complete")
    DataSystem.albums.ReGenerate()
    print("New songs downloaded and albums generated")

app, auth = InitializeServer()

@app.on_event("startup")
async def Startup():
    await CleanUp()
    if os.getenv("DATA_PATH") is None:
        await ResyncServer()
async def CleanUp():
    pass
    # print("Cleaning up...")
    # SongManager.DeleteSongsWithoutReference()
    # #PlaylistManager.DeletePlaylistsWithoutReference()
    # #DataSystem.users.DeleteUsersWithoutReference()
    # paths.ClearPending()
    # paths.ClearProcessing()
    # print("Cleanup complete")

@app.on_event("shutdown")
async def Shutdown():
    print("Saving...")
    IDManager.Save()
    ShareManager.Save()
    print("Saved!")

@app.get("/")
@app.head("/")
async def root(song = Query(None), s = Query(None)):
    if song:
        song = DataSystem.songs.Get(song)
        if not song:
            return
        return HTMLResponse(embeds.SongEmbed(song))
    if s:
        song = ShareManager.GetSong(s)
        if not song:
            return
        return HTMLResponse(embeds.SongEmbed(song))
    return {
        "message": "Welcome to the SwarmTunes API", 
        "status": "ok",
        "songs": len(DataSystem.songs.items),
        "albums": len(DataSystem.albums.items),
        "playlists": len(DataSystem.playlists.items),
        "users": len(DataSystem.users.items),
        "emotes": len(emotes.emotes),
        "current-path": paths.DATA_DIR
    }

@app.get("/swarmfm")
def SwarmFM():
    return {"https://cast.sw.arm.fm/stream"}    

@app.get("/songs")
def GetSongs(ids: list[str] = Query(None), filters: str = Query(None), maxResults: int = Query(100)):
    if ids:
        songs = []
        for id in ids:
            song = DataSystem.songs.Get(id)
            if not song:
                raise HTTPException(404, detail="Song not found")
            songs.append(song)
        return SongSerializer.SerializeAllToNetwork(songs)
    elif filters:
        songs = DataSystem.songs.items
        serialized = SongSerializer.SerializeAllToNetwork(songs)
        try:
            return Filter.FilterDict(serialized, Filter.GetFilters(filters))
        except:
            raise HTTPException(400, detail="Invalid filters")
    else:
        songs = DataSystem.songs.items
        songs = songs[:maxResults]
        return SongSerializer.SerializeAllToNetwork(songs)

@app.get("/songs/{id}/share")
def GetSongShare(id: str):
    song = DataSystem.songs.Get(id)
    if not song:
        raise HTTPException(404, detail="Song not found")
    link = ShareManager.ShareSong(song)
    return {"link": link}
    
    
# class EditSongRequest(BaseModel):
#     title: str
#     type: Literal["neuro", "evil", "duet", "mashup"]
#     artist: str
#     date: str
#     #google_drive_id: str
#     original: bool

# @app.put("/songs/{id}")
# def EditSong(id: str, req: EditSongRequest, token: str = Depends(auth)):
#     VailidateAdmin(token)
#     song = DataSystem.songs.Get(id)
#     if not song:
#         raise HTTPException(404, detail="Song not found")
#     song.title = req.title
#     song.type = req.type
#     song.artist = req.artist
#     song.date = req.date
#     #song.google_drive_id = req.google_drive_id
#     song.original = req.original
#     return {"success": True}

@app.get("/files/album/{id}")
def GetAlbumFile(id: str):
    album = DataSystem.albums.Get(id)
    if not album:
        raise HTTPException(404, detail="Album not found")
    filename = ExportAlbum(album)
    file_path = paths.PROCESSING_DIR / id
    return FileResponse(file_path, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={filename}"})
    

@app.get("/files/{id}")
def GetSongFile(id: str, export: bool = Query(False)):
    if export:
        song = DataSystem.songs.Get(id)
        if song is None:
            raise HTTPException(404, detail="Song not found")
        filename = ExportSong(song) + ".mp3"
        file_path = paths.PROCESSING_DIR / id
        return FileResponse(file_path, media_type="audio/mpeg", headers={"Content-Disposition": f"attachment; filename={filename}"})
    if not DataSystem.songs.Get(id):
        raise HTTPException(404, detail="Song not found")
    file_path = paths.MP3_DIR / id
    return FileResponse(file_path, media_type="audio/mpeg", headers={"Accept-Ranges": "bytes"})

@app.get("/covers/{name}")
def GetCover(name: str, size: int = Query(128)):
    size = 2 ** round(math.log2(size))
    if size > 1024:
        size = 1024
    if size < 1:
        size = 1
    path = None
    match name:
        case "neuro":
            path = paths.ART_DIR / "neuro.png"
        case "evil":
            path = paths.ART_DIR / "evil.png"
        case "duet":
            path = paths.ART_DIR / "duet.png"
        case "swarmfm":
            path = paths.ART_DIR / "swarmfm.png"
        case _:
            song = DataSystem.songs.Get(name)
            if not song:
                raise HTTPException(404, detail="Song not found")
            path = GetCoverPathFromSong(song)
    file = ResizeCover(path, size)
    if not file:
        raise HTTPException(404, detail="Cover not found")

    return FileResponse(file, media_type="image/webp", headers={"Accept-Ranges": "bytes"})
    

@app.get("/albums")
def GetAlbums(ids: list[str] = Query(None), filters: str = Query(None)):
    if ids:
        albums = []
        for id in ids:
            album = DataSystem.albums.Get(id)
            if not album:
                raise HTTPException(404, detail="Album not found")
            albums.append(album)
        return AlbumSerializer.SerializeAllToNetwork(albums)
    elif filters:
        albums = DataSystem.albums.items
        serialized = AlbumSerializer.SerializeAllToNetwork(albums)
        try:
            return Filter.FilterDict(serialized, Filter.GetFilters(filters))
        except:
            raise HTTPException(400, detail="Invalid filters")
    else:
        albums = DataSystem.albums.items
        return AlbumSerializer.SerializeAllToNetwork(albums)

@app.get("/emotes")
def GetEmotes(names: list[str] = Query(None), scale: int = Query(1)):
    if names:
        emotesList = {}
        for name in names:
            emote = emotes.GetEmote(name)
            if not emote:
                raise HTTPException(404, detail="Emote not found")
            emotesList[name] = emote + "/" + str(scale) + "x.webp"
        return emotesList
    else:
        emotesList = {}
        for name, emote in emotes.emotes.items():
            emotesList[name] = emote + "/" + str(scale) + "x.webp"
        return emotesList

class LoginRequest(BaseModel):
    username: str
    password: str
    create: bool = False

@app.post("/users/login")
def Login(req: LoginRequest):
    username = req.username
    password = req.password
    create = req.create

    if len(username) > 32 or len(username) <= 0:
        raise HTTPException(400, detail="Invalid username")
    username = username.strip().lower()
    if not re.match(r"^[a-z0-9_-]+$", username):
        raise HTTPException(400, detail="Username contains invalid characters")
    
    if len(password) > 32 or len(password) <= 0:
        raise HTTPException(400, detail="Invalid password")

    if create:
        if len(password) < 5:
            raise HTTPException(400, detail="Password too short")
        if DataSystem.users.UsernameExists(username):
            raise HTTPException(400, detail="Username already taken")
        if username in ["admin", "vedal", "vedal987", "neuro-sama", "evil neuro", "neuro", "evil"]:
            raise HTTPException(400, detail="Username is reserved")
        
        DataSystem.users.CreateWithPassword(username, password)
    token = SessionManager.Login(username, password)
    if not token:
        raise HTTPException(401, detail="Invalid username or password")
    return {"token": token.token, "isAdmin": token.user.validAdmin}

@app.post("/me/logout")
def Logout(token: str = Depends(auth)):
    if not SessionManager.TokenIsValid(token):
        raise HTTPException(401, detail="Invalid token")
    SessionManager.Logout(token)
    return

@app.get("/me")
def GetUser(token: str = Depends(auth)):
    user = VailidateUser(token)
    return UserSerializer.SerializeToNetwork(user)

@app.delete("/me")
def DeleteUser(token: str = Depends(auth)):
    user = VailidateUser(token)
    DataSystem.users.Remove(user)
    return

@app.get("/playlists")
def GetPlaylists(ids: list[str] = Query(None), filters: str = Query(None), token: str = Depends(auth)):
    user = VailidateUser(token)
    if ids:
        playlists = []
        for id in ids:
            playlist = VailidatePlaylist(token, id)
            playlists.append(playlist)
        return PlaylistSerializer.SerializeAllToNetwork(playlists)
    elif filters:
        userPlaylist = user.playlists
        serialized = PlaylistSerializer.SerializeAllToNetwork(userPlaylist)
        try:
            return Filter.FilterDict(serialized, Filter.GetFilters(filters))
        except:
            raise HTTPException(400, detail="Invalid filters")
    else:
        playlists = user.playlists
        return PlaylistSerializer.SerializeAllToNetwork(playlists)

class NewPlaylistRequest(BaseModel):
    name: str
    songs: list[str] = []

@app.post("/playlists")
def NewPlaylist(req: NewPlaylistRequest, token: str = Depends(auth)):
    user = VailidateUser(token)
    name = req.name.strip()
    if len(name) > 32 or len(name) <= 0:
        raise HTTPException(400, detail="Invalid playlist name")
    if not re.match(r"^[0-9A-Za-z_ ]+$", name):
        raise HTTPException(400, detail="Playlist name contains invalid characters")

    playlist = DataSystem.playlists.Create(name=name, userId=user.id)
    user.AddPlaylist(playlist)
    for id in req.songs:
        song = DataSystem.songs.Get(id)
        if not song:
            raise HTTPException(404, detail="Song not found")
        playlist.AddSong(song)
    DataSystem.playlists.Save(playlist)
    DataSystem.users.Save(user)
    return PlaylistSerializer.SerializeToNetwork(playlist)

@app.delete("/playlists/{id}")
def DeletePlaylist(id: str,  token: str = Depends(auth)):
    user = VailidateUser(token)
    playlist = VailidatePlaylist(token, id)
    user.RemovePlaylist(playlist)
    DataSystem.playlists.Remove(playlist)
    DataSystem.users.Save(user)
    return

class PlaylistSongUpdateRequest(BaseModel):
    songs: list[str]

@app.patch("/playlists/{id}/add")
def AddSongToPlaylist(id: str, req: PlaylistSongUpdateRequest, token: str = Depends(auth)):
    playlist = VailidatePlaylist(token, id)
    for song in req.songs:
        song = DataSystem.songs.Get(song)
        if not song:
            raise HTTPException(404, detail="Song not found")
        if song in playlist.songs:
            raise HTTPException(400, detail="Song already in playlist")
        playlist.AddSong(song)

    DataSystem.playlists.Save(playlist)
    return {"success": True}

@app.patch("/playlists/{id}/remove")
def RemoveSongFromPlaylist(id: str, req: PlaylistSongUpdateRequest, token: str = Depends(auth)):
    playlist = VailidatePlaylist(token, id)
    for song in req.songs:
        song = DataSystem.songs.Get(song)
        if not song:
            raise HTTPException(404, detail="Song not found")
        if song not in playlist.songs:
            raise HTTPException(400, detail="Song not in playlist")
        playlist.RemoveSong(song)

    DataSystem.playlists.Save(playlist)
    return {"success": True}

class RenamePlaylistRequest(BaseModel):
    name: str

@app.patch("/playlists/{id}")
def RenamePlaylist(id: str, req: RenamePlaylistRequest, token: str = Depends(auth)):
    playlist = VailidatePlaylist(token, id)
    name = req.name.strip()
    if len(name) > 32 or len(name) <= 0:
        raise HTTPException(400, detail="Invalid playlist name")
    if not re.match(r"^[0-9A-Za-z_ ]+$", name):
        raise HTTPException(400, detail="Playlist name contains invalid characters")
    playlist.name = name
    DataSystem.playlists.Save(playlist)
    return {"success": True}
    
@app.get("/search")
def Search(query: str = Query(""), maxResults: int = Query(20)):
    results = SearchSongs(query)
    return SongSerializer.SerializeAllToNetwork(results[:maxResults])

@app.post("/resync")
async def Resync(token: str = Depends(auth)):
    VailidateAdmin(token)
    task = asyncio.create_task(ResyncServer())
    task.add_done_callback(lambda task: task.exception())
    return