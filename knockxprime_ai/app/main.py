from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import chat, users, usage, plans, admin
from app.core.keep_alive import router as keep_alive_router
from app.middleware.rate_limiting import RateLimitMiddleware
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.cors import add_cors_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    print("🚀 Starting KnockXPrime AI Backend...")
    await init_db()
    print("✅ Database initialized")
    yield
    print("👋 Shutting down KnockXPrime AI Backend...")


app = FastAPI(
    title="KnockXPrime AI",
    description="AI-powered chat service with subscription management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add request logging
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting
app.add_middleware(RateLimitMiddleware, calls_per_minute=settings.rate_limit_requests)

# Add CORS middleware
app = add_cors_middleware(app)

# Include routers
app.include_router(keep_alive_router, prefix="/health", tags=["health"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(usage.router, prefix="/api/v1/usage", tags=["usage"])
app.include_router(plans.router, prefix="/api/v1/plans", tags=["plans"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/")
async def root():
    return {
        "message": "KnockXPrime AI API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs" if settings.environment == "development" else "Contact support for API documentation",
        "health": "/health"
    }


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "KnockXPrime AI API",
        "version": "1.0.0",
        "description": "AI-powered chat service with subscription management",
        "endpoints": {
            "health": "/health",
            "users": "/api/v1/users",
            "chat": "/api/v1/chat",
            "usage": "/api/v1/usage",
            "plans": "/api/v1/plans",
            "admin": "/api/v1/admin"
        },
        "authentication": "Bearer token required for most endpoints",
        "rate_limits": {
            "requests_per_minute": settings.rate_limit_requests,
            "window_seconds": settings.rate_limit_window
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )