from fastapi import HTTPException, status
from typing import Dict, Any
from app.core.daily_usage import daily_usage_service
from app.services.grok_service import grok_service
from app.schemas.chat_schema import ChatRequest


class BillingGuard:
    """Enforce subscription plan limits and billing rules"""
    
    @staticmethod
    async def validate_request(user: Dict[str, Any], chat_request: ChatRequest) -> Dict[str, Any]:
        """Validate if user can make the request within their plan limits"""
        
        # Estimate tokens for the request
        estimated_tokens = grok_service.calculate_request_tokens(chat_request)
        
        # Check daily limits (both requests and tokens)
        can_proceed, usage_info = await daily_usage_service.check_daily_limits(
            user['id'], estimated_tokens
        )
        
        if not can_proceed:
            limit_type = usage_info.get('limit_type', 'unknown')
            
            if limit_type == 'requests':
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Daily request limit exceeded",
                        "message": f"You have reached your daily limit of {usage_info['max_requests']} requests.",
                        "current_requests": usage_info['current_requests'],
                        "max_requests": usage_info['max_requests'],
                        "plan_name": usage_info['plan_name'],
                        "upgrade_required": usage_info['plan_name'] == 'Baby Free'
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail={
                        "error": "Daily token limit exceeded",
                        "message": f"Request requires {estimated_tokens} tokens, but you only have {usage_info['max_tokens'] - usage_info['current_tokens']} remaining today.",
                        "current_tokens": usage_info['current_tokens'],
                        "max_tokens": usage_info['max_tokens'],
                        "plan_name": usage_info['plan_name'],
                        "upgrade_required": True
                    }
                )
        
        return {
            "estimated_tokens": estimated_tokens,
            "usage_info": usage_info
        }
    
    @staticmethod
    async def log_usage(user_id: str, actual_tokens: int):
        """Log actual token usage after successful request"""
        await daily_usage_service.update_daily_usage(user_id, actual_tokens, 1)
    
    @staticmethod
    def extract_token_usage(grok_response: Dict[str, Any]) -> int:
        """Extract actual token usage from Grok API response"""
        usage = grok_response.get('usage', {})
        return usage.get('total_tokens', 0)


# Global guard instance
billing_guard = BillingGuard()