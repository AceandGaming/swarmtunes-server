import logging

from sqlalchemy.orm import Session

from st.automated.cleanup import sync_cleanup
from st.automated.sync import correct_many
from st.core.backup import create_backup
from st.core.log import setup_logging
from st.core.paths import AUDIO, CORRECT, DOWNLOADS
from st.database.database import create as create_db
from st.database.dependencies import db_session
from st.external.rclone_api import DriveFile, download_files, get_all_files
from st.features.song import AudioReferenceType, SongAudioReference

log = logging.getLogger(__name__)


def download(db: Session):
    drive_files = get_all_files()

    refs = (
        db.query(SongAudioReference)
        .filter(SongAudioReference.type == AudioReferenceType.GOOGLE_DRIVE)
        .all()
    )

    to_download: list[tuple[SongAudioReference, DriveFile]] = []
    for ref in refs:
        drive_file = next(
            (f for f in drive_files if f.id == ref.external_id), None
        )
        if not drive_file:
            print(f"File {ref.external_id} not found on Drive, skipping")
            continue

        to_download.append((ref, drive_file))

    log.info(f"Downloading {len(to_download)} files from Drive...")
    download_files([file for _, file in to_download], str(DOWNLOADS))

    log.info(f"Correcting {len(to_download)} files...")
    failed, _ = correct_many(list({file for _, file in to_download}))

    if len(failed) > 0:
        log.error(f"Failed to correct {len(failed)} files!")
        exit(1)

    log.info(f"Replacing {len(to_download)} files...")
    for ref, file in to_download:
        path = CORRECT / file.id
        try:
            path.replace(AUDIO / str(ref.id))
        except Exception:
            log.error(
                f"Failed to replace audio file {path} -> {AUDIO / str(ref.id)}",
                exc_info=True,
            )


def main():
    print("Before continuing, ensure the server is NOT running!")
    input("Press enter to continue...")

    setup_logging()
    create_db()

    print("Creating backup of current database...")
    try:
        create_backup(True, "Pre-Redownload Backup")
    except Exception:
        print("Failed to create backup!")
        exit(0)

    try:
        with db_session() as db:
            download(db)
    finally:
        sync_cleanup()


if __name__ == "__main__":
    main()
