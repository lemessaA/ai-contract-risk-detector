"""
FastAPI Routes for Contract Analysis
API endpoints for contract upload, analysis, and results retrieval
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import os
import uuid
import asyncio
from pathlib import Path
import logging

from config import settings
from agents.contract_agent import ContractAnalysisOrchestrator
from storage import get_analysis_store, store_analysis

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize orchestrator
orchestrator = ContractAnalysisOrchestrator()

@router.post("/analyze-contract", summary="Analyze a contract for risks")
async def analyze_contract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Contract file (PDF, DOCX, or TXT)")
) -> Dict[str, Any]:
    """
    Upload and analyze a contract file for legal risks and compliance issues.
    
    This endpoint starts a multi-agent analysis workflow that:
    1. Parses the document
    2. Extracts individual clauses
    3. Analyzes each clause for risks
    4. Checks compliance with essential clauses
    5. Generates a "Before You Sign" report
    
    Args:
        file: Contract file to analyze (PDF, DOCX, or TXT format)
        
    Returns:
        Analysis ID for tracking progress and retrieving results
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not allowed. Allowed types: {settings.allowed_extensions}"
            )
        
        # Check file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_filename = f"{analysis_id}_{file.filename}"
        file_path = os.path.join(settings.upload_dir, upload_filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Initialize analysis status
        analysis_store = get_analysis_store()
        analysis_store[analysis_id] = {
            "analysis_id": analysis_id,
            "filename": file.filename,
            "file_path": file_path,
            "status": "processing",
            "progress": {
                "document_parsing": False,
                "clause_extraction": False,
                "risk_analysis": False,
                "compliance_checking": False,
                "report_generation": False
            },
            "current_step": "Starting analysis...",
            "results": None,
            "error": None,
            "created_at": str(asyncio.get_event_loop().time())
        }
        
        # Start analysis in background
        background_tasks.add_task(run_contract_analysis, analysis_id, file_path)
        
        logger.info(f"Started contract analysis for {file.filename} with ID: {analysis_id}")
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "message": "Contract analysis started successfully",
            "estimated_time": "5-10 minutes",
            "status_url": f"/api/analysis-status/{analysis_id}",
            "results_url": f"/api/analysis-results/{analysis_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting contract analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@router.get("/analysis-status/{analysis_id}", summary="Get analysis status")
async def get_analysis_status(analysis_id: str) -> Dict[str, Any]:
    """
    Get the current status and progress of a contract analysis.
    
    Args:
        analysis_id: Unique identifier for the analysis
        
    Returns:
        Current analysis status and progress information
    """
    try:
        analysis_store = get_analysis_store()
        if analysis_id not in analysis_store:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = analysis_store[analysis_id]
        
        # Calculate overall progress percentage
        progress_values = analysis["progress"].values()
        progress_percentage = sum(1 for completed in progress_values if completed) / len(progress_values) * 100
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "filename": analysis["filename"],
            "status": analysis["status"],
            "current_step": analysis["current_step"],
            "progress_percentage": round(progress_percentage, 1),
            "detailed_progress": analysis["progress"],
            "error": analysis["error"],
            "created_at": analysis["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/analysis-results/{analysis_id}", summary="Get analysis results")
async def get_analysis_results(analysis_id: str) -> Dict[str, Any]:
    """
    Get the complete results of a contract analysis.
    
    Args:
        analysis_id: Unique identifier for the analysis
        
    Returns:
        Complete analysis results including risk assessment and recommendations
    """
    try:
        analysis_store = get_analysis_store()
        if analysis_id not in analysis_store:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = analysis_store[analysis_id]
        
        if analysis["status"] == "processing":
            return {
                "success": False,
                "message": "Analysis still in progress",
                "status": analysis["status"],
                "current_step": analysis["current_step"],
                "progress": analysis["progress"]
            }
        
        if analysis["status"] == "failed":
            return {
                "success": False,
                "message": "Analysis failed",
                "error": analysis["error"],
                "status": analysis["status"]
            }
        
        # Return complete results
        return {
            "success": True,
            "analysis_id": analysis_id,
            "filename": analysis["filename"],
            "status": analysis["status"],
            "results": analysis["results"],
            "completed_at": analysis.get("completed_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@router.get("/analysis-summary/{analysis_id}", summary="Get analysis summary")
async def get_analysis_summary(analysis_id: str) -> Dict[str, Any]:
    """
    Get a summary of the analysis results (key metrics and recommendations).
    
    Args:
        analysis_id: Unique identifier for the analysis
        
    Returns:
        Summary of analysis results with key metrics
    """
    try:
        analysis_store = get_analysis_store()
        if analysis_id not in analysis_store:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = analysis_store[analysis_id]
        
        if analysis["status"] != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        results = analysis["results"]
        
        # Extract key metrics
        document_info = results.get("document_parsed", {})
        clauses_info = results.get("clauses_extracted", {})
        risks_info = results.get("risks_analyzed", {})
        compliance_info = results.get("compliance_checked", {})
        report_info = results.get("report_generated", {})
        
        # Calculate summary metrics
        word_count = document_info.get("word_count", 0)
        clause_count = clauses_info.get("total_clauses", 0)
        risk_analyses = risks_info.get("analyses", [])
        high_risk_count = sum(1 for r in risk_analyses if r.get("risk_level") == "High")
        medium_risk_count = sum(1 for r in risk_analyses if r.get("risk_level") == "Medium")
        compliance_score = compliance_info.get("compliance_analysis", {}).get("overall_score", 0)
        
        # Extract report summary
        report_summary = report_info.get("before_sign_report", {})
        executive_summary = report_summary.get("executive_summary", {})
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "filename": analysis["filename"],
            "summary_metrics": {
                "document_metrics": {
                    "word_count": word_count,
                    "page_count": document_info.get("page_count", 0),
                    "file_type": document_info.get("file_type", "unknown")
                },
                "clause_metrics": {
                    "total_clauses": clause_count,
                    "clauses_analyzed": len(risk_analyses)
                },
                "risk_metrics": {
                    "high_risk_clauses": high_risk_count,
                    "medium_risk_clauses": medium_risk_count,
                    "low_risk_clauses": len(risk_analyses) - high_risk_count - medium_risk_count
                },
                "compliance_metrics": {
                    "overall_score": compliance_score,
                    "grade": compliance_info.get("compliance_analysis", {}).get("compliance_grade", "F")
                }
            },
            "key_recommendations": {
                "overall_risk_level": executive_summary.get("overall_risk_level", "Unknown"),
                "recommended_action": executive_summary.get("recommended_action", "Legal Review"),
                "key_takeaway": executive_summary.get("key_takeaway", "Analysis completed"),
                "top_risks_count": len(report_summary.get("top_risky_clauses", []))
            },
            "quick_actions": report_summary.get("quick_recommendations", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.delete("/analysis/{analysis_id}", summary="Delete analysis")
async def delete_analysis(analysis_id: str) -> Dict[str, Any]:
    """
    Delete an analysis and its associated files.
    
    Args:
        analysis_id: Unique identifier for the analysis
        
    Returns:
        Deletion confirmation
    """
    try:
        analysis_store = get_analysis_store()
        if analysis_id not in analysis_store:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = analysis_store[analysis_id]
        
        # Delete uploaded file
        file_path = analysis.get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to delete file {file_path}: {str(e)}")
        
        # Remove from store
        del analysis_store[analysis_id]
        
        logger.info(f"Deleted analysis {analysis_id}")
        
        return {
            "success": True,
            "message": "Analysis deleted successfully",
            "analysis_id": analysis_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete analysis: {str(e)}")


@router.get("/analyses", summary="List all analyses")
async def list_analyses() -> Dict[str, Any]:
    """
    List all contract analyses.
    
    Returns:
        List of all analyses with basic information
    """
    try:
        analyses_list = []
        
        for analysis_id, analysis in analysis_store.items():
            analyses_list.append({
                "analysis_id": analysis_id,
                "filename": analysis["filename"],
                "status": analysis["status"],
                "created_at": analysis["created_at"],
                "completed_at": analysis.get("completed_at"),
                "progress_percentage": sum(1 for completed in analysis["progress"].values() if completed) / len(analysis["progress"]) * 100
            })
        
        # Sort by creation time (newest first)
        analyses_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "total_analyses": len(analyses_list),
            "analyses": analyses_list
        }
        
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list analyses: {str(e)}")


# Background task function
async def run_contract_analysis(analysis_id: str, file_path: str):
    """Background task to run the contract analysis workflow"""
    try:
        # Update status
        analysis_store = get_analysis_store()
        if analysis_id in analysis_store:
            analysis_store[analysis_id]["status"] = "processing"
            analysis_store[analysis_id]["current_step"] = "Initializing analysis..."
        
        # Run analysis
        result = await orchestrator.analyze_contract(file_path)
        
        # Update store with results
        analysis_store = get_analysis_store()
        if analysis_id in analysis_store:
            if result.get("success", False):
                analysis_store[analysis_id].update({
                    "status": "completed",
                    "results": result["results"],
                    "progress": result["progress"],
                    "current_step": "Analysis completed successfully",
                    "completed_at": str(asyncio.get_event_loop().time())
                })
            else:
                analysis_store[analysis_id].update({
                    "status": "failed",
                    "error": result.get("error", "Unknown error"),
                    "current_step": "Analysis failed"
                })
        
        logger.info(f"Completed contract analysis {analysis_id} with status: {analysis_store[analysis_id]['status']}")
        
    except Exception as e:
        logger.error(f"Error in background analysis {analysis_id}: {str(e)}")
        
        # Update store with error
        analysis_store = get_analysis_store()
        if analysis_id in analysis_store:
            analysis_store[analysis_id].update({
                "status": "failed",
                "error": str(e),
                "current_step": "Analysis failed"
            })
