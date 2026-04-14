from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LinkedIn AI Content Agent"
    api_prefix: str = ""
    app_timezone: str = "America/New_York"

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-5.2", alias="OPENAI_MODEL")

    database_url: str = Field("sqlite:///data/content_agent.db", alias="DATABASE_URL")

    email_provider: str = Field("smtp", alias="EMAIL_PROVIDER")
    email_provider_api_key: str | None = Field(None, alias="EMAIL_PROVIDER_API_KEY")
    email_from: str = Field(..., alias="EMAIL_FROM")
    weekly_report_email: str = Field(..., alias="WEEKLY_REPORT_EMAIL")

    smtp_host: str | None = Field(None, alias="SMTP_HOST")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    smtp_username: str | None = Field(None, alias="SMTP_USERNAME")
    smtp_password: str | None = Field(None, alias="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(True, alias="SMTP_USE_TLS")

    linkedin_mock_mode: bool = Field(True, alias="LINKEDIN_MOCK_MODE")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
