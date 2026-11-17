import logging
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from st.core.config import get_config
from st.features.album import Album, AlbumType, create_album_service
from st.features.song import Song, create_song_service
from st.features.song.song import SongType

log = logging.getLogger("automated")


def create_setlist_title(date: datetime, songs: list[Song]) -> str:
    singer_count: dict[frozenset[str], int] = {}
    for song in songs:
        singers = frozenset(song.singer_names)
        if singers in singer_count:
            singer_count[singers] += 1
        else:
            singer_count[singers] = 1

    singers = max(singer_count, key=lambda singers: singer_count[singers])

    name = ""
    if len(singers) == 1:
        name = list(singers)[0]
    elif {"Neuro-sama", "Evil Neuro"} == singers:
        name = "Neuro and Evil"
    else:
        name = f"{date.strftime('%-d %B %Y')} Setlist"

    if (date.month, date.day) == (12, 25):
        name = name.strip() + " Christmas"
    elif (date.month, date.day) == (10, 29):
        name = name.strip() + " Halloween"

    return name


def create_collection_title(disc: int) -> str:
    return f"Disc {disc}"


def update_albums(db: Session):
    log.info("Updating albums...")
    config = get_config()

    song_service = create_song_service(db)

    songs = song_service.get_all()

    by_disc: dict[int, list[Song]] = defaultdict(list)
    by_date: dict[datetime, list[Song]] = defaultdict(list)
    by_date_ep: dict[datetime, list[Song]] = defaultdict(list)

    for song in songs:
        if song.disc:
            by_disc[song.disc].append(song)

        if song.type == SongType.ORIGINAL:
            by_date_ep[song.date_released].append(song)
        else:
            by_date[song.date_released].append(song)

    for date in list(by_date.keys()):
        if len(by_date[date]) < config.automated.album_min_songs:
            del by_date[date]

    log.info(
        f"Grouped {len(by_date)} songs by date and {len(by_disc)} by disc."
    )

    album_service = create_album_service(db)

    for date, songs in by_date.items():
        album = (
            album_service.query()
            .filter(Album.type == AlbumType.SETLIST, Album.date == date)
            .first()
        )

        if album:
            if {song.id for song in album.songs} == {song.id for song in songs}:
                continue

            album.title = create_setlist_title(date, songs)
            album.songs = songs
            log.debug(
                f"Updating album {album.title} with {len(album.songs)} songs."
            )
        else:
            album = Album(
                type=AlbumType.SETLIST,
                title=create_setlist_title(date, songs),
                date=date,
                songs=songs,
            )
            db.add(album)
            log.debug(
                f"Creating album {album.title} with {len(album.songs)} songs."
            )

        album.last_updated = datetime.now(timezone.utc)

    for date, songs in by_date_ep.items():
        album = (
            album_service.query()
            .filter(Album.type == AlbumType.EP, Album.date == date)
            .first()
        )

        title = songs[0].title if len(songs) == 1 else "EP"

        if album:
            if {song.id for song in album.songs} == {song.id for song in songs}:
                continue

            album.title = title
            album.songs = songs
            log.debug(
                f"Updating album {album.title} with {len(album.songs)} songs."
            )
        else:
            album = Album(
                type=AlbumType.EP,
                title=title,
                date=date,
                songs=songs,
            )
            db.add(album)
            log.debug(
                f"Creating album {album.title} with {len(album.songs)} songs."
            )

        album.last_updated = datetime.now(timezone.utc)

    for disc, songs in by_disc.items():
        album = (
            album_service.query()
            .filter(Album.type == AlbumType.DISC, Album.disc == disc)
            .first()
        )

        if album:
            if {song.id for song in album.songs} == {song.id for song in songs}:
                continue

            album.title = create_collection_title(disc)
            album.songs = songs
            log.debug(
                f"Updating album {album.title} with {len(album.songs)} songs."
            )
        else:
            album = Album(
                type=AlbumType.DISC,
                title=create_collection_title(disc),
                disc=disc,
                songs=songs,
            )
            db.add(album)
            log.debug(
                f"Creating album {album.title} with {len(album.songs)} songs."
            )

        album.last_updated = datetime.now(timezone.utc)

    log.info("Done updating albums.")
