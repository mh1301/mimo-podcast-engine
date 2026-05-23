"""MiMo Podcast Production Engine - Configuration."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "MiMo Podcast Production Engine"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # MiMo LLM configuration
    mimo_api_base: str = "http://localhost:8080/v1"
    mimo_api_key: str = "sk-mimo-placeholder"
    mimo_model: str = "MiMo-7B-RL"
    mimo_max_tokens: int = 4096
    mimo_temperature: float = 0.7

    # Storage
    output_dir: str = "./output"
    episodes_db: str = "./data/episodes.json"

    # Audio processing
    audio_sample_rate: int = 44100
    audio_format: str = "wav"
    target_loudness: float = -16.0

    # Pipeline
    pipeline_timeout: int = 600

    class Config:
        env_prefix = "MIMO_PODCAST_"
        env_file = ".env"


settings = Settings()
