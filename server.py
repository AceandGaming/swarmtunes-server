from pydantic import BaseModel
from scripts.classes.song import SongManager
from scripts.classes.album import AlbumManager
from scripts.classes.user import UserManager, PlaylistManager, SessionManager, User, Playlist
from fastapi import FastAPI, HTTPException, Query, Form, Header, Depends
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import scripts.embed as embeds
import scripts.api.emotes as emotes
import time, math
import scripts.paths as paths
from scripts.download import DownloadMissingSongs
from scripts.filters import Filter
from scripts.export import ExportSong
from scripts.cover import GetCover as ResizeCover
import asyncio
import re
import os

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
    print("Loading songs...")
    SongManager.Load()
    print("Generating albums...")
    AlbumManager.GenerateAlbums()
    print("Loading playlists...")
    PlaylistManager.Load()
    print(f"Loaded {len(SongManager.songs)} songs, {len(AlbumManager.albums)} albums and {len(PlaylistManager.playlists)} playlists")
    print("Loading users...")
    UserManager.Load()
    print(f"Loaded {len(UserManager.users)} users")
    print("Loading emotes...")
    emotes.Load()
    print(f"Loaded {len(emotes.emotes)} emotes")
    print(f"Server started in {math.floor((time.time() - startTime) * 1000)} miliseconds")
    print("todo: Fix discord bot")
    return app

def GetFilters(filterString: str):
    filters = []
    for split in filterString.split(","):
        filters.append(Filter.CreateFromString(split))
    return filters
def VailidateToken(token: str):
    user = SessionManager.GetUser(token)
    if not user:
        raise HTTPException(401, detail="Invalid token", headers={"token-expired": "true"})
    return user
def VailidatePlaylist(token: str, uuid: str):
    user = VailidateToken(token)
    playlist = PlaylistManager.GetPlaylist(uuid)
    if not playlist:
        raise HTTPException(404, detail="Playlist not found")
    if playlist.user != user:
        raise HTTPException(403, detail="Playlist not owned by user")
    return playlist

InitializeServer()

@app.on_event("startup")
async def CleanUp():
    print("Cleaning up...")
    SongManager.DeleteSongsWithoutReference()
    #PlaylistManager.DeletePlaylistsWithoutReference()
    #UserManager.DeleteUsersWithoutReference()
    paths.ClearPending()
    paths.ClearProcessing()
    print("Cleanup complete")
    async def Download():
        print("Downloading new files...")
        await DownloadMissingSongs()
        print("Downloading new files complete")
        AlbumManager.GenerateAlbums()
        print("New songs downloaded and albums generated")
    if os.getenv("DATA_PATH") is None:
        asyncio.create_task(Download())
@app.on_event("shutdown")
async def Shutdown():
    print("Saving...")
    SongManager.Save()
    PlaylistManager.Save()
    UserManager.Save()
    print("Saved!")

@app.get("/")
async def root(song = Query(...)):
    if song:
        song = SongManager.GetSong(song)
        if not song:
            return
        return HTMLResponse(embeds.SongEmbed(song))
    return {
        "message": "Welcome to the SwarmTunes API", 
        "status": "ok",
        "songs": len(SongManager.songs),
        "albums": len(AlbumManager.albums),
        "playlists": len(PlaylistManager.playlists),
        "users": len(UserManager.users),
        "emotes": len(emotes.emotes),
        "current-path": paths.DATA_PATH
    }

@app.get("/swarmfm")
def SwarmFM():
    return {"https://cast.sw.arm.fm/stream"}    

@app.get("/songs")
def GetSongs(uuids: list[str] = Query(None), filters: str = Query(None), maxResults: int = Query(100)):
    if uuids:
        songs = []
        for uuid in uuids:
            song = SongManager.GetSong(uuid)
            if not song:
                raise HTTPException(404, detail="Song not found")
            songs.append(song)
        return SongManager.ConvertToNetworkDict(songs)
    elif filters:
        songs = SongManager.GetSongs(GetFilters(filters))
        # except:
        #     raise HTTPException(400, detail="Invalid filters")
        songs = songs[:maxResults]
        return SongManager.ConvertToNetworkDict(songs) #type: ignore
    else:
        songs = SongManager.GetSongs()
        songs = songs[:maxResults]
        return SongManager.ConvertToNetworkDict(songs) #type: ignore

@app.get("/files/{uuid}")
def GetSongFile(uuid: str, export: bool = Query(False)):
    if export:
        try: filename = ExportSong(uuid)
        except: raise HTTPException(404, detail="Song not found")
        file_path = paths.PROCESSING_DIR / uuid
        return FileResponse(file_path, media_type="audio/mpeg", headers={"Content-Disposition": f"attachment; filename={filename}"})
    if not SongManager.GetSong(uuid):
        raise HTTPException(404, detail="Song not found")
    file_path = paths.MUSIC_DIR / uuid
    return FileResponse(file_path, media_type="audio/mpeg", headers={"Accept-Ranges": "bytes"})

