from typing import Literal, Optional
from pydantic import BaseModel
from scripts.types import *
from fastapi import FastAPI, HTTPException, Query, Depends, Response, Cookie, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import scripts.embed as embeds
import scripts.api.emotes as emotes
import time, math
import scripts.paths as paths
from scripts.download import DownloadMissingSongs
import scripts.filters as Filter
from scripts.export import ExportSong, ExportAlbum, ExportPlaylist
from scripts.cover import GetCover as ResizeCover
from scripts.cover import GetCoverPathFromSong
import asyncio
import re
import os
from scripts.search import SearchSongs
from scripts.share import ShareManager
from scripts.id_manager import IDManager
from scripts.data_system import DataSystem
from scripts.serializer import *
import scripts.maintenance as maintenance
import scripts.config as config
from scripts.delete import DeleteManager
from urllib.parse import quote

def InitializeServer():
    global app
    startTime = time.time()

    allow_origins = [
        "https://swarmtunes.com",
    ]
    allow_origin_regex = ""
    if os.getenv("DATA_PATH") is not None: #dev only
        allow_origin_regex = r".*"
    print("Starting server...")
    print("Allowing origins:", allow_origins)
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["invaild-token"],
        allow_origin_regex=allow_origin_regex
    )

    print("FastAPI started")
    print("Loading data")
    IDManager.Load()
    ShareManager.Load()
    emotes.Load()
    print(f"Server started in {math.floor((time.time() - startTime) * 1000)} miliseconds")
    return app

def VailidateToken(tokenString: str|None) -> Token:
    if not tokenString:
        raise HTTPException(401, detail="Token Required", headers={"invaild-token": "true"})

    id, secret = tokenString.split(":")
    token = DataSystem.tokens.Get(id)

    if not token:
        raise HTTPException(401, detail="Invalid token", headers={"invaild-token": "true"})
    if not DataSystem.tokens.ValidateToken(token, secret):
        raise HTTPException(401, detail="Invalid token", headers={"invaild-token": "true"})

    return token
def VailidateUser(tokenString: str) -> User:
    token = VailidateToken(tokenString)

    user = DataSystem.users.Get(token.userId)
    if not user:
        raise HTTPException(401, detail="Invalid token", headers={"invaild-token": "true"})

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
def VerifyPlaylistName(name: str):
    name = name.strip()
    if len(name) > 32 or len(name) <= 0:
        raise HTTPException(400, detail="Invalid playlist name")
    if not re.match(r"^[0-9A-Za-z_ :]+$", name):
        raise HTTPException(400, detail="Playlist name contains invalid characters")
    return name

async def ResyncServer():
    print("Downloading new files...")
    await DownloadMissingSongs()
    print("Downloading new files complete")
    DataSystem.albums.ReGenerate()
    print("New songs downloaded and albums generated")

app = InitializeServer()

@app.on_event("startup")
async def Startup():
    if os.getenv("DATA_PATH") is None:
        await CleanUp()
        await ResyncServer()

async def CleanUp():
    print("Cleaning up...")
    maintenance.ClearAllOrphaned()
    maintenance.ClearProcessing()
    DeleteManager.DeleteExtraFiles()

@app.on_event("shutdown")
async def Shutdown():
    print("Saving...")
    ShareManager.Save()
    print("Saved!")

@app.get("/")
@app.head("/")
async def root(song = Query(None), s = Query(None), p = Query(None)):
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
    if p:
        playlist = ShareManager.GetPlaylist(p)
        if not playlist:
            return
        return HTMLResponse(embeds.PlaylistEmbed(playlist, p))
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

@app.get("/playlists/{id}/share")
def SharePlaylist(id: str, sessionToken: str = Cookie(None)):
    playlist = VailidatePlaylist(sessionToken, id)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")
    link = ShareManager.SharePlaylist(playlist)
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

