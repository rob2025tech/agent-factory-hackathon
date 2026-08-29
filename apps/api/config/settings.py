# apps/api/config/settings.py

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    ollama_url: str = "http://localhost:11434"
    # ollama_model: str = "gemma3:4b"
    ollama_model: str = "qwen3:8b"
    # ollama_model: str = "qwen3:1.7b"

    # butterbase_api_base: str
    # butterbase_api_key: str
    butterbase_api_base: str | None = None
    butterbase_api_key: str | None = None

    evermind_api_key: str | None = None
    nebius_api_key: str | None = None
    cerebras_api_key: str | None = None

    memory_provider: str = "evermind"
    llm_provider: str = "ollama"
    storage_provider: str = "local"
    analytics_provider: str = "local"
    

settings = Settings()
