from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./wellness_tracker.db"
    
    # JWT Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI API
    openai_api_key: Optional[str] = None
    
    # App Settings
    app_name: str = "Wellness Tracker API"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()