@app.get("/files/playlist/{id}")
def GetPlaylistFile(id: str, sessionToken: str = Cookie(None)):
    playlist = VailidatePlaylist(sessionToken, id)
    filename =  ExportPlaylist(playlist)
    file_path = paths.PROCESSING_DIR / id
    return FileResponse(file_path, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={filename}"})
    

@app.get("/files/{id}")
def GetSongFile(id: str, export: bool = Query(False)):
    song = DataSystem.songs.Get(id)
    if song is None:
        raise HTTPException(404, detail="Song not found")
    if song.isCopywrited:
        raise HTTPException(404, detail="Song not found")
    if not re.match(r"[a-z0-9_]+", id):
        raise HTTPException(400, detail="Invaild Id")

    if export:
        filename = ExportSong(song) + ".mp3"
        filename = quote(filename)
        file_path = paths.PROCESSING_DIR / id
        return FileResponse(file_path, media_type="audio/mpeg", headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"})
    
    file_path = paths.MP3_DIR / id
    ngnixPath = f"/protected/{file_path.relative_to(paths.DATA_DIR)}"
    response = Response()
    response.headers["X-Accel-Redirect"] = ngnixPath
    response.headers["Content-Type"] = "audio/mpeg"
    return response

@app.get("/covers/{name:path}")
def GetCover(name: str, size: int = Query(128)):
    size = 2 ** round(math.log2(size))
    if size > 1024:
        size = 1024
    if size < 1:
        size = 1
    path = paths.ART_DIR / f"{name}.png"
    print(path)
    
    if not path.resolve().is_relative_to(paths.ART_DIR.resolve()): # not in art dir
        raise HTTPException(404, detail="Cover not found")
    if not path.exists():
        raise HTTPException(404, detail="Cover not found")

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

@app.get("/emotes/{name}")
def GetEmote(name: str, scale: int = Query(1)):
    emote = emotes.GetEmote(name)
    if not emote:
        raise HTTPException(404, detail="Emote not found")
    return RedirectResponse(emote + "/" + str(scale) + "x.webp")

# @app.get("/emotes")
# def GetEmotes(names: list[str] = Query(None), scale: int = Query(1)):
#     if names:
#         emotesList = {}
#         for name in names:
#             emote = emotes.GetEmote(name)
#             if not emote:
#                 raise HTTPException(404, detail="Emote not found")
#             emotesList[name] = emote + "/" + str(scale) + "x.webp"
#         return emotesList
#     else:
#         emotesList = {}
#         for name, emote in emotes.emotes.items():
#             emotesList[name] = emote + "/" + str(scale) + "x.webp"
#         return emotesList

class LoginRequest(BaseModel):
    username: str
    password: str
    create: bool = False
    remeber: bool = False

@app.post("/users/login")
def Login(req: LoginRequest, response: Response):
    username = req.username
    password = req.password
    create = req.create

    username = username.strip().lower()
    if len(username) > 32 or len(username) <= 0:
        raise HTTPException(400, detail="Invalid username")
    if not re.match(r"^[a-z0-9_-]+$", username):
        raise HTTPException(400, detail="Username contains invalid characters")
    
    if len(password) > config.USER_MAX_PASSWORD_LENGTH or len(password) <= 0:
        raise HTTPException(400, detail="Invalid password")

    if create:
        if len(password) < config.USER_MIN_PASSWORD_LENGTH:
            raise HTTPException(400, detail="Password too short")
        if DataSystem.users.UsernameExists(username):
            raise HTTPException(400, detail="Username already taken")
        if username in ["admin", "vedal", "vedal987", "neuro-sama", "evilneuro", "neuro", "evil"]:
            raise HTTPException(400, detail="Username is reserved")
        
        DataSystem.users.CreateWithPassword(username, password)
    
    user = DataSystem.users.GetUserFromLogin(username, password)
    if not user:
        raise HTTPException(401, detail="Invalid username or password")
    
    token, secret = DataSystem.tokens.CreateFromUser(user)
    response.set_cookie(
        key="sessionToken",
        value=f"{token.id}:{secret}",
        max_age=int(token.maxAge),
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )

    return {"success": True, "isAdmin": user.validAdmin, "id": user.id, "username": user.username}

@app.post("/me/logout")
def Logout(response: Response, sessionToken: str = Cookie(None)):
    if sessionToken:
        response.delete_cookie("sessionToken")
        id, secret = sessionToken.split(":")
        if id:
            DataSystem.tokens.RemoveId(id)
    return {"success": True}

@app.get("/me/session")
def GetSession(response: Response, sessionToken: str = Cookie(None)):
    if not sessionToken:
        raise HTTPException(401, detail="Token Required", headers={"invaild-token": "true"})
    id, secret = sessionToken.split(":")
    token = DataSystem.tokens.Get(id)
    if not token:
        raise HTTPException(401, detail="Invalid token", headers={"invaild-token": "true"})

    if DataSystem.tokens.HasExpired(token):
        if not DataSystem.tokens.ValidateSecret(token, secret):
            raise HTTPException(401, detail="Invalid token", headers={"invaild-token": "true"})
        
        newToken, newSecret = DataSystem.tokens.Refresh(token)
        if newSecret is None:
            raise HTTPException(401, detail="Token not renewable", headers={"invaild-token": "true"})
    
        response.set_cookie(
            key="sessionToken",
            value=f"{id}:{newSecret}",
            max_age=int(newToken.maxAge),
            httponly=True,
            secure=True,
            samesite="none",
            path="/"
        )
    else:
        if not DataSystem.tokens.ValidateToken(token, secret):
            raise HTTPException(401, detail="Invalid token", headers={"invaild-token": "true"})
        
    user = token.user
    if not user:
        raise HTTPException(401, detail="Invalid token", headers={"invaild-token": "true"})
    return {"success": True, "username": user.username, "id": user.id, "isAdmin": user.validAdmin}

@app.get("/me")
def GetUser(sessionToken: str = Cookie(None)):
    user = VailidateUser(sessionToken)
    return UserSerializer.SerializeToNetwork(user)

@app.delete("/me")
def DeleteUser(sessionToken: str = Cookie(None)):
    #TODO: Require password
    user = VailidateUser(sessionToken)
    DataSystem.users.Remove(user)
    return


class AddSharedPlaylistRequest(BaseModel):
    code: str

@app.post("/playlists/shared")
def AddSharedPlaylist(req: AddSharedPlaylistRequest, sessionToken: str = Cookie(None)):
    user = VailidateUser(sessionToken)
    playlist = ShareManager.GetPlaylist(req.code)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")
    
    newId = IDManager.NewId(Playlist)
    playlist.id = newId

    user.AddPlaylist(playlist)

    DataSystem.users.Save(user)
    DataSystem.playlists.Save(playlist)
    return {"playlist": PlaylistSerializer.SerializeToNetwork(playlist)}

@app.get("/playlists")
def GetPlaylists(ids: list[str] = Query(None), filters: str = Query(None), sessionToken: str = Cookie(None)):
    user = VailidateUser(sessionToken)
    if ids:
        playlists = []
        for id in ids:
            playlist = VailidatePlaylist(sessionToken, id)
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
def NewPlaylist(req: NewPlaylistRequest, sessionToken: str = Cookie(None)):
    user = VailidateUser(sessionToken)
    name = VerifyPlaylistName(req.name)

    if user.PlaylistLimitReached():
        raise HTTPException(400, detail="User has reached playlist limit")

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
def DeletePlaylist(id: str,  sessionToken: str = Cookie(None)):
    user = VailidateUser(sessionToken)
    playlist = VailidatePlaylist(sessionToken, id)
    user.RemovePlaylist(playlist)
    DataSystem.playlists.Remove(playlist)
    DataSystem.users.Save(user)
    return

class PlaylistSongUpdateRequest(BaseModel):
    songs: list[str]

@app.patch("/playlists/{id}/add")
def AddSongToPlaylist(id: str, req: PlaylistSongUpdateRequest, sessionToken: str = Cookie(None)):
    playlist = VailidatePlaylist(sessionToken, id)
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
def RemoveSongFromPlaylist(id: str, req: PlaylistSongUpdateRequest, sessionToken: str = Cookie(None)):
    playlist = VailidatePlaylist(sessionToken, id)
    for song in req.songs:
        song = DataSystem.songs.Get(song)
        if not song:
            raise HTTPException(404, detail="Song not found")
        if song not in playlist.songs:
            raise HTTPException(400, detail="Song not in playlist")
        playlist.RemoveSong(song)

    DataSystem.playlists.Save(playlist)
    return {"success": True}

class PatchPlaylistRequest(BaseModel):
    name: Optional[str]
    songIds: Optional[list[str]]

@app.patch("/playlists/{id}")
def PatchPlaylist(id: str, req: PatchPlaylistRequest, sessionToken: str = Cookie(None)):
    playlist = VailidatePlaylist(sessionToken, id)
    if req.name:
        playlist.name = VerifyPlaylistName(req.name)
    if req.songIds:
        playlist.songIds = []
        for id in req.songIds:
            song = DataSystem.songs.Get(id)
            if not song:
                raise HTTPException(404, detail="Song not found")
            playlist.AddSong(song)
    DataSystem.playlists.Save(playlist)
    return {"success": True}

    
@app.get("/search")
def Search(query: str = Query(""), maxResults: int = Query(20)):
    results = SearchSongs(query)
    return SongSerializer.SerializeAllToNetwork(results[:maxResults])

@app.post("/resync")
async def Resync(sessionToken: str = Cookie(None)):
    VailidateAdmin(sessionToken)
    task = asyncio.create_task(ResyncServer())
    task.add_done_callback(lambda task: task.exception())
    return