"""
Shared Storage Module
Common storage for analysis results across all API modules
"""
from typing import Dict, Any

# In-memory storage for analysis results (in production, use Redis or database)
analysis_store: Dict[str, Dict[str, Any]] = {}

def get_analysis_store() -> Dict[str, Dict[str, Any]]:
    """Get the shared analysis store"""
    return analysis_store

def store_analysis(analysis_id: str, analysis_data: Dict[str, Any]) -> None:
    """Store analysis data"""
    analysis_store[analysis_id] = analysis_data

def get_analysis(analysis_id: str) -> Dict[str, Any]:
    """Get analysis data by ID"""
    return analysis_store.get(analysis_id)

def delete_analysis(analysis_id: str) -> bool:
    """Delete analysis by ID"""
    if analysis_id in analysis_store:
        del analysis_store[analysis_id]
        return True
    return False
