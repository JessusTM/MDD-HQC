"""Application configuration loaded from environment and `.env`."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    """Pydantic settings for MDD-HQC (env vars + defaults)."""

    APP_NAME: str = "MDD-HQC"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE_NAME: str = "mdd_hqc.jsonl"
    LOG_MAX_BYTES: int = 10_485_760
    LOG_BACKUP_COUNT: int = 5


config = Config()
