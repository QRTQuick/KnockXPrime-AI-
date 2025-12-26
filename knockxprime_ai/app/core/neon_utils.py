"""
Neon Database REST API utilities and helpers
"""
import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings


class NeonAPIError(Exception):
    """Custom exception for Neon API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


async def test_neon_connection() -> Dict[str, Any]:
    """Test connection to Neon REST API"""
    try:
        headers = {
            "Authorization": f"Bearer {settings.neon_api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple test query
        payload = {
            "query": "SELECT 1 as test_connection",
            "params": []
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.neon_api_url}/query",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "message": "Connection successful",
                    "data": result
                }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)}"
        }


def format_neon_error(response: httpx.Response) -> str:
    """Format Neon API error response for logging"""
    try:
        error_data = response.json()
        return f"Neon API Error {response.status_code}: {error_data.get('message', 'Unknown error')}"
    except:
        return f"Neon API Error {response.status_code}: {response.text}"


def convert_params_for_neon(args: tuple) -> List[Any]:
    """Convert asyncpg-style parameters to Neon REST API format"""
    return [str(arg) if arg is not None else None for arg in args]


async def execute_with_retry(query: str, params: List = None, max_retries: int = 3) -> Dict[str, Any]:
    """Execute query with retry logic for transient failures"""
    headers = {
        "Authorization": f"Bearer {settings.neon_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "params": params or []
    }
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.neon_api_url}/query",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    error_msg = format_neon_error(response)
                    if attempt == max_retries - 1:
                        raise NeonAPIError(error_msg, response.status_code, response.json())
                    last_error = error_msg
                    
        except httpx.TimeoutException as e:
            if attempt == max_retries - 1:
                raise NeonAPIError(f"Request timeout after {max_retries} attempts: {str(e)}")
            last_error = f"Timeout on attempt {attempt + 1}"
            
        except httpx.RequestError as e:
            if attempt == max_retries - 1:
                raise NeonAPIError(f"Request error after {max_retries} attempts: {str(e)}")
            last_error = f"Request error on attempt {attempt + 1}: {str(e)}"
    
    raise NeonAPIError(f"All {max_retries} attempts failed. Last error: {last_error}")