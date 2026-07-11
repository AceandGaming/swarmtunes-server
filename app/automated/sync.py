import logging
import multiprocessing
from multiprocessing import Pool, cpu_count

from sqlalchemy.orm import Session

from core.paths import AUDIO, CORRECT, DOWNLOADS
from external.rclone_api import DriveFile, download_files, get_all_files
from features.song import (
    AudioReferenceType,
    SongAudioReference,
    create_song_service,
)

from .downloader.correct import correct_and_convert_mp3
from .downloader.metadata import Metadata, load_file_metadata

log = logging.getLogger("automated")


def get_new_drive_files(db: Session) -> list[DriveFile]:
    files = get_all_files()

    log.info(f"Checking {len(files)} files on Drive.")

    new = []
    for file in files:
        refs = (
            db.query(SongAudioReference)
            .filter(
                SongAudioReference.type == AudioReferenceType.GOOGLE_DRIVE,
                SongAudioReference.external_id == file.id,
            )
            .all()
        )
        if not refs:
            log.debug(f"Found new file on Drive: {file.filename}")
            new.append(file)

    log.info(f"Found {len(new)} new files on Drive.")
    return new


def load_metadata(file):
    return load_file_metadata(DOWNLOADS / file.path), file


def load_all_metadata(files):
    # Known issue: The below code sometimes looses logs from load_metadata
    with Pool(max(1, cpu_count() - 1)) as pool:
        return pool.map(load_metadata, files)


def load_all_metadata_sync(files):
    """Debugging"""
    data = []
    for file in files:
        data.append(load_metadata(file))
    return data


def check_downloads(files: list[DriveFile]):
    failed = []
    for file in files:
        path = DOWNLOADS / file.path
        if not path.exists():
            log.warning(f"Download failed for {file.filename}.")
            failed.append(file)
    return failed


def correct_mp3(file: DriveFile):
    file_in = DOWNLOADS / file.path
    file_out = CORRECT / file.id
    if file_out.exists():
        raise FileExistsError(f"File {file_out} already exists.")

    correct_and_convert_mp3(file_in, file_out)
    log.debug(f"Corrected and converted {file.filename}.")


def correct_many(files: list[DriveFile]):
    ctx = multiprocessing.get_context("spawn")

    def handle_error(e):
        log.exception("Error occurred while correcting MP3", exc_info=e)

    with ctx.Pool(max(1, cpu_count() - 1)) as pool:
        pool.map_async(
            correct_mp3,
            [file for file in files],
            error_callback=handle_error,
        )
        pool.close()
        pool.join()

    failed = []
    for file in files:
        if not (CORRECT / file.id).exists():
            failed.append(file)

    return failed


def sync(db: Session):
    new = get_new_drive_files(db)
    if len(new) == 0:
        log.info("No new files to sync.")
        return

    log.info(f"Downloading {len(new)} new files from Drive...")
    download_files(new, str(DOWNLOADS))

    failed = check_downloads(new)
    if failed:
        raise Exception(
            f"Failed to download {len(failed)} files. Aborting sync!"
        )

    log.info("Download complete! Loading metadata.")
    metadatas = load_all_metadata(new)
    metadatas = [
        (metadata, file)
        for metadata, file in metadatas
        if metadata is not None
        and metadata.hash is not None
        and len(metadata.artists) > 0
        and len(metadata.singers) > 0
    ]

    if len(metadatas) != len(new):
        log.warning(
            f"Metadata loading failed for {len(new) - len(metadatas)} files."
        )
    if not metadatas:
        raise Exception("No metadata loaded. Aborting sync!")

    songs_to_update: list[tuple[SongAudioReference, Metadata, DriveFile]] = []
    to_create: list[tuple[Metadata, DriveFile]] = []

    for metadata, file in metadatas:
        reference = (
            db.query(SongAudioReference)
            .filter_by(
                type=AudioReferenceType.GOOGLE_DRIVE, audio_hash=metadata.hash
            )
            .first()
        )
        if reference:
            songs_to_update.append((reference, metadata, file))
        else:
            to_create.append((metadata, file))

    log.info(
        f"Found {len(songs_to_update)} songs to update and {len(to_create)} to create."
    )
    if len(songs_to_update) == 0 and len(to_create) == 0:
        log.info("No songs to update or create. Exiting sync.")
        return

    log.info("Updating songs...")
    service = create_song_service(db)
    for ref, metadata, file in songs_to_update:
        service.update_with_metadata(ref.song, metadata)
        ref.external_id = file.id

    log.info("Correcting MP3s...")
    failed = correct_many([file for _, file in to_create])

    if failed:
        raise Exception(
            f"Failed to convert {len(failed)} files. Aborting sync!"
        )

    for metadata, file in to_create:
        ref = SongAudioReference(
            external_id=file.id,
            audio_hash=metadata.hash,
            type=AudioReferenceType.GOOGLE_DRIVE,
        )
        service.create_from_metadata(metadata, [ref])

        path = CORRECT / file.id
        try:
            path.rename(AUDIO / str(ref.id))
        except Exception:
            log.error(
                f"Failed to move audio file {path} -> {AUDIO / str(ref.id)}",
                exc_info=True,
            )

    log.info("Sync completed successfully!")
    log.info(
        f"Created {len(to_create)} new songs and updated {len(songs_to_update)} existing ones."
    )
