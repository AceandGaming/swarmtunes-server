import logging

from sqlalchemy.orm import Session

from core.paths import AUDIO, CORRECT
from external.rclone_api import DriveFile, download_files, get_all_files
from features.song import AudioReferenceType, SongAudioReference

from .sync import check_downloads, correct_many

log = logging.getLogger("automated")


def get_without_audio(db: Session):
    refs = (
        db.query(SongAudioReference)
        .filter(SongAudioReference.type == AudioReferenceType.GOOGLE_DRIVE)
        .all()
    )

    missing = []
    for ref in refs:
        path = AUDIO / str(ref.id)
        if not path.exists():
            missing.append(ref)

    return missing


def download_missing(db: Session):
    log.info("Checking for missing audio files.")

    refrences_without_audio = get_without_audio(db)

    log.info(f"Found {len(refrences_without_audio)} missing audio files.")
    if len(refrences_without_audio) == 0:
        log.info("No missing audio files to download.")
        return

    drive_files = {file.id: file for file in get_all_files()}
    files_to_download: list[DriveFile] = []

    linked: list[tuple[SongAudioReference, DriveFile]] = []

    for ref in refrences_without_audio:
        drive_file = drive_files.get(ref.external_id)
        if drive_file is not None:
            files_to_download.append(drive_file)
            linked.append((ref, drive_file))

    if len(files_to_download) != len(refrences_without_audio):
        log.warning(
            f"Failed to find {len(refrences_without_audio) - len(files_to_download)} audio files."
        )

    log.info(f"Downloading {len(files_to_download)} audio files.")
    download_files(files_to_download, str(AUDIO))

    failed = check_downloads(files_to_download)
    if failed:
        raise Exception(
            f"Failed to download {len(failed)} audio files. Aborting sync!"
        )

    log.info("Download complete! Correcting.")
    failed = correct_many(files_to_download)
    if failed:
        raise Exception(
            f"Failed to correct {len(failed)} audio files. Aborting sync!"
        )

    for file, ref in linked:
        path = CORRECT / str(file.id)
        try:
            path.rename(AUDIO / str(ref.id))
        except Exception:
            log.error(
                f"Failed to move audio file {path} -> {AUDIO / str(ref.id)}",
                exc_info=True,
            )

    log.info(f"Successfully {len(linked)} corrected missing audio files!")
