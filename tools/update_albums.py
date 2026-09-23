import sys
from pathlib import Path

import questionary

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "app"))

from automated.albums import update_albums  # noqa: E402
from database.database import create as create_db  # noqa: E402
from database.dependencies import db_session  # noqa: E402
from features.album.album import Album  # noqa: E402

create_db()

with db_session() as db:
    if questionary.confirm(
        "Would you like to delete all existing albums?",
        default=False,
        auto_enter=False,
    ).ask():
        db.query(Album).delete()
        db.flush()

    update_albums(db)
