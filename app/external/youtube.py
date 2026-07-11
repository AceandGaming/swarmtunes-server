import json
import re
from dataclasses import dataclass
from datetime import datetime

import isodate
from googleapiclient.discovery import build

from core.paths import CONFIG
from features.metadata import MetaArtist, Metadata, MetadataSource

from .google_verify import get_google_credentials


@dataclass(kw_only=True)
class ConfigValue:
    channelId: str | None = None
    playlistId: str | None = None
    channelFilter: list[str] | None = None
    artistName: str | None = None
    formatTitle: bool = True


youtube = build(
    "youtube", "v3", credentials=get_google_credentials(), cache_discovery=False
)


def load_config() -> list[ConfigValue]:
    if not (CONFIG / "youtube_config.json").exists():
        return []
    try:
        with open(CONFIG / "youtube_config.json", "r") as f:
            dict = json.load(f)
            configs = [ConfigValue(**item) for item in dict]
    except Exception as e:
        print("Failed to load YT config:", e)
        return []
    for config in configs:
        if bool(config.channelId) == bool(config.playlistId):
            print(
                "Invalid YT config: Must contain either channelId or playlistId (not both):",
                config,
            )
            return []

    return configs


def get_all_videos(config: ConfigValue) -> list[dict]:
    if config.playlistId:
        search = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=config.playlistId,
                maxResults=999999,
            )
            .execute()
        )
    elif config.channelId:
        search = (
            youtube.search()
            .list(
                part="snippet",
                channelId=config.channelId,
                maxResults=999999,
                type="video",
            )
            .execute()
        )
    else:
        raise Exception("Invalid config")

    video_ids = [
        (item["snippet"]["resourceId"]["videoId"]) for item in search["items"]
    ]

    details = (
        youtube.videos()
        .list(part="contentDetails,snippet", id=",".join(video_ids))
        .execute()
    )

    items = []

    for item in details["items"]:
        if (
            config.channelFilter
            and item["snippet"]["channelTitle"].strip()
            not in config.channelFilter
        ):
            continue

        items.append(item)

    return items


def filter_title(title: str) -> str:
    title = re.sub(r"[({[【].*?[)}\]】]\)", "", title)
    print(title)

    parts = re.split(r"( - | \| )", title)

    for i, part in enumerate(parts.copy()):
        norm = part.strip().lower()
        if not (
            norm.startswith("feat")
            or norm.startswith("covered by")
            or norm.startswith("with")
            or norm.startswith("cover by")
        ):
            continue

        try:
            parts.pop(i)
            parts.pop(i - 1)  # seprator
        except IndexError:
            pass

    return "".join(parts)


def create_metadata(item: dict, config: ConfigValue) -> tuple[str, Metadata]:
    data = item["snippet"]
    print(json.dumps(item, indent=4))

    artist = MetaArtist(name=config.artistName or data["channelTitle"].strip())

    if config.formatTitle:
        title = filter_title(data["title"])
    else:
        title = data["title"]

    return (
        item["id"],
        Metadata(
            source=MetadataSource.YOUTUBE,
            title=title,
            title_og=None,
            artists=[artist],
            singers=[artist],
            date=datetime.fromisoformat(item["snippet"]["publishedAt"]),
            disc=None,
            hash=None,
            seconds=isodate.parse_duration(
                item["contentDetails"]["duration"]
            ).total_seconds(),
        ),
    )
