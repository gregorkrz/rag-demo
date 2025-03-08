from pathlib import Path

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = structlog.get_logger(__name__)


def create_path(folder_name: str) -> Path:
    """Creates and returns a path for storing data or logs."""
    path = Path(__file__).parent.resolve().parent / f"{folder_name}"
    path.mkdir(exist_ok=True)
    return path


class Settings(BaseSettings):
    """
    Application settings model that provides configuration for all components.
    Combines both infrastructure and consensus settings.
    """

    # Flag to enable/disable attestation simulation
    simulate_attestation: bool = False

    # Gemini Settings
    gemini_api_key: str = ""

    # OpenRouter Settings
    open_router_base_url: str = "https://openrouter.ai/api/v1"
    open_router_api_key: str = ""

    # Restrict backend listener to specific IPs
    cors_origins: list[str] = ["*"]

    # Path Settings
    data_path: Path = create_path("data")
    input_path: Path = create_path("flare_ai_rag")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Create a global settings instance
settings = Settings()
logger.debug("Settings have been initialized.", settings=settings.model_dump())
