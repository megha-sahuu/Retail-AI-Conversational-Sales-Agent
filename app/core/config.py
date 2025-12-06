from pydantic import BaseModel
from functools import lru_cache
import os


class Settings(BaseModel):
    app_name: str = "Retail AI Conversational Sales Agent"
    environment: str = os.getenv("ENVIRONMENT", "local")
    api_v1_prefix: str = "/api/v1"

    # LLM
    llm_provider: str = os.getenv("LLM_PROVIDER", "dummy")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Data paths
    data_dir: str = os.getenv("DATA_DIR", "data")


@lru_cache
def get_settings() -> Settings:
    return Settings()
