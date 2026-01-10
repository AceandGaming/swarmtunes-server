from mutagen.id3 import ID3
import mutagen.id3._frames as ID3Frames
import scripts.paths as paths
from scripts.types import Song, Album, Playlist
import shutil
import zipfile
import json
from scripts.cover import GetCoverPathFromSong

def CreateAlbumName(song):
    return f"{" and ".join(song.singers)} Karaoke"

def ExportSong(song: Song):
    fromPath = paths.MP3_DIR / song.id
    toPath = paths.PROCESSING_DIR / song.id
    if not fromPath.exists():
        raise Exception("Song not found")

    shutil.copy(fromPath, toPath)
    audio = ID3(toPath)
    audio["TIT2"] = ID3Frames.TIT2(encoding=3, text=song.title) #title
    audio["TPE1"] = ID3Frames.TPE1(encoding=3, text=song.artist) #artist
    audio["TALB"] = ID3Frames.TALB(encoding=3, text=CreateAlbumName(song)) #album

    cover = paths.COVERS_DIR / song.id
    if not cover.exists():
        cover = GetCoverPathFromSong(song)
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

def ExportPlaylist(playlist: Playlist):
    files = []
    for song in playlist.songs:
        if song.isCopywrited:
            continue
        filename = ExportSong(song)
        files.append((
            paths.PROCESSING_DIR / song.id,
            filename + ".mp3"
        ))

    path = paths.PROCESSING_DIR / playlist.id
    metadata = {
        "date": playlist.date.isoformat(),
        "type": playlist.coverType,
        "title": playlist.name
    }
    with zipfile.ZipFile(path, "w") as zipf:
        for path, name in files:
            zipf.write(path, arcname=name)
        zipf.writestr("metadata.json", json.dumps(metadata, indent=2))

    return playlist.name