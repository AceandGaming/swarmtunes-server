from pydantic_settings import BaseSettings, SettingsConfigDict

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
    max_delete_percent: float = 0.05

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
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="_")

    fastapi: FastAPI = FastAPI()
    sync: Sync = Sync()
    cache: Cache = Cache()
    backups: Backups = Backups()

