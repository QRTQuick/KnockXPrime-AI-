"""
CORS middleware configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings


def add_cors_middleware(app: FastAPI) -> FastAPI:
    """Add CORS middleware with proper configuration"""
    
    # Production CORS settings
    if settings.environment == "production":
        allowed_origins = [
            "https://knockxprime-ai-frontend.onrender.com",
            "https://knockxprime.ai",
            "https://www.knockxprime.ai"
        ]
    else:
        # Development CORS settings
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID",
            "Cache-Control"
        ],
        expose_headers=[
            "X-Request-ID",
            "X-Process-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ],
        max_age=600  # 10 minutes
    )
    
    return app