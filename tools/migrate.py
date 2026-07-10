"""A tool to migrate from the old server to the new one"""

import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, TypedDict

import questionary

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "app"))

import re

from database.database import create as create_db  # noqa: E402
from database.dependencies import db_session  # noqa: E402
from features.identity import AuthProvider, Identity, LegacyCredentials  # noqa: E402
from features.playlist import Playlist  # noqa: E402
from features.song import Song  # noqa: E402
from features.user import User, UserRoles  # noqa: E402


class UserData(TypedDict):
    playlistIds: Optional[list[str]]


@dataclass(eq=False)
class OldUser:
    id: str
    username: str
    password: str
    date: datetime
    userData: UserData


@dataclass(eq=False)
class OldPlaylist:
    id: str
    name: str
    userId: str
    date: datetime
    songIds: list[str]


class SongExternalStorage(TypedDict):
    googleDriveId: Optional[str]
    youtubeId: Optional[str]


@dataclass(kw_only=True, eq=False)
class OldSong:
    id: str
    title: str
    artists: list[str]
    singers: list[str]
    date: datetime
    duration: Optional[float] = None
    coverArt: Optional[str] = None
    subtitle: Optional[str] = None
    isOriginal: bool = False
    storage: SongExternalStorage
    isCopywrited: bool = False
    fingerprint: Optional[str] = None


def load_user(path: Path):
    data = json.loads(path.read_text())

    if "date" in data:
        data["date"] = datetime.fromisoformat(data["date"]).replace(tzinfo=timezone.utc)
    else:
        data["date"] = datetime.now()
    if "userData" in data:
        data["userData"] = UserData(**data["userData"])

    return OldUser(**data)


def load_playlist(path: Path):
    data = json.loads(path.read_text())

    data["date"] = datetime.fromisoformat(data["date"]).replace(tzinfo=timezone.utc)
    return OldPlaylist(**data)


def load_song(path: Path):
    data = json.loads(path.read_text())

    data["date"] = datetime.fromisoformat(data["date"]).replace(tzinfo=timezone.utc)

    if "storage" in data:
        data["storage"] = SongExternalStorage(**data["storage"])

    if data.get("artist") is not None:
        data["artists"] = data["artist"].split(", ")
        del data["artist"]
    return OldSong(**data)


def load_old_data(path: Path):
    songs_path = path / "songs"
    users_path = path / "users"
    playlists_path = path / "playlists"

    return (
        [load_song(s) for s in songs_path.iterdir()],
        [load_user(u) for u in users_path.iterdir()],
        [load_playlist(p) for p in playlists_path.iterdir()],
    )


def normlize_title(title: str):
    title = title.lower()
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"\(.*\)", "", title)
    title = re.sub(r"\[^a-z]", "", title)
    return title.strip()


def create_song_lookup(
    old_songs: list[OldSong], new_songs: list[Song]
) -> dict[OldSong, Song]:
    lookup: dict[OldSong, Song] = {}
    potental_matches: dict[OldSong, list[Song]] = defaultdict(list)

    for old_song in old_songs:
        title_a = normlize_title(old_song.title)
        for new_song in new_songs:
            title_b = normlize_title(new_song.title)

            if title_a != title_b:
                continue
            if (old_song.date - new_song.date_released).days > 1:
                continue

            if (
                old_song.title.lower() == new_song.title.lower()
                and len(
                    {normlize_title(a) for a in old_song.artists}
                    & {normlize_title(a) for a in new_song.artist_names}
                )
                > 0
            ):
                lookup[old_song] = new_song
            else:
                potental_matches[old_song].append(new_song)

    missing: dict[OldSong, list[Song] | None]
    missing = {old_song: None for old_song in old_songs if old_song not in lookup}
    missing |= {
        old_song: matches
        for old_song, matches in potental_matches.items()
        if old_song not in lookup
    }

    print(f"{len(missing)} songs could not be found.")
    # for old_song, matches in missing.items():
    #     choices = [
    #         questionary.Choice(
    #             f"{song.title} - {song.artist_names and song.artist_names[0]} ({song.singer_names and song.singer_names[0]})",
    #             song,
    #             description=f"{song.date_released} - {song.artist_names} | {song.singer_names}",
    #         )
    #         for song in sorted(matches or new_songs, key=lambda s: s.title)
    #     ]
    #     song = questionary.select(
    #         f"Song: {old_song.title} could not be found.\nArtists: {old_song.artists}\nSingers: {old_song.singers}\nDate: {old_song.date}",
    #         choices=choices,
    #         show_description=True,
    #         use_search_filter=True,
    #         use_jk_keys=False,
    #     ).ask()

    #     lookup[old_song] = song

    return lookup


def main():
    # while True:
    #     data_path = Path(input("Please enter the path to the old data: ")).resolve()
    #     if data_path.is_dir():
    #         break
    #     print("Invalid path. Please try again.")
    data_path = Path("/home/ace/Downloads/old_data/")

    old_songs, old_users, old_playlists = load_old_data(data_path)
    print("Loaded old data.")
    print(
        f"Found {len(old_songs)} songs, {len(old_users)} users and {len(old_playlists)} playlists."
    )

    playlist_lookup = {playlist.id: playlist for playlist in old_playlists}
    song_lookup = {song.id: song for song in old_songs}

    create_db()
    with db_session() as db:
        new_songs = db.query(Song).all()

        lookup = create_song_lookup(old_songs, new_songs)

        for user in old_users:
            new_user = User(
                username=user.username,
                role=UserRoles.USER,
            )
            identity = Identity(
                provider=AuthProvider.LEGACY,
                provider_id=user.username,
                legacy_creds=LegacyCredentials(password_hash=user.password),
            )
            new_user.identities.append(identity)

            for playlist_id in set(user.userData.get("playlistIds") or []):
                playlist = playlist_lookup[playlist_id]
                new_playlist = Playlist(title=playlist.name)
                new_songs = set()

                for song_id in playlist.songIds:
                    song = song_lookup[song_id]
                    new_song = lookup.get(song)
                    if new_song:
                        new_songs.add(new_song)

                for song in new_songs:
                    new_playlist.add_song(song)

                db.add(new_playlist)
                new_user.playlists.append(new_playlist)

            db.add(new_user)


if __name__ == "__main__":
    main()
