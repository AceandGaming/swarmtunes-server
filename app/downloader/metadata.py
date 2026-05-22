import json
from mutagen.id3 import ID3
from typing import Optional
import re
from datetime import datetime
from dataclasses import dataclass
from typing import Literal
from pathlib import Path
import logging
log = logging.getLogger("Downloader")

@dataclass
class Metadata:
    source: Literal["json", "id3"]
    title: str
    title_og: Optional[str]
    artists: list[str]
    singers: list[str]
    date: datetime
    disc: int
    hash: Optional[str] #audio hash


def convert_name(name: str) -> str:
    name = re.sub(r"\(.*\)", "", name).strip()
    return {
        "neuro": "Neuro-sama",
        "evil": "Evil Neuro",
    }.get(name.lower(), name)

def convert_to_singers(cover_artist: str) -> list[str]:
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
    

def create_from_id3(file: ID3):
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
        source="id3",
        title=title,
        title_og=title_og,
        artists=artists,
        singers=singers,
        date=date,
        disc=int(file["TPOS"].text[0]),
        hash=None
    )
    log.debug(f"Created Metadata from ID3: {data}")
    return data

def create_from_json(file: dict):
    artists = file["Artist"].split(",")
    artists = [convert_name(a.strip()) for a in artists]
    singers = convert_to_singers(file["CoverArtist"])

    data = Metadata(
        source="json",
        title=file["Title"],
        title_og=file["TitleOG"],
        artists=artists,
        singers=singers,
        date=datetime.fromisoformat(file["Date"]),
        disc=file["Discnumber"],
        hash=file["xxHash"],
    )
    log.debug(f"Created Metadata from JSON: {data}")
    return data

def load_file_metadata(path: Path) -> Metadata | None:
    file = ID3(path)
    if  "COMM::ved" in file:
        try:
            return create_from_json(json.loads(file["COMM::ved"].text[0]))
        except Exception as e:
            log.error(f"Error parsing json metadata: {e}")
            pass
    try:
        return create_from_id3(file)
    except Exception as e:
        log.error(f"Error parsing id3 metadata: {e}")
        return None
    