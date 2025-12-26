from fastapi import APIRouter, HTTPException, status, Depends
from app.core.auth import get_current_user
from app.schemas.chat_schema import ChatRequest, ChatResponse, UsageInfo
from app.services.grok_service import grok_service
from app.services.billing_guard import billing_guard
from app.services.usage_service import usage_service

router = APIRouter()


@router.post("/completions", response_model=dict)
async def chat_completion(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Handle chat completion requests with billing enforcement"""
    
    try:
        # Validate request against user's plan limits
        validation_result = await billing_guard.validate_request(current_user, request)
        
        # Make request to Grok API
        grok_response = await grok_service.chat_completion(request)
        
        # Extract actual token usage
        actual_tokens = billing_guard.extract_token_usage(grok_response)
        
        # Log usage (use actual tokens if available, otherwise use estimate)
        tokens_to_log = actual_tokens if actual_tokens > 0 else validation_result['estimated_tokens']
        await billing_guard.log_usage(current_user['id'], tokens_to_log)
        
        # Add usage info to response
        usage_stats = await usage_service.get_usage_stats(current_user['id'])
        grok_response['usage_info'] = {
            "tokens_used_this_month": usage_stats.tokens_used,
            "tokens_remaining": usage_stats.tokens_remaining,
            "plan_name": usage_stats.plan_name,
            "max_tokens": usage_stats.max_tokens
        }
        
        return grok_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/usage", response_model=UsageInfo)
async def get_chat_usage(current_user: dict = Depends(get_current_user)):
    """Get current usage information"""
    
    usage_stats = await usage_service.get_usage_stats(current_user['id'])
    
    return UsageInfo(
        tokens_used=usage_stats.tokens_used,
        tokens_remaining=usage_stats.tokens_remaining,
        requests_made=usage_stats.requests,
        plan_name=usage_stats.plan_name,
        max_tokens=usage_stats.max_tokens
    )