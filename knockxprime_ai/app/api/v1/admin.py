from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.auth import get_current_user
from app.core.database import db

router = APIRouter()


async def verify_admin_user(current_user: dict = Depends(get_current_user)):
    """Verify user has admin privileges"""
    # For now, check if user is the first registered user or has admin email
    admin_emails = ["admin@knockxprime.ai", "owner@knockxprime.ai"]
    
    if current_user['email'] not in admin_emails:
        # Check if first user (user ID 1 or earliest created)
        first_user = await db.fetchrow(
            "SELECT id FROM users ORDER BY created_at ASC LIMIT 1"
        )
        if not first_user or str(current_user['id']) != str(first_user['id']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
    
    return current_user


@router.get("/stats/overview")
async def admin_overview(admin_user: dict = Depends(verify_admin_user)):
    """Get admin dashboard overview"""
    
    # User statistics
    total_users = await db.fetchval("SELECT COUNT(*) FROM users")
    new_users_today = await db.fetchval(
        "SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE"
    )
    new_users_week = await db.fetchval(
        "SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '7 days'"
    )
    
    # Usage statistics
    current_month = date.today().replace(day=1)
    total_tokens_month = await db.fetchval(
        "SELECT COALESCE(SUM(tokens_used), 0) FROM usage WHERE month = $1",
        current_month
    )
    total_requests_month = await db.fetchval(
        "SELECT COALESCE(SUM(requests), 0) FROM usage WHERE month = $1",
        current_month
    )
    
    # Revenue estimation (based on active users with paid plans)
    revenue_estimate = await db.fetchval("""
        SELECT COALESCE(SUM(p.price), 0)
        FROM users u
        JOIN plans p ON u.plan_id = p.id
        WHERE u.created_at >= NOW() - INTERVAL '30 days'
    """)
    
    # Plan distribution
    plan_distribution = await db.fetch("""
        SELECT p.name, COUNT(u.id) as user_count
        FROM plans p
        LEFT JOIN users u ON p.id = u.plan_id
        GROUP BY p.id, p.name
        ORDER BY p.price ASC
    """)
    
    return {
        "users": {
            "total": total_users,
            "new_today": new_users_today,
            "new_this_week": new_users_week
        },
        "usage": {
            "total_tokens_this_month": total_tokens_month,
            "total_requests_this_month": total_requests_month
        },
        "revenue": {
            "estimated_monthly": float(revenue_estimate or 0),
            "currency": "USD"
        },
        "plan_distribution": [
            {"plan": row['name'], "users": row['user_count']}
            for row in plan_distribution
        ]
    }


@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    plan_filter: Optional[str] = None,
    admin_user: dict = Depends(verify_admin_user)
):
    """List all users with pagination"""
    
    query = """
        SELECT u.id, u.username, u.email, u.created_at, u.updated_at,
               p.name as plan_name, p.price
        FROM users u
        JOIN plans p ON u.plan_id = p.id
    """
    params = []
    
    if plan_filter:
        query += " WHERE p.name = $1"
        params.append(plan_filter)
    
    query += " ORDER BY u.created_at DESC LIMIT $" + str(len(params) + 1) + " OFFSET $" + str(len(params) + 2)
    params.extend([limit, offset])
    
    users = await db.fetch(query, *params)
    
    return {
        "users": [dict(user) for user in users],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": len(users) == limit
        }
    }


@router.get("/usage/top-users")
async def top_users_by_usage(
    limit: int = 10,
    admin_user: dict = Depends(verify_admin_user)
):
    """Get top users by token usage this month"""
    
    current_month = date.today().replace(day=1)
    
    top_users = await db.fetch("""
        SELECT u.username, u.email, p.name as plan_name,
               usage.tokens_used, usage.requests, p.max_tokens,
               ROUND((usage.tokens_used::float / p.max_tokens) * 100, 2) as usage_percentage
        FROM usage
        JOIN users u ON usage.user_id = u.id
        JOIN plans p ON u.plan_id = p.id
        WHERE usage.month = $1
        ORDER BY usage.tokens_used DESC
        LIMIT $2
    """, current_month, limit)
    
    return {
        "top_users": [dict(user) for user in top_users],
        "month": current_month.isoformat()
    }


@router.post("/users/{user_id}/reset-usage")
async def reset_user_usage(
    user_id: str,
    admin_user: dict = Depends(verify_admin_user)
):
    """Reset user's current month usage (admin only)"""
    
    current_month = date.today().replace(day=1)
    
    # Check if user exists
    user = await db.fetchrow("SELECT username FROM users WHERE id = $1", user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Reset usage
    await db.execute("""
        UPDATE usage 
        SET tokens_used = 0, requests = 0, updated_at = NOW()
        WHERE user_id = $1 AND month = $2
    """, user_id, current_month)
    
    return {
        "message": f"Usage reset for user {user['username']}",
        "user_id": user_id,
        "month": current_month.isoformat()
    }


@router.get("/system/health")
async def system_health(admin_user: dict = Depends(verify_admin_user)):
    """Get detailed system health information"""
    
    # Database health
    db_test = await db.fetchval("SELECT 1")
    db_healthy = db_test == 1
    
    # Recent error count (you'd implement error logging)
    # For now, just return basic info
    
    return {
        "database": {
            "status": "healthy" if db_healthy else "error",
            "connection": "active"
        },
        "api": {
            "status": "healthy",
            "uptime": "N/A"  # You could track this
        },
        "external_services": {
            "grok_api": "unknown"  # You could ping Grok API
        },
        "timestamp": datetime.utcnow().isoformat()
    }