"""
Version Comparison API Routes
Handles contract version comparison functionality
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import asyncio

from services.version_comparison import VersionComparisonAgent
from storage import get_analysis_store

router = APIRouter(prefix="/api", tags=["version-comparison"])

# Initialize agent
comparison_agent = VersionComparisonAgent()

@router.post("/version-comparison/compare-texts")
async def compare_contract_texts(
    original_text: str = Form(...),
    modified_text: str = Form(...),
    original_label: Optional[str] = Form("Original"),
    modified_label: Optional[str] = Form("Modified")
):
    """
    Compare two contract texts
    
    Args:
        original_text: Original contract text
        modified_text: Modified contract text
        original_label: Label for original version
        modified_label: Label for modified version
        
    Returns:
        Detailed comparison results
    """
    try:
        response = await comparison_agent.compare_versions(
            original_text, 
            modified_text, 
            (original_label, modified_label)
        )
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text comparison failed: {str(e)}")

@router.post("/version-comparison/compare-files")
async def compare_contract_files(
    original_file: UploadFile = File(...),
    modified_file: UploadFile = File(...),
    original_label: Optional[str] = Form("Original"),
    modified_label: Optional[str] = Form("Modified")
):
    """
    Compare two contract files
    
    Args:
        original_file: Original contract file
        modified_file: Modified contract file
        original_label: Label for original version
        modified_label: Label for modified version
        
    Returns:
        Detailed comparison results
    """
    try:
        # Read file contents
        original_content = await original_file.read()
        modified_content = await modified_file.read()
        
        # Decode text content with error handling
        try:
            original_text = original_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                original_text = original_content.decode('latin-1')
            except UnicodeDecodeError:
                original_text = original_content.decode('utf-8', errors='ignore')
        
        try:
            modified_text = modified_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                modified_text = modified_content.decode('latin-1')
            except UnicodeDecodeError:
                modified_text = modified_content.decode('utf-8', errors='ignore')
        
        # Compare versions
        response = await comparison_agent.compare_versions(
            original_text, 
            modified_text, 
            (original_label, modified_label)
        )
        
        # Add file information
        response["file_info"] = {
            "original_filename": original_file.filename,
            "modified_filename": modified_file.filename,
            "original_size": len(original_content),
            "modified_size": len(modified_content)
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File comparison failed: {str(e)}")

@router.post("/version-comparison/compare-analyses")
async def compare_contract_analyses(
    original_analysis: str = Form(...),
    modified_analysis: str = Form(...),
    original_label: Optional[str] = Form("Original"),
    modified_label: Optional[str] = Form("Modified")
):
    """
    Compare analysis results of two contract versions
    
    Args:
        original_analysis: Original contract analysis (JSON string)
        modified_analysis: Modified contract analysis (JSON string)
        original_label: Label for original version
        modified_label: Label for modified version
        
    Returns:
        Analysis comparison results
    """
    try:
        # Parse analysis JSON
        original_dict = json.loads(original_analysis)
        modified_dict = json.loads(modified_analysis)
        
        # Compare analyses
        response = await comparison_agent.compare_analyses(
            original_dict, 
            modified_dict, 
            (original_label, modified_label)
        )
        
        return JSONResponse(content=response)
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in analysis data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis comparison failed: {str(e)}")

@router.post("/version-comparison/compare-with-stored/{analysis_id}")
async def compare_with_stored_analysis(
    analysis_id: str,
    modified_text: str = Form(...),
    modified_label: Optional[str] = Form("Modified")
):
    """
    Compare new text with a stored analysis
    
    Args:
        analysis_id: ID of stored analysis
        modified_text: New contract text to compare
        modified_label: Label for new version
        
    Returns:
        Comparison results
    """
    try:
        # Get stored analysis (this would need access to the analysis store)
        # For now, return error indicating this needs implementation
        raise HTTPException(
            status_code=501, 
            detail="Comparison with stored analysis not yet implemented"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
