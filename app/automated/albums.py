import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from core.config import get_config
from features.album import Album, AlbumType, create_album_service
from features.song import Song, create_song_service

log = logging.getLogger("automated")


def create_setlist_title(date: datetime) -> str:
    return f"{date.strftime('%-d %B %Y')} Setlist"


def create_collection_title(disc: int) -> str:
    return f"Disc {disc}"


def update_albums(db: Session):
    log.info("Updating albums...")
    config = get_config()

    song_service = create_song_service(db)

    songs = song_service.get_all()

    by_disc: dict[int, list[Song]] = {}
    by_date: dict[datetime, list[Song]] = {}

    for song in songs:
        if song.disc:
            if song.disc not in by_disc:
                by_disc[song.disc] = []
            by_disc[song.disc].append(song)

        if song.date_released not in by_date:
            by_date[song.date_released] = []
        by_date[song.date_released].append(song)

    for date in list(by_date.keys()):
        if len(by_date[date]) < config.album_min_songs:
            del by_date[date]

    log.info(f"Grouped {len(by_date)} songs by date and {len(by_disc)} by disc.")

    album_service = create_album_service(db)

    for date, songs in by_date.items():
        album = (
            album_service.query()
            .filter(Album.type == AlbumType.DATE_SETLIST, Album.date == date)
            .first()
        )

        if album:
            if {song.id for song in album.songs} == {song.id for song in songs}:
                continue

            album.title = create_setlist_title(date)
            album.songs = songs
            log.debug(f"Updating album {album.title} with {len(album.songs)} songs.")
        else:
            album = Album(
                type=AlbumType.DATE_SETLIST,
                title=create_setlist_title(date),
                date=date,
                songs=songs,
            )
            db.add(album)
            log.debug(f"Creating album {album.title} with {len(album.songs)} songs.")

        album.last_updated = datetime.now(timezone.utc)

    for disc, songs in by_disc.items():
        album = (
            album_service.query()
            .filter(Album.type == AlbumType.DISC_COLLECTION, Album.disc == disc)
            .first()
        )

        if album:
            if {song.id for song in album.songs} == {song.id for song in songs}:
                continue

            album.title = create_collection_title(disc)
            album.songs = songs
            log.debug(f"Updating album {album.title} with {len(album.songs)} songs.")
        else:
            album = Album(
                type=AlbumType.DISC_COLLECTION,
                title=create_collection_title(disc),
                disc=disc,
                songs=songs,
            )
            db.add(album)
            log.debug(f"Creating album {album.title} with {len(album.songs)} songs.")

        album.last_updated = datetime.now(timezone.utc)

    log.info("Done updating albums.")
