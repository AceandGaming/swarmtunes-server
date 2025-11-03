from nanoid import generate
from scripts.classes.song import SongManager, Song
import scripts.paths as paths
import json

class ShareManager:
    songLinks = {}

    @staticmethod
    def ShareSong(song: Song):
        link = generate(size=8)
        while link in ShareManager.songLinks:
            link = generate(size=8)
        ShareManager.songLinks[link] = song.uuid
        return link
    @staticmethod
    def GetSong(link: str):
        uuid = ShareManager.songLinks.get(link)
        if not uuid:
            return
        return SongManager.GetSong(uuid)
    
    @staticmethod
    def Save():
        data = {
            "songLinks": ShareManager.songLinks
        }
        with open(paths.SHARE_FILE, "w") as f:
            f.write(json.dumps(data, indent=2))
    @staticmethod
    def Load():
        if not paths.SHARE_FILE.exists():
            return
        with open(paths.SHARE_FILE, "r") as f:
            data = json.load(f)
            ShareManager.songLinks = data["songLinks"]