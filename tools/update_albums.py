import questionary

from st.automated.albums import update_albums
from st.database.database import create as create_db
from st.database.dependencies import db_session
from st.features.album.album import Album

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
