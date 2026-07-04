import json
import logging
import re
from datetime import datetime
from pathlib import Path

from mutagen.mp3 import MP3

from features.metadata import MetaArtist, Metadata, MetadataSource

log = logging.getLogger()


def change_name(name: str):
    name = name.strip()
    if name.lower() == "neuro":
        name = "Neuro-sama"
    elif name.lower() == "evil":
        name = "Evil Neuro"
    return name


def convert_name(name: str) -> MetaArtist:
    match = re.match(r"(.*) \((.*?)\)", name)
    if match is not None:
        name = match.group(2)
        og_name = match.group(1)
    else:
        name = name
        og_name = None

    name = change_name(name)

    return MetaArtist(name=name, name_og=og_name)


def convert_to_singers(cover_artist: str) -> list[MetaArtist]:
    cover_artist = cover_artist.strip()

    match = re.match(r"duet \((.*)\)", cover_artist, re.IGNORECASE)
    if match is not None:
        cover_artist = match.group(1)

    if "&" in cover_artist:
        singers = []
        for split in cover_artist.split("&"):
            singers.append(convert_name(split.strip()))
        return singers

    return [convert_name(cover_artist)]


def create_from_id3(file):
    if not {"TIT2", "TPE1", "COMM::eng"} <= set(file.keys()):
        raise ValueError("Invalid metadata")

    mat = re.match(r"(.*) \((.*?)\)", file["TIT2"].text[0])
    title = None
    title_og = None
    if mat is None:
        title = file["TIT2"].text[0]
    else:
        title = mat.group(2)
        title_og = mat.group(1)

    mat = re.match(r"(.*) - (.*)", file["TPE1"].text[0])
    if mat is None:
        raise ValueError("Invalid artist format: " + file["TPE1"].text[0])

    singers = convert_to_singers(mat.group(1))
    artists = mat.group(2).split(",")
    artists = [convert_name(a.strip()) for a in artists]

    date = datetime.fromisoformat(file["COMM::eng"].text[0])

    data = Metadata(
        source=MetadataSource.ID3,
        title=title,
        title_og=title_og,
        artists=artists,
        singers=singers,
        date=date,
        disc=int(file["TPOS"].text[0]),
        hash=None,
        seconds=file.info.length,
    )
    log.debug(f"Created Metadata from ID3: {data}")
    return data


def create_from_json(file: dict):
    artists = file["Artist"].split(",")
    artists_og = (
        file["ArtistOG"].split(",") if (file.get("ArtistOG", "none").lower() != "none") else []
    )
    artists = [
        MetaArtist(name=change_name(a), name_og=change_name(aog))
        for a, aog in zip(artists, artists_og)
    ]
    singers = convert_to_singers(file["CoverArtist"])

    data = Metadata(
        source=MetadataSource.JSON,
        title=file["Title"],
        title_og=file["TitleOG"] if file.get("TitleOG", "none").lower() != "none" else None,
        artists=artists,
        singers=singers,
        date=datetime.fromisoformat(file["Date"]),
        disc=file["Discnumber"],
        hash=file["xxHash"],
        seconds=0,
    )
    log.debug(f"Created Metadata from JSON: {data}")
    return data


def load_file_metadata(path: Path) -> Metadata | None:
    file = MP3(path)
    if "COMM::ved" in file:
        try:
            meta = create_from_json(json.loads(file["COMM::ved"].text[0]))
            meta.seconds = file.info.length
            return meta
        except Exception as e:
            log.exception("Error parsing json metadata", exc_info=e)
    try:
        log.debug(f"No JSON metadata found for {path}. Reverting to ID3")
        return create_from_id3(file)
    except Exception as e:
        log.exception("Error parsing id3 metadata", exc_info=e)
        return None
