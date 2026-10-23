from datetime import datetime
from uuid import UUID

import questionary

from st.database.database import create as create_db  # noqa: E402
from st.database.dependencies import db_session  # noqa: E402
from st.features.artist import create_or_get  # noqa: E402
from st.features.song import (  # noqa: E402
    create_song_service,
)

create_db()

with db_session() as db:
    service = create_song_service(db)

    while True:
        id = questionary.text("Enter the song id:").ask()
        if id is None:
            exit(0)

        song = service.get(UUID(id))
        if song is not None:
            break

    song.title = questionary.text("Title (English):", default=song.title).ask()
    song.title_original = (
        questionary.text(
            "Original title:", default=song.title_original or ""
        ).ask()
        or None
    )
    song.date_released = datetime.fromisoformat(
        questionary.text(
            "Date (ISO):",
            default=song.date_released.isoformat(),
        ).ask()
    )

    new_artists = []
    i = 0
    while True:
        artist = song.artists[i] if i < len(song.artists) else None

        name = questionary.text(
            f"Artist Name {i + 1} (English):",
            default=artist.name if artist else "",
        ).ask()
        if name is None:
            exit(0)
        if not name:
            break
        og_name = questionary.text(
            f"Original Artist Name {i + 1}:",
        ).ask()
        if og_name is None:
            exit(0)

        new_artists.append(create_or_get(db, name, og_name))
        i += 1

        if i >= len(song.artists):
            if not questionary.confirm(
                "Add another artist?", default=False
            ).ask():
                break

    new_singers = []
    i = 0
    while True:
        singer = song.singers[i] if i < len(song.singers) else None

        name = questionary.text(
            f"Singer Name {i + 1} (English):",
            default=singer.name if singer else "",
        ).ask()
        if name is None:
            exit(0)
        if not name:
            break
        og_name = questionary.text(
            f"Original Singer Name {i + 1}:",
        ).ask()
        if og_name is None:
            exit(0)

        new_singers.append(create_or_get(db, name, og_name))
        i += 1

        if i >= len(song.singers):
            if not questionary.confirm(
                "Add another singer?", default=False
            ).ask():
                break

    song.artists = new_artists
    song.singers = new_singers
