from mutagen.id3 import ID3
import mutagen.id3._frames as ID3Frames
import scripts.paths as paths
from scripts.types import Song, Album
import shutil
import zipfile
import json

def CreateAlbumName(song):
    return f"{" and ".join(song.singers)} Karaoke"
def ExportSong(song: Song):
    path = paths.PROCESSING_DIR / song.id
    shutil.copy(paths.MP3_DIR / song.id, path)
    audio = ID3(path)
    audio["TIT2"] = ID3Frames.TIT2(encoding=3, text=song.title) #title
    audio["TPE1"] = ID3Frames.TPE1(encoding=3, text=song.artist) #artist
    audio["TALB"] = ID3Frames.TALB(encoding=3, text=CreateAlbumName(song)) #album

    cover = paths.COVERS_DIR / song.id
    if not cover.exists():
        cover = paths.ART_DIR / ((song.coverType or "duet") + ".png")
    with open(cover, "rb") as f:
        audio["APIC"] = ID3Frames.APIC( #cover
            encoding=3,
            mime="image/png",
            type=3,
            desc="Cover",
            data=f.read(),
        )
    audio.save(v2_version=3)

    return str(song)
def ExportAlbum(album: Album):
    files = []
    for song in album.songs:
        filename = ExportSong(song)
        files.append((
            paths.PROCESSING_DIR / song.id,
            filename + ".mp3"
        ))

    path = paths.PROCESSING_DIR / album.id
    metadata = {
        "date": album.date.isoformat(),
        "type": album.coverType,
        "title": album.PrettyName
    }
    with zipfile.ZipFile(path, "w") as zipf:
        for path, name in files:
            zipf.write(path, arcname=name)
        zipf.writestr("metadata.json", json.dumps(metadata, indent=2))

    return album.PrettyName