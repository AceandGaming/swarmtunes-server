import logging
import multiprocessing
from multiprocessing import Pool, cpu_count

from sqlalchemy.orm import Session

from core.paths import AUDIO, CORRECT, DOWNLOADS
from external.rclone_api import DriveFile, download_files, get_all_files
from features.song import AudioReferenceType, SongAudioReference, create_song_service

from .downloader.correct import correct_and_convert_mp3
from .downloader.metadata import load_file_metadata

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


def check_downloads(files):
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


def sync(db: Session):
    new = get_new_drive_files(db)
    if len(new) == 0:
        log.info("No new files to sync.")
        return

    log.info(f"Downloading {len(new)} new files from Drive.")
    download_files(new, str(DOWNLOADS))

    failed = check_downloads(new)
    if failed:
        raise Exception(f"Failed to download {len(failed)} files. Aborting sync!")

    log.info("Download complete! Loading metadata...")
    metadatas = load_all_metadata(new)
    metadatas = [
        (metadata, file)
        for metadata, file in metadatas
        if metadata is not None and metadata.hash is not None
    ]

    if len(metadatas) != len(new):
        log.warning(f"Metadata loading failed for {len(new) - len(metadatas)} files.")
    if not metadatas:
        raise Exception("No metadata loaded. Aborting sync!")

    songs_to_update = []
    to_create = []

    for metadata, file in metadatas:
        reference = db.query(SongAudioReference).filter_by(audio_hash=metadata.hash).first()
        if reference:
            songs_to_update.append((reference.song, metadata))
        else:
            to_create.append((metadata, file))

    log.info(f"Found {len(songs_to_update)} songs to update and {len(to_create)} to create.")
    if len(songs_to_update) == 0 and len(to_create) == 0:
        log.info("No songs to update or create. Exiting sync.")
        return

    log.info("Updating songs...")
    service = create_song_service(db)
    for song, metadata in songs_to_update:
        service.update_with_metadata(song, metadata)

    log.info("Correcting MP3s...")
    ctx = multiprocessing.get_context("spawn")

    def handle_error(e):
        log.exception("Error occurred while correcting MP3", exc_info=e)

    with ctx.Pool(max(1, cpu_count() - 1)) as pool:
        pool.map_async(correct_mp3, [file for _, file in to_create], error_callback=handle_error)
        pool.close()
        pool.join()

    failed = []
    for metadata, file in to_create:
        if not (CORRECT / file.id).exists():
            failed.append((metadata, file))

    if failed:
        raise Exception(f"Failed to convert {len(failed)} files. Aborting sync.")

    for metadata, file in to_create:
        ref = SongAudioReference(
            external_id=file.id,
            audio_hash=metadata.hash,
            type=AudioReferenceType.GOOGLE_DRIVE,
        )
        song = service.create_from_metadata(metadata, [ref])
        path = CORRECT / file.id
        path.rename(AUDIO / str(song.id))

    log.info("Sync completed successfully!")
    log.info(
        f"Created {len(to_create)} new songs and updated {len(songs_to_update)} existing ones."
    )
