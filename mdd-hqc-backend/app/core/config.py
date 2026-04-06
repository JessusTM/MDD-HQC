"""Application configuration loaded from environment and `.env`."""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    """Pydantic settings for MDD-HQC (env vars + defaults)."""

    LOG_LEVEL: str = "DEBUG"
    LOG_FILE_NAME: str = "mdd_hqc.jsonl"
    LOG_MAX_BYTES: int = 10_485_760
    LOG_BACKUP_COUNT: int = 5
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """Returns the configured CORS origins as a normalized list."""

        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]


config = Config()
