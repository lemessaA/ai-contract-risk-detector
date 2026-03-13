"""
Guardrails Middleware for FastAPI
Provides API-wide safety mechanisms and monitoring
"""

import time
import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from guardrails import guardrails_system, RiskLevel, GuardrailAction

logger = logging.getLogger(__name__)

class GuardrailsMiddleware(BaseHTTPMiddleware):
    """Middleware to apply guardrails to all API requests"""
    
    def __init__(self, app, enable_rate_limiting: bool = True):
        super().__init__(app)
        self.enable_rate_limiting = enable_rate_limiting
        self.request_counts = {}
        self.blocked_ips = {}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request through guardrails"""
        
        # Get client IP for tracking
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            if time.time() - self.blocked_ips[client_ip] < 3600:  # Block for 1 hour
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "IP address temporarily blocked due to suspicious activity",
                        "guardrail_triggered": True,
                        "risk_level": "high"
                    }
                )
            else:
                # Unblock after timeout
                del self.blocked_ips[client_ip]
        
        # Rate limiting check
        if self.enable_rate_limiting:
            rate_limit_result = self._check_rate_limit(client_ip)
            if rate_limit_result["blocked"]:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": rate_limit_result["message"],
                        "guardrail_triggered": True,
                        "risk_level": "medium"
                    }
                )
        
        # Suspicious activity detection
        suspicious_result = self._detect_suspicious_activity(request, client_ip)
        if suspicious_result["blocked"]:
            return JSONResponse(
                status_code=400,
                content={
                    "error": suspicious_result["message"],
                    "guardrail_triggered": True,
                    "risk_level": suspicious_result["risk_level"]
                }
            )
        
        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log security events
        self._log_security_event(request, response, process_time, client_ip)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> Dict[str, Any]:
        """Check if client exceeds rate limits"""
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = [
                req_time for req_time in self.request_counts[ip]
                if current_time - req_time < 60
            ]
            if not self.request_counts[ip]:
                del self.request_counts[ip]
        
        # Check current request count
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        request_count = len(self.request_counts[client_ip])
        
        if request_count >= 100:  # 100 requests per minute
            self.blocked_ips[client_ip] = current_time
            return {
                "blocked": True,
                "message": "Rate limit exceeded. IP temporarily blocked.",
                "request_count": request_count
            }
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        
        return {
            "blocked": False,
            "request_count": request_count + 1
        }
    
    def _detect_suspicious_activity(self, request: Request, client_ip: str) -> Dict[str, Any]:
        """Detect suspicious request patterns"""
        
        # Check for suspicious headers
        suspicious_headers = [
            "X-Forwarded-Host",
            "X-Originating-IP",
            "X-Remote-IP",
            "X-Remote-Addr"
        ]
        
        header_score = 0
        for header in suspicious_headers:
            if header in request.headers:
                header_score += 1
        
        # Check for suspicious user agents
        user_agent = request.headers.get("User-Agent", "").lower()
        suspicious_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
            "scanner", "crawler", "bot", "spider"
        ]
        
        agent_score = sum(1 for agent in suspicious_agents if agent in user_agent)
        
        # Check for unusual request patterns
        url_path = request.url.path.lower()
        suspicious_paths = [
            "/admin", "/config", "/env", "/secret", "/backup",
            "/test", "/debug", "/.env", "/.git"
        ]
        
        path_score = sum(1 for path in suspicious_paths if path in url_path)
        
        # Calculate total risk score
        total_score = header_score + agent_score + path_score
        
        if total_score >= 3:
            self.blocked_ips[client_ip] = time.time()
            return {
                "blocked": True,
                "message": "Suspicious activity detected. Access temporarily blocked.",
                "risk_level": "high",
                "score": total_score
            }
        elif total_score >= 2:
            return {
                "blocked": False,
                "message": "Suspicious activity detected",
                "risk_level": "medium",
                "score": total_score
            }
        
        return {
            "blocked": False,
            "risk_level": "low",
            "score": total_score
        }
    
    def _log_security_event(self, request: Request, response: Response, 
                           process_time: float, client_ip: str):
        """Log security-related events"""
        
        # Log slow requests (potential DoS)
        if process_time > 10:  # 10 seconds
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {process_time:.2f}s from IP {client_ip}"
            )
        
        # Log error responses
        if response.status_code >= 400:
            logger.warning(
                f"Error response: {response.status_code} for {request.method} "
                f"{request.url.path} from IP {client_ip}"
            )
        
        # Log file upload attempts
        if request.method == "POST" and "upload" in request.url.path:
            logger.info(
                f"File upload attempt: {request.method} {request.url.path} "
                f"from IP {client_ip}"
            )

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Add comprehensive security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' ws://localhost:* wss://localhost:* http://localhost:* https://localhost:*"
        )
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        
        return response

class AuditLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests for audit purposes"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("audit")
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Log request details
        request_data = {
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
            "content_type": request.headers.get("Content-Type", "")
        }
        
        # Process request
        response = await call_next(request)
        
        # Log response details
        end_time = time.time()
        request_data.update({
            "status_code": response.status_code,
            "response_time": end_time - start_time,
            "response_size": len(response.body) if hasattr(response, 'body') else 0
        })
        
        # Log to audit logger
        self.logger.info(f"API Request: {request_data}")
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
