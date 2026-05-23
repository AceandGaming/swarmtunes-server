from .song import Song, SongAudio
from .json import NetworkSongV1, NetworkSongV2
from .cover import get_song_artwork
from database.models.song import SQLSong
from database.models.artist import SQLArtist
from typing import Literal, cast
from dataclasses import asdict

def to_network_v1(song: Song) -> NetworkSongV1:
    artworks = {artwork.type: f"{artwork.type}/{artwork.name}" for artwork in get_song_artwork(song)}
    ytId = None
    for audio in song.audio_references:
        if audio.type == "youtube":
            ytId = audio.id

    return {
        "id": song.id,
        "title": song.title,
        "artist": ", ".join(song.artists),
        "cover": artworks["custom"] or artworks["default"] or artworks["plush"] or None,
        "singers": song.singers,
        "date": song.date_released.strftime("%Y-%m-%d"),
        "isOriginal": song.type == "original",
        "youtubeId": ytId
    }

def to_network_v2(song: Song) -> NetworkSongV2:
    audio_id = None
    audio_type: Literal["audio", "youtube"] | None = None
    for refrence in song.audio_references:
        if refrence.type in ["audio", "youtube"]:
            audio_id = refrence.id
            audio_type = cast(Literal["audio", "youtube"], refrence.type)
            break

    if audio_id is None or audio_type is None:
        raise Exception("Song has no supported audio")

    return {
        "id": song.id,
        "title": song.title,
        "titleOriginal": song.title_original,
        "artists": song.artists,
        "singers": song.singers,
        "type": song.type,
        "dateReleased": song.date_released.isoformat(),
        "seconds": int(song.duration),
        "artworks": {artwork.type: artwork.name for artwork in get_song_artwork(song)},
        "audioType": audio_type,
        "audioId": audio_id,
        "drmProtected": song.is_copyrighted
    }

def to_sql(song: Song) -> SQLSong:
    return SQLSong(
        # methods from id object
        id = song.id,
        date_created = song.date_created,
        disabled_at = song.disabled_at,
        hidden=song.hidden,

        title = song.title,
        title_original = song.title_original,

        artists = [SQLArtist(name=artist) for artist in song.artists],
        singers = [SQLArtist(name=singer) for singer in song.singers],
        type = song.type,

        date_released = song.date_released,
        disc = song.disc,
        is_copyrighted = song.is_copyrighted,
        custom_artwork = song.custom_artwork,

        seconds = song.duration,
        audio_references = [asdict(audio) for audio in song.audio_references],
        metadata_source = song.metadata_source
    ) 

def from_sql(song: SQLSong) -> Song:
    refrences = []
    for audio in song.audio_references:
        refrences.append(SongAudio(
            type=audio["type"], 
            id=audio["id"]
        ))

    return Song(
        # methods from id object
        id = song.id,
        date_created = song.date_created,
        disabled_at = song.disabled_at,
        hidden=song.hidden,

        title = song.title,
        title_original = song.title_original,

        artists = [artist.name for artist in song.artists],
        singers = [singer.name for singer in song.singers],
        type = song.type,

        date_released = song.date_released,
        disc = song.disc,
        is_copyrighted = song.is_copyrighted,
        custom_artwork = song.custom_artwork,

        seconds = song.seconds,
        audio_references = refrences,
        metadata_source = song.metadata_source
    )

__all__ = [
    "Song", 
    "SongAudio", 
    "get_song_artwork", 
    "to_network_v1", 
    "to_network_v2", 
    "to_sql", 
    "from_sql"
]