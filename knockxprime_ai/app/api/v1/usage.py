from fastapi import APIRouter, Depends
from typing import List
from datetime import date, datetime, timedelta
from app.core.auth import get_current_user
from app.core.database import db
from app.schemas.usage_schema import UsageStats, MonthlyUsage
from app.core.daily_usage import daily_usage_service

router = APIRouter()


@router.get("/current")
async def get_current_usage(current_user: dict = Depends(get_current_user)):
    """Get current day usage statistics"""
    usage = await daily_usage_service.get_daily_usage(current_user['id'])
    if not usage:
        await daily_usage_service.create_daily_usage_record(current_user['id'])
        usage = await daily_usage_service.get_daily_usage(current_user['id'])
    
    tokens_remaining = max(0, usage['max_tokens'] - usage['tokens_used'])
    requests_remaining = max(0, usage['max_requests'] - usage['requests'])
    usage_percentage = (usage['tokens_used'] / usage['max_tokens']) * 100
    
    return {
        "user_id": current_user['id'],
        "tokens_used": usage['tokens_used'],
        "requests": usage['requests'],
        "day": date.today(),
        "plan_name": usage['plan_name'],
        "max_tokens": usage['max_tokens'],
        "max_requests": usage['max_requests'],
        "tokens_remaining": tokens_remaining,
        "requests_remaining": requests_remaining,
        "usage_percentage": round(usage_percentage, 2)
    }


@router.get("/daily")
async def get_daily_usage(current_user: dict = Depends(get_current_user)):
    """Get today's usage statistics"""
    return await get_current_usage(current_user)


@router.get("/monthly")
async def get_monthly_usage(current_user: dict = Depends(get_current_user)):
    """Get current month usage statistics"""
    current_month = date.today().replace(day=1)
    
    usage = await db.fetchrow("""
        SELECT u.tokens_used, u.requests, p.name as plan_name, p.max_tokens, p.max_requests
        FROM usage u
        JOIN users usr ON u.user_id = usr.id
        JOIN plans p ON usr.plan_id = p.id
        WHERE u.user_id = $1 AND u.month = $2
    """, current_user['id'], current_month)
    
    if not usage:
        return {
            "month": current_month,
            "tokens_used": 0,
            "requests": 0,
            "max_tokens": current_user.get('max_tokens', 0),
            "max_requests": current_user.get('max_requests', 0),
            "plan_name": current_user.get('plan_name', 'Unknown')
        }
    
    return {
        "month": current_month,
        "tokens_used": usage['tokens_used'],
        "requests": usage['requests'],
        "max_tokens": usage['max_tokens'],
        "max_requests": usage['max_requests'],
        "plan_name": usage['plan_name']
    }


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
        SELECT u.month, u.tokens_used, u.requests, p.max_tokens, p.max_requests, p.name as plan_name
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
    
    # Get today's usage
    today_usage = await daily_usage_service.get_daily_usage(current_user['id'])
    if not today_usage:
        await daily_usage_service.create_daily_usage_record(current_user['id'])
        today_usage = await daily_usage_service.get_daily_usage(current_user['id'])
    
    # Get yesterday's usage for comparison
    yesterday = date.today() - timedelta(days=1)
    yesterday_usage = await db.fetchrow("""
        SELECT tokens_used, requests
        FROM usage
        WHERE user_id = $1 AND day = $2
    """, current_user['id'], yesterday)
    
    # Calculate trends
    yesterday_tokens = yesterday_usage['tokens_used'] if yesterday_usage else 0
    yesterday_requests = yesterday_usage['requests'] if yesterday_usage else 0
    
    token_trend = today_usage['tokens_used'] - yesterday_tokens
    request_trend = today_usage['requests'] - yesterday_requests
    
    return {
        "today": {
            "tokens_used": today_usage['tokens_used'],
            "requests": today_usage['requests'],
            "tokens_remaining": max(0, today_usage['max_tokens'] - today_usage['tokens_used']),
            "requests_remaining": max(0, today_usage['max_requests'] - today_usage['requests'])
        },
        "yesterday": {
            "tokens_used": yesterday_tokens,
            "requests": yesterday_requests
        },
        "trends": {
            "token_change": token_trend,
            "request_change": request_trend
        },
        "plan_info": {
            "name": today_usage['plan_name'],
            "max_tokens": today_usage['max_tokens'],
            "max_requests": today_usage['max_requests'],
            "price": current_user.get('price', 0)
        }
    }