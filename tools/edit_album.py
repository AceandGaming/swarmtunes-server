from uuid import UUID

import questionary

from st.database.database import create as create_db
from st.database.dependencies import db_session
from st.features.album import Album, create_album_service

create_db()

with db_session() as db:
    service = create_album_service(db)

    while True:
        id = questionary.text("Enter the album id:").ask()
        if id is None:
            exit(0)

        album = service.get(UUID(id))
        if album is not None:
            break

    album.title = questionary.text(
        "Title (English):", default=album.title
    ).ask()
