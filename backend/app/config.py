from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "auto"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"  # Latest free tier model per official docs
    embedding_model: str = "auto"
    database_url: str
    cors_allow_origins: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()


