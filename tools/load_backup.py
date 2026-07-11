import shutil
import sys
import tarfile
from dataclasses import asdict
from pathlib import Path

import questionary

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "app"))

import core.paths as paths  # noqa: E402
from core.backup import (  # noqa: E402
    BackupMetadata,
    create_backup,
    get_backups,
    get_hash,
)

print("Before continuing, ensure the server is NOT running!")
backups = get_backups()

if len(backups) == 0:
    print("No backups found! (good luck...)")
    exit(0)

print(f"Found {len(backups)} backups:")

answer = questionary.select(
    "Select backup to load",
    choices=[
        questionary.Choice(
            title=f"{file.name} - {metadata.name}",
            value=(file, metadata),
            description=f"Created at: {metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        )
        for file, metadata in sorted(
            backups, key=lambda x: x[1].created_at, reverse=True
        )
    ],
).ask()
if answer is None:
    exit(0)

path, metadata = answer
path: Path
metadata: BackupMetadata

print("Running integrity checks...")

if metadata.completed_at is None or metadata.completed_at < metadata.created_at:
    print("Backup incomplete!")
    exit(0)
if get_hash(path) != metadata.post_hash or metadata.sqlite_integrity_check != "ok":
    print("Backup corrupted!")
    exit(0)

print("Backup Metadata:")
for key, value in asdict(metadata).items():
    print(f"  {key}: {value}")

if not questionary.confirm("Continue?").ask():
    exit(0)

print("Creating backup of current database...")
try:
    create_backup(True, "Pre-Restore Backup")
except Exception:
    print("Failed to create backup!")
    if not questionary.confirm("Continue Anyway?", default=False).ask():
        exit(0)

print("Are you sure? This will override the curent database!")
if questionary.text("Type RESTORE to continue:").ask() != "RESTORE":
    exit(0)

DATABASE = paths.DATA / "database.db"
DATABASE_OLD = paths.DATA / "database.db.old"
PERSISTENT = paths.PERSISTENT_DATA
PERSISTENT_OLD = paths.DATA / "persistent.old"

print("Coping files from backup...")

if DATABASE.exists():
    DATABASE.rename(DATABASE_OLD)
try:
    shutil.copyfile(path / "database.db", DATABASE)
except:
    DATABASE.unlink(missing_ok=True)
    if DATABASE_OLD.exists():
        DATABASE_OLD.rename(DATABASE)
    raise

if metadata.type == "full":
    if PERSISTENT.exists():
        PERSISTENT.rename(PERSISTENT_OLD)

    try:
        with tarfile.open(path / "persistent.tar") as tar:
            tar.extractall(str(paths.DATA))
    except:
        shutil.rmtree(PERSISTENT, ignore_errors=True)
        if PERSISTENT_OLD.exists():
            PERSISTENT_OLD.rename(PERSISTENT)
        raise

print("Cleaning up...")
shutil.rmtree(PERSISTENT_OLD, ignore_errors=True)
DATABASE_OLD.unlink(missing_ok=True)

print("Done!")
