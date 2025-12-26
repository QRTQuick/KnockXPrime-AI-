from fastapi import APIRouter, HTTPException, status, Depends
from app.core.auth import get_current_user
from app.schemas.chat_schema import ChatRequest, ChatResponse, UsageInfo
from app.services.grok_service import grok_service
from app.services.billing_guard import billing_guard
from app.core.daily_usage import daily_usage_service

router = APIRouter()


@router.post("/completions", response_model=dict)
async def chat_completion(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Handle chat completion requests with billing enforcement"""
    
    try:
        # Validate request against user's plan limits (daily)
        validation_result = await billing_guard.validate_request(current_user, request)
        
        # Make request to Grok API
        grok_response = await grok_service.chat_completion(request)
        
        # Extract actual token usage
        actual_tokens = billing_guard.extract_token_usage(grok_response)
        
        # Log usage (use actual tokens if available, otherwise use estimate)
        tokens_to_log = actual_tokens if actual_tokens > 0 else validation_result['estimated_tokens']
        await billing_guard.log_usage(current_user['id'], tokens_to_log)
        
        # Add usage info to response
        daily_usage = await daily_usage_service.get_daily_usage(current_user['id'])
        grok_response['usage_info'] = {
            "tokens_used_today": daily_usage['tokens_used'],
            "tokens_remaining_today": max(0, daily_usage['max_tokens'] - daily_usage['tokens_used']),
            "requests_made_today": daily_usage['requests'],
            "requests_remaining_today": max(0, daily_usage['max_requests'] - daily_usage['requests']),
            "plan_name": daily_usage['plan_name'],
            "max_tokens_daily": daily_usage['max_tokens'],
            "max_requests_daily": daily_usage['max_requests']
        }
        
        return grok_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/usage")
async def get_chat_usage(current_user: dict = Depends(get_current_user)):
    """Get current usage information"""
    
    daily_usage = await daily_usage_service.get_daily_usage(current_user['id'])
    if not daily_usage:
        await daily_usage_service.create_daily_usage_record(current_user['id'])
        daily_usage = await daily_usage_service.get_daily_usage(current_user['id'])
    
    return {
        "tokens_used": daily_usage['tokens_used'],
        "tokens_remaining": max(0, daily_usage['max_tokens'] - daily_usage['tokens_used']),
        "requests_made": daily_usage['requests'],
        "requests_remaining": max(0, daily_usage['max_requests'] - daily_usage['requests']),
        "plan_name": daily_usage['plan_name'],
        "max_tokens": daily_usage['max_tokens'],
        "max_requests": daily_usage['max_requests'],
        "period": "daily"
    }