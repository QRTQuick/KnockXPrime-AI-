from fastapi import APIRouter, Depends
from typing import List
from datetime import date, datetime, timedelta
from app.core.auth import get_current_user
from app.core.database import db
from app.schemas.usage_schema import UsageStats, MonthlyUsage
from app.services.usage_service import usage_service

router = APIRouter()


@router.get("/current", response_model=UsageStats)
async def get_current_usage(current_user: dict = Depends(get_current_user)):
    """Get current month usage statistics"""
    return await usage_service.get_usage_stats(current_user['id'])


@router.get("/history", response_model=List[MonthlyUsage])
async def get_usage_history(
    months: int = 6,
    current_user: dict = Depends(get_current_user)
):
    """Get usage history for the last N months"""
    
    # Calculate date range
    end_date = date.today().replace(day=1)
    start_date = end_date - timedelta(days=30 * months)
    
    usage_history = await db.fetch("""
        SELECT u.month, u.tokens_used, u.requests, p.max_tokens, p.name as plan_name
        FROM usage u
        JOIN users usr ON u.user_id = usr.id
        JOIN plans p ON usr.plan_id = p.id
        WHERE u.user_id = $1 AND u.month >= $2 AND u.month <= $3
        ORDER BY u.month DESC
    """, current_user['id'], start_date, end_date)
    
    return [
        MonthlyUsage(
            month=record['month'],
            tokens_used=record['tokens_used'],
            requests=record['requests'],
            max_tokens=record['max_tokens'],
            plan_name=record['plan_name']
        )
        for record in usage_history
    ]


@router.get("/stats")
async def get_usage_analytics(current_user: dict = Depends(get_current_user)):
    """Get detailed usage analytics"""
    
    current_stats = await usage_service.get_usage_stats(current_user['id'])
    
    # Get last month for comparison
    last_month = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_usage = await db.fetchrow("""
        SELECT tokens_used, requests
        FROM usage
        WHERE user_id = $1 AND month = $2
    """, current_user['id'], last_month)
    
    # Calculate trends
    last_month_tokens = last_month_usage['tokens_used'] if last_month_usage else 0
    last_month_requests = last_month_usage['requests'] if last_month_usage else 0
    
    token_trend = current_stats.tokens_used - last_month_tokens
    request_trend = current_stats.requests - last_month_requests
    
    return {
        "current_month": {
            "tokens_used": current_stats.tokens_used,
            "requests": current_stats.requests,
            "usage_percentage": current_stats.usage_percentage
        },
        "last_month": {
            "tokens_used": last_month_tokens,
            "requests": last_month_requests
        },
        "trends": {
            "token_change": token_trend,
            "request_change": request_trend
        },
        "plan_info": {
            "name": current_stats.plan_name,
            "max_tokens": current_stats.max_tokens,
            "tokens_remaining": current_stats.tokens_remaining
        }
    }