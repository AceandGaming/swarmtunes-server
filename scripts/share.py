from nanoid import generate
from scripts.types import Song, Playlist
from scripts.data_system import DataSystem
import scripts.paths as paths
import json

class ShareManager:
    songLinks = {}
    playlistLinks = {}

    @staticmethod
    def ShareSong(song: Song):
        link = generate(size=8)
        while link in ShareManager.songLinks:
            link = generate(size=8)
        ShareManager.songLinks[link] = song.id
        return link
    @staticmethod
    def GetSong(link: str):
        id = ShareManager.songLinks.get(link)
        if not id:
            return
        return DataSystem.songs.Get(id)

    @staticmethod
    def SharePlaylist(playlist: Playlist):
        link = generate(size=8)
        while link in ShareManager.playlistLinks:
            link = generate(size=8)
        ShareManager.playlistLinks[link] = playlist.id
        return link

    @staticmethod
    def GetPlaylist(link: str):
        id = ShareManager.playlistLinks.get(link)
        if not id:
            return
        return DataSystem.playlists.Get(id)
    
    @staticmethod
    def Save():
        data = {
            "songLinks": ShareManager.songLinks,
            "playlistLinks": ShareManager.playlistLinks
        }
        with open(paths.SHARE_FILE, "w") as f:
            f.write(json.dumps(data, indent=2))
    @staticmethod
    def Load():
        if not paths.SHARE_FILE.exists():
            return
        with open(paths.SHARE_FILE, "r") as f:
            data = json.load(f)
            ShareManager.songLinks = data.get("songLinks", {})
            ShareManager.playlistLinks = data.get("playlistLinks", {})