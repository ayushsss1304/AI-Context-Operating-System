from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Context Operating System"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ai_context_os"
    default_llm_provider: str = "groq"
    default_llm_model: str = "qwen-or-mistral-model-name"
    embedding_model: str = "embedding-model-name"
    auto_create_tables: bool = True
    auto_run_migrations: bool = True
    groq_api_key: str | None = None
    openrouter_api_key: str | None = None
    together_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
