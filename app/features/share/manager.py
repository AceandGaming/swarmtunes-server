from datetime import datetime, timedelta, timezone

from features.playlist import Playlist
from features.song import Song
from sqlalchemy.orm import Session

from .link import ShareLink, ShareLinkType


def orm_to_linktype(orm: Song | Playlist) -> ShareLinkType:
    if isinstance(orm, Song):
        return ShareLinkType.SONG
    elif isinstance(orm, Playlist):
        return ShareLinkType.PLAYLIST


class ShareManager:
    def __init__(self, db: Session):
        self._db = db

    def query(self):
        return self._db.query(ShareLink).filter(
            ShareLink.expires_at.is_(None) | ShareLink.expires_at
            > datetime.now(timezone.utc)
        )

    def add(self, link: ShareLink):
        self._db.add(link)
        self._db.flush()

    def get(self, link: str):
        return self.query().filter(ShareLink.link == link).first()

    def share(self, obj: Song | Playlist, expires_in: timedelta | None = None):
        link = ShareLink(
            type=orm_to_linktype(obj),
            external_id=obj.id,
            expires_at=(datetime.now(timezone.utc) + expires_in)
            if expires_in
            else None,
        )

        self.add(link)
        return link
