"""Tool to add songs from YT"""

import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import questionary

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "app"))

from database.database import create as create_db  # noqa: E402
from database.dependencies import db_session  # noqa: E402
from external.youtube import create_metadata, get_video  # noqa: E402
from features.metadata import MetaArtist, Metadata, MetadataSource  # noqa: E402
from features.song import (  # noqa: E402
    AudioReferenceType,
    SongAudioReference,
    create_song_service,
)

create_db()

while True:
    yt_url = questionary.text("Enter the video url:").ask()
    if yt_url is None:
        exit(0)

    url = urlsplit(yt_url)
    if url.scheme != "https":
        print("Invalid URL")
        continue

    try:
        if url.hostname == "www.youtube.com":
            yt_id = parse_qs(url.query)["v"][0]
        elif url.domain == "youtu.be.com":
            yt_id = url.path.split("/")[1]
        else:
            print("Invalid URL")
            continue
    except Exception:
        print("Invalid URL")
        continue

    break

video = get_video(yt_id)
_, metadata = create_metadata(video, yt_id)

print("Metadata:")
for key, value in asdict(metadata).items():
    print(f"  {key}: {value}")

if questionary.confirm("Would you like to edit the above data?", default=False).ask():
    metadata.title = questionary.text("Title (English):", default=metadata.title).ask()
    metadata.title_og = (
        questionary.text("Original title:", default=metadata.title_og or "").ask()
        or None
    )
    metadata.date = datetime.fromisoformat(
        questionary.text(
            "Date (ISO):",
            default=metadata.date.isoformat(),
        ).ask()
    )

    new_artists = []
    i = 0
    while True:
        artist = metadata.artists[i] if i < len(metadata.artists) else None

        name = questionary.text(
            f"Artist Name {i + 1} (English):",
            default=artist.name if artist else "",
        ).ask()
        if name is None:
            exit(0)
        og_name = questionary.text(
            f"Original Artist Name {i + 1}:",
        ).ask()
        if og_name is None:
            exit(0)

        new_artists.append(MetaArtist(name=name, name_og=og_name))
        i += 1

        if i >= len(metadata.artists):
            if not questionary.confirm("Add another artist?", default=False).ask():
                break

    new_singers = []
    i = 0
    while True:
        singer = metadata.singers[i] if i < len(metadata.singers) else None

        name = questionary.text(
            f"Singer Name {i + 1} (English):",
            default=singer.name if singer else "",
        ).ask()
        if name is None:
            exit(0)
        og_name = questionary.text(
            f"Original Singer Name {i + 1}:",
        ).ask()
        if og_name is None:
            exit(0)

        new_singers.append(MetaArtist(name=name, name_og=og_name))
        i += 1

        if i >= len(metadata.singers):
            if not questionary.confirm("Add another singer?", default=False).ask():
                break

    metadata.artists = new_artists
    metadata.singers = new_singers

with db_session() as db:
    song_service = create_song_service(db)

    ref = SongAudioReference(
        type=AudioReferenceType.YOUTUBE,
        external_id=yt_id,
    )

    song_service.create_from_metadata(metadata, [ref])

print("Done!")