@app.get("/covers/{name}")
def GetCover(name: str, size: int = Query(128)):
    if size > 1024:
        size = 1024
    if size < 1:
        size = 1
    path = None
    match name:
        case "neuro":
            path = paths.COVERS_DIR / "neuro.png"
        case "evil":
            path = paths.COVERS_DIR / "evil.png"
        case "duet":
            path = paths.COVERS_DIR / "duet.png"
        case "swarmfm":
            path = paths.COVERS_DIR / "swarmfm.png"
        case _:
            song = SongManager.GetSong(name)
            if not song:
                raise HTTPException(404, detail="Cover not found")
            path = song.cover_art
    file = ResizeCover(path, size)
    if not file:
        raise HTTPException(404, detail="Cover not found")

    return FileResponse(file, media_type="image/webp", headers={"Accept-Ranges": "bytes"})
    

@app.get("/albums")
def GetAlbums(uuids: list[str] = Query(None), filters: str = Query(None)):
    if uuids:
        albums = []
        for uuid in uuids:
            album = AlbumManager.GetAlbum(uuid)
            if not album:
                raise HTTPException(404, detail="Album not found")
            albums.append(album)
        return AlbumManager.ConvertToNetworkDict(albums)
    elif filters:
        try: albums = AlbumManager.GetAlbums(filters=GetFilters(filters))
        except:
            raise HTTPException(400, detail="Invalid filters")
        return AlbumManager.ConvertToNetworkDict(albums, True) #type: ignore
    else:
        albums = AlbumManager.GetAlbums()
        return AlbumManager.ConvertToNetworkDict(albums, True) #type: ignore

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
        if UserManager.GetUserWithUsername(username):
            raise HTTPException(400, detail="Username already taken")
        
        UserManager.AddUser(User(username, password))
    token = SessionManager.Login(username, password)
    if not token:
        raise HTTPException(401, detail="Invalid username or password")
    return {"token": token}

@app.post("/users/logout")
def Logout(token: str = Depends(auth)):
    if not SessionManager.TokenIsValid(token):
        raise HTTPException(401, detail="Invalid token")
    SessionManager.Logout(token)
    return

@app.get("/playlists")
def GetPlaylists(uuids: list[str] = Query(None), filters: str = Query(None), token: str = Depends(auth)):
    user = VailidateToken(token)
    if uuids:
        playlists = []
        for uuid in uuids:
            playlist = VailidatePlaylist(token, uuid)
            playlists.append(playlist)
        return PlaylistManager.ConvertToNetworkDict(playlists)
    elif filters:
        try: playlists = PlaylistManager.GetPlaylists(GetFilters(filters), user.playlists)
        except:
            raise HTTPException(400, detail="Invalid filters")
        return PlaylistManager.ConvertToNetworkDict(playlists, True)
    else:
        playlists = user.playlists
        return PlaylistManager.ConvertToNetworkDict(playlists, True)

class NewPlaylistRequest(BaseModel):
    name: str
    songs: list[str] = []

@app.post("/playlists/new")
def NewPlaylist(req: NewPlaylistRequest, token: str = Depends(auth)):
    user = VailidateToken(token)
    name = req.name.strip()
    if len(name) > 32 or len(name) <= 0:
        raise HTTPException(400, detail="Invalid playlist name")
    if not re.match(r"^[0-9A-Za-z_ ]+$", name):
        raise HTTPException(400, detail="Playlist name contains invalid characters")

    playlist = Playlist(name, user.uuid)
    for uuid in req.songs:
        song = SongManager.GetSong(uuid)
        if not song:
            raise HTTPException(404, detail="Song not found")
        playlist.AddSong(song)
    PlaylistManager.AddPlaylist(playlist)
    return playlist.ToNetworkDict()

class DeletePlaylistRequest(BaseModel):
    uuid: str

@app.post("/playlists/delete")
def DeletePlaylist(req: DeletePlaylistRequest, token: str = Depends(auth)):
    playlist = VailidatePlaylist(token, req.uuid)
    PlaylistManager.RemovePlaylist(playlist)
    return {"success": True}

class PlaylistSongUpdateRequest(BaseModel):
    songs: list[str]

@app.post("/playlists/{uuid}/add")
def AddSongToPlaylist(uuid: str, req: PlaylistSongUpdateRequest, token: str = Depends(auth)):
    playlist = VailidatePlaylist(token, uuid)
    for song in req.songs:
        song = SongManager.GetSong(song)
        if not song:
            raise HTTPException(404, detail="Song not found")
        if song in playlist.songs:
            raise HTTPException(400, detail="Song already in playlist")
        playlist.AddSong(song)

    return {"success": True}

@app.post("/playlists/{uuid}/remove")
def RemoveSongFromPlaylist(uuid: str, req: PlaylistSongUpdateRequest, token: str = Depends(auth)):
    playlist = VailidatePlaylist(token, uuid)
    for song in req.songs:
        song = SongManager.GetSong(song)
        if not song:
            raise HTTPException(404, detail="Song not found")
        if song not in playlist.songs:
            raise HTTPException(400, detail="Song not in playlist")
        playlist.RemoveSong(song)
    return {"success": True}

class RenamePlaylistRequest(BaseModel):
    name: str

@app.post("/playlists/{uuid}/rename")
def RenamePlaylist(uuid: str, req: RenamePlaylistRequest, token: str = Depends(auth)):
    playlist = VailidatePlaylist(token, uuid)
    name = req.name.strip()
    if len(name) > 32 or len(name) <= 0:
        raise HTTPException(400, detail="Invalid playlist name")
    if not re.match(r"^[0-9A-Za-z_ ]+$", name):
        raise HTTPException(400, detail="Playlist name contains invalid characters")
    playlist.title = name
    return {"success": True}
    