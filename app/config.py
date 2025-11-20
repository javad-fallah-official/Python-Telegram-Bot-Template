from typing import List
from pydantic import BaseSettings, validator

class Features(BaseSettings):
    admin_tools: bool = True
    bans: bool = True
    join_check: bool = True
    referral: bool = True

    class Config:
        env_prefix = "FEATURES_"

class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_MODE: str = "polling"
    POSTGRES_URL: str | None = None
    DEBUG: bool = True
    FEATURES: Features = Features()
    ADMIN_IDS: List[int] = []
    REQUIRED_CHANNELS: List[str] = []
    JOINCHECK_CACHE_TTL: int = 300
    JOIN_PROMPT_TEXT: str = "Please join the required channels"

    @validator("ADMIN_IDS", pre=True)
    def parse_admin_ids(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [int(x) for x in v]
        return [int(x) for x in str(v).split(",") if x]

    @validator("REQUIRED_CHANNELS", pre=True)
    def parse_required_channels(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        return [str(x).strip() for x in str(v).split(",") if x]

    class Config:
        env_file = ".env"

settings = Settings()
