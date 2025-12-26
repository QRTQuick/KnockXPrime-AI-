from datetime import date, datetime
from typing import Dict, Optional
import uuid
from app.core.database import db
from app.schemas.usage_schema import UsageStats


class UsageService:
    
    @staticmethod
    async def get_current_usage(user_id: str) -> Optional[Dict]:
        """Get current month usage for user"""
        current_month = date.today().replace(day=1)
        
        usage = await db.fetchrow("""
            SELECT u.*, p.name as plan_name, p.max_tokens
            FROM usage u
            JOIN users usr ON u.user_id = usr.id
            JOIN plans p ON usr.plan_id = p.id
            WHERE u.user_id = $1 AND u.month = $2
        """, user_id, current_month)
        
        return dict(usage) if usage else None
    
    @staticmethod
    async def create_usage_record(user_id: str) -> Dict:
        """Create new usage record for current month"""
        current_month = date.today().replace(day=1)
        
        await db.execute("""
            INSERT INTO usage (user_id, tokens_used, requests, month)
            VALUES ($1, 0, 0, $2)
            ON CONFLICT (user_id, month) DO NOTHING
        """, user_id, current_month)
        
        return await UsageService.get_current_usage(user_id)
    
    @staticmethod
    async def update_usage(user_id: str, tokens_consumed: int, requests_increment: int = 1):
        """Update usage statistics"""
        current_month = date.today().replace(day=1)
        
        # Ensure usage record exists
        await UsageService.create_usage_record(user_id)
        
        # Update usage
        await db.execute("""
            UPDATE usage 
            SET tokens_used = tokens_used + $1,
                requests = requests + $2,
                updated_at = NOW()
            WHERE user_id = $3 AND month = $4
        """, tokens_consumed, requests_increment, user_id, current_month)
    
    @staticmethod
    async def get_usage_stats(user_id: str) -> UsageStats:
        """Get comprehensive usage statistics"""
        current_month = date.today().replace(day=1)
        
        # Get or create usage record
        usage = await UsageService.get_current_usage(user_id)
        if not usage:
            await UsageService.create_usage_record(user_id)
            usage = await UsageService.get_current_usage(user_id)
        
        tokens_remaining = max(0, usage['max_tokens'] - usage['tokens_used'])
        usage_percentage = (usage['tokens_used'] / usage['max_tokens']) * 100
        
        return UsageStats(
            user_id=uuid.UUID(user_id),
            tokens_used=usage['tokens_used'],
            requests=usage['requests'],
            month=current_month,
            plan_name=usage['plan_name'],
            max_tokens=usage['max_tokens'],
            tokens_remaining=tokens_remaining,
            usage_percentage=round(usage_percentage, 2)
        )
    
    @staticmethod
    async def check_usage_limits(user_id: str, requested_tokens: int) -> tuple[bool, Dict]:
        """Check if user can make request within limits"""
        usage = await UsageService.get_current_usage(user_id)
        if not usage:
            await UsageService.create_usage_record(user_id)
            usage = await UsageService.get_current_usage(user_id)
        
        tokens_after_request = usage['tokens_used'] + requested_tokens
        can_proceed = tokens_after_request <= usage['max_tokens']
        
        return can_proceed, {
            'current_usage': usage['tokens_used'],
            'max_tokens': usage['max_tokens'],
            'requested_tokens': requested_tokens,
            'tokens_after_request': tokens_after_request,
            'plan_name': usage['plan_name']
        }


# Global service instance
usage_service = UsageService()