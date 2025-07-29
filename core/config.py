"""
Configuration module for the Telegram bot.
Loads environment variables and provides configuration settings.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration management for the Telegram bot."""
    
    # Bot settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")
    
    # Webhook settings
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBHOOK_SECRET_TOKEN: str = os.getenv("WEBHOOK_SECRET_TOKEN", "")
    WEBHOOK_HOST: str = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    WEBHOOK_PORT: int = int(os.getenv("WEBHOOK_PORT", "8000"))
    
    # Bot mode: "polling" or "webhook"
    BOT_MODE: str = os.getenv("BOT_MODE", "polling").lower()
    
    # Debug and logging
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Admin settings
    ADMIN_USER_IDS: List[int] = [
        int(uid.strip()) for uid in os.getenv("ADMIN_USER_IDS", "").split(",") 
        if uid.strip().isdigit()
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "bot.db")
    
    @classmethod
    def validate(cls, skip_bot_token=False) -> None:
        """Validate required configuration."""
        if not skip_bot_token and not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        
        if cls.BOT_MODE not in ["polling", "webhook"]:
            raise ValueError("BOT_MODE must be 'polling' or 'webhook'")
        
        if cls.BOT_MODE == "webhook":
            if not cls.WEBHOOK_URL:
                raise ValueError("WEBHOOK_URL is required for webhook mode")
            if not cls.WEBHOOK_SECRET_TOKEN:
                logger.warning("WEBHOOK_SECRET_TOKEN not set - webhook security is reduced")
    
    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in cls.ADMIN_USER_IDS