import httpx
import json
from typing import Dict, Any, List
from app.core.config import settings
from app.schemas.chat_schema import ChatRequest, ChatResponse


class GrokService:
    def __init__(self):
        self.base_url = settings.grok_base_url
        self.api_key = settings.grok_api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat_completion(self, request: ChatRequest) -> Dict[str, Any]:
        """Send chat completion request to Grok API"""
        
        # Prepare request payload
        payload = {
            "model": request.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": request.stream
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            
            response.raise_for_status()
            return response.json()
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
        return len(text) // 4
    
    def calculate_request_tokens(self, request: ChatRequest) -> int:
        """Calculate estimated tokens for the request"""
        total_chars = sum(len(msg.content) for msg in request.messages)
        input_tokens = self.estimate_tokens(str(total_chars))
        
        # Add estimated output tokens
        estimated_output = request.max_tokens or 1000
        
        return input_tokens + estimated_output


# Global service instance
grok_service = GrokService()