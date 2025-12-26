import os
from pydantic_settings import BaseSettings
from typing import Optional, List


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
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    
    # Render Configuration
    render_external_url: str = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
    
    # CORS Settings - Use property to handle environment variable parsing
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins from environment or use defaults"""
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            # Try to parse as JSON first, then fall back to comma-separated
            try:
                import json
                return json.loads(cors_env)
            except:
                return [origin.strip() for origin in cors_env.split(",")]
        
        # Default origins
        if self.environment == "production":
            return [
                "https://knockxprime-ai-frontend.onrender.com",
                "https://knockxprime.ai",
                "https://www.knockxprime.ai"
            ]
        else:
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ]
    
    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", 100))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", 60))
    
    class Config:
        env_file = ".env"


settings = Settings()