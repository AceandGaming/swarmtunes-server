from .song import Song
from .api import NetworkSongV1, NetworkSongV2
from core.cover import get_song_artwork
from features.song.song import Song
from features.artist.convert import to_network_v2 as to_network_v2_artist
from typing import Literal, cast


def to_network_v1(song: Song) -> NetworkSongV1:
    artworks = {artwork.type: f"{artwork.type}/{artwork.name}" for artwork in get_song_artwork(song)}
    ytId = None
    for audio in song.audio_references:
        if audio.type == "youtube":
            ytId = audio.id

    return {
        "id": str(song.id),
        "title": song.title,
        "artist": ", ".join(song.artist_names),
        "cover": artworks["custom"] or artworks["default"] or artworks["plush"] or None,
        "singers": song.singer_names,
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
        "id": song.str_id,
        "title": song.title,
        "titleOriginal": song.title_original,
        "artists": [to_network_v2_artist(artist) for artist in song.artists],
        "singers": [to_network_v2_artist(artist) for artist in song.singers],
        "type": song.type.value,
        "dateReleased": song.date_released.isoformat(),
        "seconds": int(song.duration),
        "artworks": {artwork.type: artwork.name for artwork in get_song_artwork(song)},
        "audioType": audio_type,
        "audioId": audio_id,
        "drmProtected": song.is_copyrighted
    }
