from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.paths import CONFIG


class Automated(BaseSettings):
    enabled: bool = False
    frequency_hours: int = 24

    album_min_songs: int = 4


class Backups(BaseSettings):
    enabled: bool = False
    use_compression: bool = True

    light_daily_count: int = 3
    light_weekly_count: int = 5

    full_daily_count: int = 0
    full_weekly_count: int = 3


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=CONFIG / ".env", env_nested_delimiter="__")

    automated: Automated = Automated()
    backups: Backups = Backups()

    token_expiry_hours: int = 24

    playlist_max_name_length: int = 100
    user_max_playlists: int = 30

    log_level: str = "DEBUG"


@lru_cache
def get_config() -> Settings:
    return Settings()
