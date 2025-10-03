from mutagen.id3 import ID3
import mutagen.id3._frames as ID3Frames
import scripts.paths as paths
from scripts.classes.song import SongManager
import shutil

def CreateAlbumName(song):
    return f"{song.cover_artist} Karaoke"
def ExportSong(uuid: str):
    song = SongManager.GetSong(uuid)
    if song is None:
        raise FileNotFoundError("Song not found")
    path = paths.PROCESSING_DIR / uuid
    shutil.copy(paths.MUSIC_DIR / uuid, path)
    audio = ID3(path)
    audio["TIT2"] = ID3Frames.TIT2(encoding=3, text=song.title) #title
    audio["TPE1"] = ID3Frames.TPE1(encoding=3, text=song.artist) #artist
    audio["TALB"] = ID3Frames.TALB(encoding=3, text=CreateAlbumName(song)) #album

    cover = paths.COVERS_DIR / (uuid + ".png")
    if not cover.exists():
        cover = paths.COVERS_DIR / (song.type + ".png")
    with open(cover, "rb") as f:
        audio["APIC"] = ID3Frames.APIC( #cover
            encoding=3,
            mime="image/png",
            type=3,
            desc="Cover",
            data=f.read(),
        )
    audio.save(v2_version=3)

    return f"{song.title} by {song.artist} ({song.type})"
    