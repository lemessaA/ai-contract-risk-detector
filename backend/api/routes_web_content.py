"""
FastAPI Routes for Web Content Analysis
API endpoints for analyzing legal content from websites
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from services.web_content_analyzer import web_analyzer
from guardrails import guardrails_system

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Pydantic models for request/response
class WebAnalysisRequest(BaseModel):
    url: HttpUrl
    analysis_options: Optional[Dict[str, Any]] = None

class BatchWebAnalysisRequest(BaseModel):
    urls: List[HttpUrl]
    analysis_options: Optional[Dict[str, Any]] = None

class ContentTypeDetectionRequest(BaseModel):
    url: HttpUrl

@router.post("/analyze-web-content", summary="Analyze legal content from a website")
async def analyze_web_content(
    request: WebAnalysisRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Analyze legal content from a single URL using contract analysis pipeline.
    
    This endpoint:
    1. Scrapes the webpage for legal content
    2. Applies contract analysis to identify risks
    3. Generates a "Before You Sign" style report
    4. Returns comprehensive analysis results
    
    Args:
        request: Web analysis request with URL and options
        
    Returns:
        Analysis ID for tracking and results
    """
    try:
        # Validate URL with guardrails
        url_validation = guardrails_system.validate_input(
            str(request.url),
            input_type="text",
            context="web_url"
        )
        
        if url_validation.triggered and url_validation.action.value == "block":
            raise HTTPException(
                status_code=400,
                detail=f"URL validation failed: {url_validation.message}"
            )
        
        # Check behavioral constraints
        behavioral_result = guardrails_system.check_behavioral_constraints(
            analysis_id="web_analysis"
        )
        
        if behavioral_result.triggered and behavioral_result.action.value == "block":
            raise HTTPException(
                status_code=429,
                detail=behavioral_result.message
            )
        
        # Start analysis
        result = await web_analyzer.analyze_web_content(
            str(request.url),
            request.analysis_options or {}
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Web content analysis failed")
            )
        
        return {
            "message": "Web content analysis started successfully",
            "analysis_id": result["analysis_id"],
            "url": str(request.url),
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Web content analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Web content analysis failed: {str(e)}"
        )

