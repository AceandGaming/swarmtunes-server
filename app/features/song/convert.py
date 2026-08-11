from typing import Literal, cast, overload

from features.artist.convert import to_network_v2 as to_network_v2_artist
from features.artwork import create_path, get_song_artwork

from .api import NetworkSongV1, NetworkSongV2
from .song import Song


def to_network_v1(song: Song) -> NetworkSongV1:
    ytId = None
    for audio in song.audio_references:
        if audio.type == "youtube":
            ytId = audio.external_id
            break

    art = create_path(get_song_artwork(song))

    return {
        "id": str(song.id),
        "title": song.title,
        "artist": ", ".join(song.artist_names),
        "artists": song.artist_names,
        "cover": art,
        "coverArt": art,
        "singers": song.singer_names,
        "date": song.date_released.strftime("%Y-%m-%d"),
        "isOriginal": song.type == "original",
        "youtubeId": ytId,
        "seconds": int(song.seconds),
    }


def to_network_v2(song: Song) -> NetworkSongV2:

    audio = song.audio_references[0]

    return {
        "id": song.str_id,
        "title": song.title,
        "titleOriginal": song.title_original,
        "artists": [to_network_v2_artist(artist) for artist in song.artists],
        "singers": [to_network_v2_artist(artist) for artist in song.singers],
        "type": song.type.value,
        "dateReleased": song.date_released.isoformat(),
        "seconds": int(song.duration),
        "artworks": {
            artwork.type: artwork.name for artwork in get_song_artwork(song)
        },
        "playable": song.playable,
        "audioType": audio.type.value,
        "audioId": audio.external_id,
        "drmProtected": song.is_copyrighted,
    }
