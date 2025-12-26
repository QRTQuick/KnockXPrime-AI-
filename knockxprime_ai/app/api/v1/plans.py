from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.core.auth import get_current_user
from app.core.plans import get_all_plans, get_plan_by_id
from app.core.database import db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_plans():
    """Get all available subscription plans"""
    plans = await get_all_plans()
    return plans


@router.get("/{plan_id}")
async def get_plan(plan_id: str):
    """Get specific plan details"""
    plan = await get_plan_by_id(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.post("/upgrade")
async def upgrade_plan(
    new_plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Upgrade user's subscription plan"""
    
    # Check if new plan exists
    new_plan = await get_plan_by_id(new_plan_id)
    if not new_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Check if it's actually an upgrade (higher price)
    current_plan_price = current_user['price']
    if new_plan['price'] <= current_plan_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only upgrade to a higher-tier plan"
        )
    
    # Update user's plan
    await db.execute(
        "UPDATE users SET plan_id = $1, updated_at = NOW() WHERE id = $2",
        new_plan_id, current_user['id']
    )
    
    return {
        "message": "Plan upgraded successfully",
        "old_plan": current_user['plan_name'],
        "new_plan": new_plan['name'],
        "new_max_tokens": new_plan['max_tokens']
    }


@router.get("/compare/pricing")
async def compare_plans():
    """Get plan comparison data"""
    plans = await get_all_plans()
    
    comparison = []
    for plan in plans:
        tokens_per_dollar = plan['max_tokens'] / plan['price'] if plan['price'] > 0 else float('inf')
        comparison.append({
            "name": plan['name'],
            "price": plan['price'],
            "max_tokens": plan['max_tokens'],
            "max_requests": plan['max_requests'],
            "tokens_per_dollar": round(tokens_per_dollar, 2) if tokens_per_dollar != float('inf') else "Unlimited",
            "features": {
                "api_access": True,
                "usage_analytics": True,
                "email_support": plan['price'] > 0,
                "priority_support": plan['price'] >= 10.00,
                "daily_limits": True
            }
        })
    
    return {
        "plans": comparison,
        "currency": "USD",
        "billing_cycle": "monthly",
        "limits": "daily"
    }