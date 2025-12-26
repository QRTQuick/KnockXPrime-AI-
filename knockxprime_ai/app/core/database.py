import httpx
import json
from typing import Optional, Dict, List, Any
import uuid
from datetime import datetime
from app.core.config import settings
from app.core.neon_utils import execute_with_retry, NeonAPIError


class NeonRestDatabase:
    def __init__(self):
        self.base_url = settings.neon_api_url
        self.headers = {
            "Authorization": f"Bearer {settings.neon_api_key}",
            "Content-Type": "application/json"
        }
    
    async def execute_query(self, query: str, params: List = None) -> Dict[str, Any]:
        """Execute a query using Neon REST API with retry logic"""
        try:
            return await execute_with_retry(query, params)
        except NeonAPIError as e:
            print(f"Database error: {e.message}")
            raise Exception(f"Database operation failed: {e.message}")
    
    async def execute(self, query: str, *args):
        """Execute a query (for compatibility)"""
        result = await self.execute_query(query, list(args))
        return result.get("rowCount", 0)
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        result = await self.execute_query(query, list(args))
        rows = result.get("rows", [])
        columns = result.get("fields", [])
        
        # Convert to dict format
        return [
            {col["name"]: row[i] for i, col in enumerate(columns)}
            for row in rows
        ]
    
    async def fetchrow(self, query: str, *args):
        """Fetch single row"""
        rows = await self.fetch(query, *args)
        return rows[0] if rows else None
    
    async def fetchval(self, query: str, *args):
        """Fetch single value"""
        result = await self.execute_query(query, list(args))
        rows = result.get("rows", [])
        return rows[0][0] if rows and rows[0] else None


# Global database instance
db = NeonRestDatabase()


async def init_db():
    """Initialize database and create tables"""
    # Create tables
    await create_tables()


async def create_tables():
    """Create all necessary tables"""
    
    # Plans table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL UNIQUE,
            price NUMERIC(10,2) NOT NULL,
            max_tokens INTEGER NOT NULL,
            max_requests INTEGER NOT NULL DEFAULT 100,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Users table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            hashed_pass TEXT NOT NULL,
            api_key TEXT NOT NULL UNIQUE,
            plan_id UUID REFERENCES plans(id),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Usage table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            tokens_used INTEGER DEFAULT 0,
            requests INTEGER DEFAULT 0,
            month DATE NOT NULL,
            day DATE NOT NULL DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(user_id, month),
            UNIQUE(user_id, day)
        )
    """)
    
    # Sessions table (optional)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            session_data JSONB,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    
    # Insert default plans if they don't exist
    await insert_default_plans()


async def insert_default_plans():
    """Insert default subscription plans"""
    plans = [
        ("Baby Free", 0.00, 1000, 10),
        ("Leveler", 4.00, 5000, 100),
        ("Log Min", 10.00, 20000, 500),
        ("High Max", 100.00, 100000, 2000)
    ]
    
    for name, price, max_tokens, max_requests in plans:
        existing = await db.fetchrow(
            "SELECT id FROM plans WHERE name = $1", name
        )
        if not existing:
            await db.execute(
                "INSERT INTO plans (name, price, max_tokens, max_requests) VALUES ($1, $2, $3, $4)",
                name, price, max_tokens, max_requests
            )