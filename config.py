import os
from typing import List, Set
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Enterprise Configuration Management for Waguri Bot"""
    
    # Telegram API Credentials
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    if not API_ID or not API_HASH or not BOT_TOKEN:
        raise ValueError("CRITICAL: API_ID, API_HASH, and BOT_TOKEN must be set in the environment or .env file.")

    # Privileged Users
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    SUDO_USERS: Set[int] = set(int(x) for x in os.getenv("SUDO_USERS", "").split() if x)
    SUDO_USERS.add(OWNER_ID)
    
    # Database
    DATABASE_PATH: str = "data/database.db"
    
    # Customization & Theme
    BOT_NAME: str = "Waguri"
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "WaguriBot")
    THEME_COLOR: str = os.getenv("THEME_COLOR", "#FFB6C1") # Light Pink / Sakura theme
    LOG_CHANNEL: int = int(os.getenv("LOG_CHANNEL", "0")) # Optional central logging channel
    
    # Limits & Thresholds
    MAX_WARNS: int = int(os.getenv("MAX_WARNS", "3"))
    ANTI_SPAM_THRESHOLD: int = int(os.getenv("ANTI_SPAM_THRESHOLD", "5"))
    MESSAGE_CACHE_SIZE: int = 10000
    
    # Third-Party APIs (Optional but required for some modules)
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    OCR_API_KEY: str = os.getenv("OCR_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Features Toggle
    ENABLE_AI: bool = os.getenv("ENABLE_AI", "True").lower() == "true"
    ENABLE_ECONOMY: bool = os.getenv("ENABLE_ECONOMY", "True").lower() == "true"
    ENABLE_ANIME: bool = os.getenv("ENABLE_ANIME", "True").lower() == "true"

    @classmethod
    def is_sudo(cls, user_id: int) -> bool:
        return user_id in cls.SUDO_USERS
