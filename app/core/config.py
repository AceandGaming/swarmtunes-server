from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.paths import CONFIG


class FastAPI(BaseSettings):
    enable_v1: bool = True
    enable_v2: bool = True

    allow_hls: bool = True
    allow_ogg: bool = True


class Sync(BaseSettings):
    enabled: bool = False
    frequency_hours: int = 24

    max_update_percent: float = 0.3
    max_create_percent: float = 0.1


class Cache(BaseSettings):
    pre_generate_hls: bool = True


class Backups(BaseSettings):
    enabled: bool = False
    use_compression: bool = True

    light_daily_count: int = 3
    light_weekly_count: int = 5

    full_daily_count: int = 0
    full_weekly_count: int = 3


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=CONFIG / ".env", env_nested_delimiter="__")

    fastapi: FastAPI = FastAPI()
    sync: Sync = Sync()
    cache: Cache = Cache()
    backups: Backups = Backups()

    token_expiry_hours: int = 24

    playlist_max_name_length: int = 100
    user_max_playlists: int = 30

    log_level: str = "DEBUG"

    album_min_songs: int = 4


@lru_cache
def get_config() -> Settings:
    return Settings()
