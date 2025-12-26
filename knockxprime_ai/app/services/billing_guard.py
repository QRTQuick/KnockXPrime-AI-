from fastapi import HTTPException, status
from typing import Dict, Any
from app.services.usage_service import usage_service
from app.services.grok_service import grok_service
from app.schemas.chat_schema import ChatRequest


class BillingGuard:
    """Enforce subscription plan limits and billing rules"""
    
    @staticmethod
    async def validate_request(user: Dict[str, Any], chat_request: ChatRequest) -> Dict[str, Any]:
        """Validate if user can make the request within their plan limits"""
        
        # Estimate tokens for the request
        estimated_tokens = grok_service.calculate_request_tokens(chat_request)
        
        # Check usage limits
        can_proceed, usage_info = await usage_service.check_usage_limits(
            user['id'], estimated_tokens
        )
        
        if not can_proceed:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "Token limit exceeded",
                    "message": f"Request requires {estimated_tokens} tokens, but you only have {usage_info['max_tokens'] - usage_info['current_usage']} remaining.",
                    "current_usage": usage_info['current_usage'],
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
        await usage_service.update_usage(user_id, actual_tokens, 1)
    
    @staticmethod
    def extract_token_usage(grok_response: Dict[str, Any]) -> int:
        """Extract actual token usage from Grok API response"""
        usage = grok_response.get('usage', {})
        return usage.get('total_tokens', 0)


# Global guard instance
billing_guard = BillingGuard()