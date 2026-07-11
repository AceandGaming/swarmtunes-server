import json
import logging
import shutil
import sqlite3
import stat
import tarfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

import core.paths as paths
from core.config import get_config

log = logging.getLogger("backups")


@dataclass(kw_only=True)
class BackupMetadata:
    id: UUID
    name: str = "Automatic Backup"

    created_at: datetime
    completed_at: datetime

    type: str
    compressed: bool = False

    sqlite_integrity_check: str
    post_hash: str


def get_backup_folder(full: bool) -> Path:
    i = 0
    while True:
        name = datetime.now(timezone.utc).strftime(
            f"%y-%m-%d {'full' if full else 'lite'}.{i}"
        )
        path = paths.BACKUPS / name

        if not path.exists():
            return path

        i += 1


def copy_sqlite(backup_dir: Path):
    log.info("Copying sqlite database to backup...")
    source = sqlite3.connect(paths.DATA / "database.db")
    target = sqlite3.connect(backup_dir / "database.db")

    with target:
        source.backup(target)

        cursor = target.cursor()
        cursor.execute("PRAGMA integrity_check;")

        result = cursor.fetchone()[0]

    source.close()
    target.close()

    return result


def copy_persistent(backup_dir: Path):
    log.info("Copying persistent data to backup...")
    with tarfile.open(backup_dir / "persistent.tar", "w") as tar:
        tar.add(paths.PERSISTENT_DATA, arcname="persistent")


def get_hash(backup_dir: Path):
    hasher = sha256()
    for file in [backup_dir / "database.db", backup_dir / "persistent.tar"]:
        if not file.exists():
            continue
        with open(file, "rb") as f:
            hasher.update(f.read())

    return hasher.hexdigest()


def create_backup(is_full, name: str | None = None):
    start_time = datetime.now(timezone.utc)

    backup_dir = get_backup_folder(is_full)
    backup_dir.mkdir()

    log.info(f"Creating new backup. Name: {backup_dir.name}")

    check = copy_sqlite(backup_dir)
    if is_full:
        copy_persistent(backup_dir)

    completed = datetime.now(timezone.utc)
    hash = get_hash(backup_dir)

    metadata = BackupMetadata(
        id=uuid4(),
        name=name or "Automatic Backup",
        created_at=start_time,
        completed_at=completed,
        type="full" if is_full else "lite",
        compressed=False,
        sqlite_integrity_check=check,
        post_hash=hash,
    )

    log.debug(f"Backup Metadata: {metadata}")

    with open(backup_dir / "metadata.json", "w") as f:
        data = json.dumps(asdict(metadata), default=str)
        f.write(data)

    # Make files read-only
    for file in backup_dir.iterdir():
        if file.is_dir():
            continue
        mode = file.stat().st_mode
        file.chmod(mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)

    log.info("Backup complete!")


def get_backups() -> list[tuple[Path, BackupMetadata]]:
    backups = []
    for file in paths.BACKUPS.iterdir():
        if not file.is_dir():
            continue

        with open(file / "metadata.json", "r") as f:
            data = json.load(f)
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["completed_at"] = datetime.fromisoformat(data["completed_at"])
            backups.append((file, BackupMetadata(**data)))

    return backups


def get_size_of_backups():
    return sum(
        f.stat().st_size for f in paths.BACKUPS.glob("**/*") if f.is_file()
    )


def trim_backups():
    log.info("Trimming backups...")
    config = get_config().backups

    backups = get_backups()

    while get_size_of_backups() > config.max_backup_size_gb * 1024 * 1024:
        oldest = min(backups, key=lambda x: x[1].created_at)
        log.debug(f"Deleting backup {oldest}")
        shutil.rmtree(oldest[0])
