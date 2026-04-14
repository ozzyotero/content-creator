from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LinkedIn AI Content Agent"
    app_timezone: str = "America/New_York"

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-5.2", alias="OPENAI_MODEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
