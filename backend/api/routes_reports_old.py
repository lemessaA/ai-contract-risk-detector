"""
Report Generation API Routes
Handles downloadable report generation
"""
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import asyncio

from services.report_generator import ReportGenerator
from storage import get_analysis_store

router = APIRouter(prefix="/api", tags=["reports"])

# Initialize report generator
report_generator = ReportGenerator()

@router.post("/reports/generate-pdf")
async def generate_pdf_report(
    analysis_id: str = Form(...),
    filename: Optional[str] = Form(None)
):
    """
    Generate PDF report from analysis results
    
    Args:
        analysis_id: ID of the contract analysis
        filename: Optional custom filename
        
    Returns:
        PDF report in base64 format
    """
    try:
        # Get analysis results
        if analysis_id not in analysis_store = get_analysis_store():
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_store = get_analysis_store()[analysis_id].get("results", {})
        
        # Generate PDF
        response = await report_generator.generate_pdf_report(analysis_results, filename)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/reports/generate-html")
async def generate_html_report(
    analysis_id: str = Form(...),
    filename: Optional[str] = Form(None)
):
    """
    Generate HTML report from analysis results
    
    Args:
        analysis_id: ID of the contract analysis
        filename: Optional custom filename
        
    Returns:
        HTML report in base64 format
    """
    try:
        # Get analysis results
        if analysis_id not in analysis_store = get_analysis_store():
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_store = get_analysis_store()[analysis_id].get("results", {})
        
        # Generate HTML
        response = await report_generator.generate_html_report(analysis_results, filename)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML generation failed: {str(e)}")

@router.post("/reports/generate-word")
async def generate_word_report(
    analysis_id: str = Form(...),
    filename: Optional[str] = Form(None)
):
    """
    Generate Word document report from analysis results
    
    Args:
        analysis_id: ID of the contract analysis
        filename: Optional custom filename
        
    Returns:
        Word document report in base64 format
    """
    try:
        # Get analysis results
        if analysis_id not in analysis_store = get_analysis_store():
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_store = get_analysis_store()[analysis_id].get("results", {})
        
        # Generate Word document
        response = await report_generator.generate_word_report(analysis_results, filename)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word document generation failed: {str(e)}")

@router.post("/reports/generate-json")
async def generate_json_report(
    analysis_id: str = Form(...),
    filename: Optional[str] = Form(None)
):
    """
    Generate JSON report from analysis results
    
    Args:
        analysis_id: ID of the contract analysis
        filename: Optional custom filename
        
    Returns:
        JSON report in base64 format
    """
    try:
        # Get analysis results
        if analysis_id not in analysis_store = get_analysis_store():
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_store = get_analysis_store()[analysis_id].get("results", {})
        
        # Generate JSON
        response = await report_generator.generate_json_report(analysis_results, filename)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON generation failed: {str(e)}")

@router.post("/reports/generate-all-formats")
async def generate_all_formats(
    analysis_id: str = Form(...),
    base_filename: Optional[str] = Form(None)
):
    """
    Generate reports in all available formats
    
    Args:
        analysis_id: ID of the contract analysis
        base_filename: Base filename for all reports
        
    Returns:
        All generated reports in different formats
    """
    try:
        # Get analysis results
        if analysis_id not in analysis_store = get_analysis_store():
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_store = get_analysis_store()[analysis_id].get("results", {})
        
        # Generate all formats concurrently
        pdf_task = report_generator.generate_pdf_report(analysis_results, f"{base_filename}.pdf" if base_filename else None)
        html_task = report_generator.generate_html_report(analysis_results, f"{base_filename}.html" if base_filename else None)
        json_task = report_generator.generate_json_report(analysis_results, f"{base_filename}.json" if base_filename else None)
        word_task = report_generator.generate_word_report(analysis_results, f"{base_filename}.rtf" if base_filename else None)
        
        # Wait for all to complete
        pdf_result, html_result, json_result, word_result = await asyncio.gather(
            pdf_task, html_task, json_task, word_task, 
            return_exceptions=True
        )
        
        # Compile results
        response = {
            "success": True,
            "analysis_id": analysis_id,
            "reports": {
                "pdf": pdf_result if not isinstance(pdf_result, Exception) else {"success": False, "error": str(pdf_result)},
                "html": html_result if not isinstance(html_result, Exception) else {"success": False, "error": str(html_result)},
                "json": json_result if not isinstance(json_result, Exception) else {"success": False, "error": str(json_result)},
                "word": word_result if not isinstance(word_result, Exception) else {"success": False, "error": str(word_result)}
            },
            "timestamp": analysis_results.get("timestamp", "")
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/reports/available-formats")
async def get_available_formats():
    """
    Get list of available report formats
    
    Returns:
        List of supported formats and their availability
    """
    try:
        formats = {
            "pdf": {
                "name": "PDF",
                "description": "Portable Document Format - Best for printing and sharing",
                "available": True,
                "mime_type": "application/pdf"
            },
            "html": {
                "name": "HTML",
                "description": "Web page format - Interactive and viewable in browsers",
                "available": True,
                "mime_type": "text/html"
            },
            "json": {
                "name": "JSON",
                "description": "Data format - For integration and analysis",
                "available": True,
                "mime_type": "application/json"
            },
            "word": {
                "name": "RTF (Word-compatible)",
                "description": "Rich Text Format - Compatible with Microsoft Word",
                "available": True,
                "mime_type": "application/rtf"
            }
        }
        
        return JSONResponse(content={
            "formats": formats,
            "total_formats": len(formats)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get formats: {str(e)}")
