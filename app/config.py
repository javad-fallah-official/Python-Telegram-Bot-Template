from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Features(BaseSettings):
    admin_tools: bool = True
    bans: bool = True
    join_check: bool = True
    referral: bool = True
    general: bool = True

    model_config = SettingsConfigDict(env_prefix="FEATURES_")

class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_MODE: str = "polling"
    POSTGRES_URL: str | None = None
    DEBUG: bool = True
    SPONSOR_ENFORCE: bool = True
    FEATURES: Features = Features()
    ADMIN_IDS: List[int] = []
    REQUIRED_CHANNELS: List[str] = []
    JOINCHECK_CACHE_TTL: int = 300
    JOIN_PROMPT_TEXT: str = "Please join the required channels"
    DB_TYPE: str = "sqlite"
    SQLITE_PATH: str = "./data/bot.db"
    MSSQL_DSN: Optional[str] = None
    MSSQL_USE_AIOODBC: bool = True
    MSSQL_POOL_MIN: int = 1
    MSSQL_POOL_MAX: int = 10
    MSSQL_QUERY_TIMEOUT: int = 30
    MSSQL_DRIVER: Optional[str] = None
    MSSQL_HOST: Optional[str] = None
    MSSQL_PORT: Optional[int] = None
    MSSQL_DB: Optional[str] = None
    MSSQL_USER: Optional[str] = None
    MSSQL_PASS: Optional[str] = None

    @field_validator("ADMIN_IDS", mode="before")
    def parse_admin_ids(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [int(x) for x in v]
        return [int(x) for x in str(v).split(",") if x]

    @field_validator("REQUIRED_CHANNELS", mode="before")
    def parse_required_channels(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        return [str(x).strip() for x in str(v).split(",") if x]

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()
