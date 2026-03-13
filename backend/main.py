"""
Main FastAPI application for AI Contract Risk Detector
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from config import settings
from api.routes_contract import router as contract_router
from api.routes_ai_chat import router as ai_chat_router
from api.routes_version_comparison import router as version_comparison_router
from api.routes_reports import router as reports_router
from api.routes_web_content import router as web_content_router
from api.routes_payments import router as payments_router
from middleware import GuardrailsMiddleware, SecurityHeadersMiddleware, AuditLoggerMiddleware

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent AI system for contract risk analysis",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],  # Next.js ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security and guardrails middleware
app.add_middleware(AuditLoggerMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(GuardrailsMiddleware, enable_rate_limiting=True)

# Create uploads directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Include routers
app.include_router(contract_router, prefix="/api", tags=["contracts"])
app.include_router(ai_chat_router)
app.include_router(version_comparison_router)
app.include_router(reports_router)
app.include_router(web_content_router, prefix="/api/web-content", tags=["web-content"])
app.include_router(payments_router, prefix="/api/payments", tags=["payments"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Contract Risk Detector API",
        "version": settings.app_version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "groq_configured": bool(settings.groq_api_key)
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
