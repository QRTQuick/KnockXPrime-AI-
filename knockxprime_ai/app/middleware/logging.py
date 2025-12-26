"""
Request logging middleware
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import uuid


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced request logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID if not exists
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Get client information
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request start
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "timestamp": time.time()
        }
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            response_info = {
                **request_info,
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "response_size": response.headers.get("content-length", "unknown")
            }
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log to console (in production, use proper logging)
            self.log_request(response_info)
            
            return response
            
        except Exception as e:
            # Log error
            error_info = {
                **request_info,
                "error": str(e),
                "process_time": round(time.time() - start_time, 3)
            }
            self.log_error(error_info)
            raise
    
    def get_client_ip(self, request: Request) -> str:
        """Extract real client IP from headers"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"
    
    def log_request(self, info: dict):
        """Log successful request"""
        print(f"[REQUEST] {info['client_ip']} - {info['method']} {info['path']} - {info['status_code']} - {info['process_time']}s")
    
    def log_error(self, info: dict):
        """Log error request"""
        print(f"[ERROR] {info['client_ip']} - {info['method']} {info['path']} - ERROR: {info['error']} - {info['process_time']}s")