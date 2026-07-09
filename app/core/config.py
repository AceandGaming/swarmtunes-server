from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.paths import CONFIG


class Automated(BaseSettings):
    enabled: bool
    sync_frequency_hours: int
    delete_old_frequency_hours: int
    delete_orphaned_frequency_hours: int

    album_min_songs: int

    max_delete_percent: float
    max_deleted_days: int
    max_token_expiry_days: int


class Backups(BaseSettings):
    enabled: bool
    use_compression: bool

    light_daily_count: int
    light_weekly_count: int

    full_daily_count: int
    full_weekly_count: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=CONFIG / ".env", env_nested_delimiter="__"
    )

    automated: Automated = Field(default_factory=Automated)  # type: ignore
    backups: Backups = Field(default_factory=Backups)  # type: ignore

    token_expiry_hours: int

    playlist_max_name_length: int
    user_max_playlists: int

    log_level: str


@lru_cache
def get_config() -> Settings:
    return Settings()  # type: ignore