@router.post("/analyze-multiple-urls", summary="Analyze legal content from multiple websites")
async def analyze_multiple_urls(
    request: BatchWebAnalysisRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Analyze legal content from multiple URLs and combine results.
    
    This endpoint:
    1. Scrapes multiple webpages concurrently
    2. Combines legal content from all sources
    3. Runs comprehensive contract analysis
    4. Provides combined and individual results
    
    Args:
        request: Batch analysis request with URLs and options
        
    Returns:
        Analysis ID for tracking and combined results
    """
    try:
        # Validate URL count
        if len(request.urls) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 URLs allowed per batch analysis"
            )
        
        # Validate each URL
        url_strings = [str(url) for url in request.urls]
        
        for url in url_strings:
            url_validation = guardrails_system.validate_input(
                url,
                input_type="text",
                context="web_url"
            )
            
            if url_validation.triggered and url_validation.action.value == "block":
                raise HTTPException(
                    status_code=400,
                    detail=f"URL validation failed for {url}: {url_validation.message}"
                )
        
        # Check behavioral constraints
        behavioral_result = guardrails_system.check_behavioral_constraints(
            analysis_id="batch_web_analysis"
        )
        
        if behavioral_result.triggered and behavioral_result.action.value == "block":
            raise HTTPException(
                status_code=429,
                detail=behavioral_result.message
            )
        
        # Start batch analysis
        result = await web_analyzer.analyze_multiple_urls(
            url_strings,
            request.analysis_options or {}
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Batch web content analysis failed")
            )
        
        return {
            "message": "Batch web content analysis started successfully",
            "analysis_id": result["analysis_id"],
            "url_count": len(url_strings),
            "urls": url_strings,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch web content analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch web content analysis failed: {str(e)}"
        )

@router.post("/detect-content-type", summary="Detect type of legal content on a webpage")
async def detect_content_type(request: ContentTypeDetectionRequest) -> Dict[str, Any]:
    """
    Detect the type of legal content on a webpage.
    
    This endpoint analyzes the URL, title, and content to determine
    what type of legal document it contains (Terms of Service,
    Privacy Policy, Cookie Policy, etc.).
    
    Args:
        request: Content type detection request with URL
        
    Returns:
        Detected content types with confidence scores
    """
    try:
        # Validate URL
        url_validation = guardrails_system.validate_input(
            str(request.url),
            input_type="text",
            context="web_url"
        )
        
        if url_validation.triggered and url_validation.action.value == "block":
            raise HTTPException(
                status_code=400,
                detail=f"URL validation failed: {url_validation.message}"
            )
        
        # Detect content type
        result = await web_analyzer.detect_legal_content_type(str(request.url))
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Content type detection failed")
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content type detection error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Content type detection failed: {str(e)}"
        )

@router.get("/web-analysis/{analysis_id}/status", summary="Get web content analysis status")
async def get_web_analysis_status(analysis_id: str) -> Dict[str, Any]:
    """
    Get the current status of a web content analysis.
    
    Args:
        analysis_id: ID of the web content analysis
        
    Returns:
        Current status, progress, and basic metadata
    """
    try:
        result = web_analyzer.get_analysis_status(analysis_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get web analysis status error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis status: {str(e)}"
        )

@router.get("/web-analysis/{analysis_id}/results", summary="Get web content analysis results")
async def get_web_analysis_results(analysis_id: str) -> Dict[str, Any]:
    """
    Get the complete results of a web content analysis.
    
    Args:
        analysis_id: ID of the web content analysis
        
    Returns:
        Complete analysis results with scraping metadata and contract analysis
    """
    try:
        result = web_analyzer.get_analysis_results(analysis_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get web analysis results error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis results: {str(e)}"
        )

@router.get("/web-analysis/active", summary="Get all active web content analyses")
async def get_active_web_analyses() -> Dict[str, Any]:
    """
    Get all currently active web content analyses.
    
    Returns:
        List of active analyses with basic metadata
    """
    try:
        from storage import get_analysis_store
        
        analysis_store = get_analysis_store()
        active_analyses = []
        
        for analysis_id, analysis in analysis_store.items():
            if analysis.get("type") in ["web_content", "web_content_batch"] and analysis.get("status") == "processing":
                active_analyses.append({
                    "analysis_id": analysis_id,
                    "type": analysis.get("type"),
                    "status": analysis.get("status"),
                    "progress": analysis.get("progress", 0),
                    "started_at": analysis.get("started_at"),
                    "urls": analysis.get("urls", [])
                })
        
        return {
            "active_analyses": active_analyses,
            "total_active": len(active_analyses)
        }
        
    except Exception as e:
        logger.error(f"Get active web analyses error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active analyses: {str(e)}"
        )

@router.delete("/web-analysis/{analysis_id}", summary="Cancel or delete web content analysis")
async def cancel_web_analysis(analysis_id: str) -> Dict[str, Any]:
    """
    Cancel an active web content analysis or delete completed analysis.
    
    Args:
        analysis_id: ID of the web content analysis to cancel/delete
        
    Returns:
        Confirmation of cancellation/deletion
    """
    try:
        from storage import get_analysis_store
        
        analysis_store = get_analysis_store()
        
        if analysis_id not in analysis_store:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found"
            )
        
        analysis = analysis_store[analysis_id]
        
        if analysis.get("status") == "processing":
            # Mark as cancelled
            analysis.update({
                "status": "cancelled",
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "message": "Web content analysis cancelled",
                "analysis_id": analysis_id,
                "status": "cancelled"
            }
        
        else:
            # Delete completed analysis
            del analysis_store[analysis_id]
            
            return {
                "message": "Web content analysis deleted",
                "analysis_id": analysis_id,
                "status": "deleted"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel web analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel analysis: {str(e)}"
        )

@router.get("/web-analysis/stats", summary="Get web content analysis statistics")
async def get_web_analysis_stats() -> Dict[str, Any]:
    """
    Get statistics about web content analyses.
    
    Returns:
        Analysis statistics including success rates, common content types, etc.
    """
    try:
        from storage import get_analysis_store
        
        analysis_store = get_analysis_store()
        
        # Filter web content analyses
        web_analyses = [
            analysis for analysis in analysis_store.values()
            if analysis.get("type") in ["web_content", "web_content_batch"]
        ]
        
        total_analyses = len(web_analyses)
        completed_analyses = len([a for a in web_analyses if a.get("status") == "completed"])
        failed_analyses = len([a for a in web_analyses if a.get("status") == "failed"])
        active_analyses = len([a for a in web_analyses if a.get("status") == "processing"])
        
        # Calculate success rate
        success_rate = (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0
        
        # Analyze common content types from completed analyses
        content_types = {}
        total_urls_analyzed = 0
        
        for analysis in web_analyses:
            if analysis.get("status") == "completed" and "results" in analysis:
                results = analysis["results"]
                
                if analysis.get("type") == "web_content":
                    # Single URL analysis
                    if "web_metadata" in results:
                        url = results["web_metadata"]["url"]
                        content_type = web_analyzer.detect_legal_content_type(url)
                        if content_type.get("success"):
                            primary_type = content_type.get("primary_type", "unknown")
                            content_types[primary_type] = content_types.get(primary_type, 0) + 1
                        total_urls_analyzed += 1
                
                elif analysis.get("type") == "web_content_batch":
                    # Batch analysis
                    if "batch_metadata" in results:
                        total_urls_analyzed += results["batch_metadata"].get("successful_scrapes", 0)
        
        return {
            "total_analyses": total_analyses,
            "completed_analyses": completed_analyses,
            "failed_analyses": failed_analyses,
            "active_analyses": active_analyses,
            "success_rate": round(success_rate, 2),
            "total_urls_analyzed": total_urls_analyzed,
            "common_content_types": content_types,
            "most_common_type": max(content_types.items(), key=lambda x: x[1])[0] if content_types else None
        }
        
    except Exception as e:
        logger.error(f"Get web analysis stats error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )

# Add the router to the main app
# In main.py, add:
# from api.routes_web_content import router as web_content_router
# app.include_router(web_content_router, prefix="/api/web-content", tags=["web-content"])
