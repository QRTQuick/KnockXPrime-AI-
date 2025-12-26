from fastapi import APIRouter
from datetime import datetime
from app.core.neon_utils import test_neon_connection

router = APIRouter()


@router.get("/")
async def health_check():
    """Health check endpoint for keeping Render service alive"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "KnockXPrime AI"
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/database")
async def database_health():
    """Check Neon database connection"""
    connection_result = await test_neon_connection()
    return {
        "database": connection_result,
        "timestamp": datetime.utcnow().isoformat()
    }