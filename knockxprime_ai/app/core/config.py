import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Neon Database REST API
    neon_api_url: str = os.getenv("NEON_API_URL", "https://ep-ancient-mountain-afykb78o.apirest.c-2.us-west-2.aws.neon.tech/neondb/rest/v1")
    neon_api_key: str = os.getenv("NEON_API_KEY", "")
    
    # Grok API
    grok_api_key: str = os.getenv("GROK_API_KEY", "")
    grok_base_url: str = "https://api.x.ai/v1"
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Keys
    api_key_length: int = 32
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"


settings = Settings()