"""
Daily usage tracking and limits for request-based plans
"""
from datetime import date, datetime
from typing import Dict, Optional
import uuid
from app.core.database import db


class DailyUsageService:
    
    @staticmethod
    async def get_daily_usage(user_id: str) -> Optional[Dict]:
        """Get current day usage for user"""
        current_day = date.today()
        
        usage = await db.fetchrow("""
            SELECT u.*, p.name as plan_name, p.max_tokens, p.max_requests
            FROM usage u
            JOIN users usr ON u.user_id = usr.id
            JOIN plans p ON usr.plan_id = p.id
            WHERE u.user_id = $1 AND u.day = $2
        """, user_id, current_day)
        
        return dict(usage) if usage else None
    
    @staticmethod
    async def create_daily_usage_record(user_id: str) -> Dict:
        """Create new daily usage record"""
        current_day = date.today()
        current_month = current_day.replace(day=1)
        
        await db.execute("""
            INSERT INTO usage (user_id, tokens_used, requests, month, day)
            VALUES ($1, 0, 0, $2, $3)
            ON CONFLICT (user_id, day) DO NOTHING
        """, user_id, current_month, current_day)
        
        return await DailyUsageService.get_daily_usage(user_id)
    
    @staticmethod
    async def update_daily_usage(user_id: str, tokens_consumed: int, requests_increment: int = 1):
        """Update daily usage statistics"""
        current_day = date.today()
        current_month = current_day.replace(day=1)
        
        # Ensure usage record exists
        await DailyUsageService.create_daily_usage_record(user_id)
        
        # Update daily usage
        await db.execute("""
            UPDATE usage 
            SET tokens_used = tokens_used + $1,
                requests = requests + $2,
                updated_at = NOW()
            WHERE user_id = $3 AND day = $4
        """, tokens_consumed, requests_increment, user_id, current_day)
        
        # Also update monthly usage
        await db.execute("""
            INSERT INTO usage (user_id, tokens_used, requests, month, day)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id, month) 
            DO UPDATE SET 
                tokens_used = usage.tokens_used + $2,
                requests = usage.requests + $3,
                updated_at = NOW()
        """, user_id, tokens_consumed, requests_increment, current_month, current_day)
    
    @staticmethod
    async def check_daily_limits(user_id: str, requested_tokens: int) -> tuple[bool, Dict]:
        """Check if user can make request within daily limits"""
        usage = await DailyUsageService.get_daily_usage(user_id)
        if not usage:
            await DailyUsageService.create_daily_usage_record(user_id)
            usage = await DailyUsageService.get_daily_usage(user_id)
        
        # Check daily request limit
        requests_after = usage['requests'] + 1
        can_make_request = requests_after <= usage['max_requests']
        
        # Check token limit
        tokens_after_request = usage['tokens_used'] + requested_tokens
        can_use_tokens = tokens_after_request <= usage['max_tokens']
        
        can_proceed = can_make_request and can_use_tokens
        
        return can_proceed, {
            'current_requests': usage['requests'],
            'max_requests': usage['max_requests'],
            'current_tokens': usage['tokens_used'],
            'max_tokens': usage['max_tokens'],
            'requested_tokens': requested_tokens,
            'tokens_after_request': tokens_after_request,
            'requests_after': requests_after,
            'plan_name': usage['plan_name'],
            'limit_type': 'requests' if not can_make_request else 'tokens' if not can_use_tokens else None
        }


# Global service instance
daily_usage_service = DailyUsageService()