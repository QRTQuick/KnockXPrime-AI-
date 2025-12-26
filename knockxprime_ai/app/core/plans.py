from typing import List, Dict, Optional
from app.core.database import db


async def get_all_plans() -> List[Dict]:
    """Get all available subscription plans"""
    plans = await db.fetch("""
        SELECT id, name, price, max_tokens, created_at
        FROM plans
        ORDER BY price ASC
    """)
    return [dict(plan) for plan in plans]


async def get_plan_by_id(plan_id: str) -> Optional[Dict]:
    """Get plan by ID"""
    plan = await db.fetchrow("""
        SELECT id, name, price, max_tokens, created_at
        FROM plans
        WHERE id = $1
    """, plan_id)
    
    return dict(plan) if plan else None


async def get_plan_by_name(name: str) -> Optional[Dict]:
    """Get plan by name"""
    plan = await db.fetchrow("""
        SELECT id, name, price, max_tokens, created_at
        FROM plans
        WHERE name = $1
    """, name)
    
    return dict(plan) if plan else None


async def get_default_plan() -> Dict:
    """Get the default plan (Leveler)"""
    plan = await get_plan_by_name("Leveler")
    if not plan:
        raise Exception("Default plan 'Leveler' not found")
    return plan


class PlanLimits:
    """Plan limits and validation"""
    
    @staticmethod
    def validate_token_usage(max_tokens: int, tokens_used: int, requested_tokens: int) -> bool:
        """Check if user can make request with requested tokens"""
        return (tokens_used + requested_tokens) <= max_tokens
    
    @staticmethod
    def get_remaining_tokens(max_tokens: int, tokens_used: int) -> int:
        """Get remaining tokens for user"""
        return max(0, max_tokens - tokens_used)