from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    gemini_api_key: str = ""
    google_maps_api_key: str = ""
    stadium_api_key: str = ""
    iot_auth_token: str = ""

    # Allows loading from .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
