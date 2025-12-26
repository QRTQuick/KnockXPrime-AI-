from fastapi import APIRouter
from datetime import datetime
import asyncio
import httpx
from app.core.neon_utils import test_neon_connection

router = APIRouter()

# Keep-alive task
keep_alive_task = None


async def keep_alive_ping():
    """Keep the service alive by pinging itself every 3 seconds"""
    while True:
        try:
            await asyncio.sleep(3)  # Wait 3 seconds
            async with httpx.AsyncClient() as client:
                # Ping the health endpoint
                await client.get("http://localhost:8000/health/ping", timeout=2.0)
        except Exception:
            # Ignore errors, just keep trying
            pass


@router.get("/")
async def health_check():
    """Health check endpoint for keeping Render service alive"""
    global keep_alive_task
    
    # Start keep-alive task if not running
    if keep_alive_task is None or keep_alive_task.done():
        keep_alive_task = asyncio.create_task(keep_alive_ping())
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "KnockXPrime AI",
        "keep_alive": "active"
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/database")
async def database_health():
    """Check Neon database connection"""
    connection_result = await test_neon_connection()
    return {
        "database": connection_result,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/keep-alive")
async def manual_keep_alive():
    """Manual keep-alive trigger for external services"""
    global keep_alive_task
    
    # Restart keep-alive task
    if keep_alive_task and not keep_alive_task.done():
        keep_alive_task.cancel()
    
    keep_alive_task = asyncio.create_task(keep_alive_ping())
    
    return {
        "message": "Keep-alive restarted",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }