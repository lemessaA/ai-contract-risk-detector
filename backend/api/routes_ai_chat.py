"""
AI Chat API Routes
Handles contract Q&A and chat functionality
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import asyncio

from services.ai_chat import AIChatAgent
from agents.contract_agent import ContractAnalysisOrchestrator
from storage import get_analysis_store

router = APIRouter(prefix="/api", tags=["ai-chat"])

# Initialize agents
ai_chat_agent = AIChatAgent()
contract_orchestrator = ContractAnalysisOrchestrator()

@router.post("/ai-chat/ask")
async def ask_about_contract(
    question: str = Form(...),
    analysis_id: Optional[str] = Form(None),
    contract_text: Optional[str] = Form(None)
):
    """
    Ask a question about a contract or its analysis
    
    Args:
        question: User's question
        analysis_id: Optional analysis ID to get context from
        contract_text: Optional contract text for context
        
    Returns:
        AI response to the question
    """
    try:
        # Get analysis results if analysis_id provided
        analysis_results = None
        if analysis_id:
            analysis_store = get_analysis_store()
            if analysis_id in analysis_store:
                analysis_results = analysis_store[analysis_id].get("results", {})
        
        # Get contract text from analysis if not provided
        if not contract_text and analysis_results:
            contract_text = analysis_results.get("document_parsed", {}).get("text", "")
        
        # Get AI response
        response = await ai_chat_agent.ask_about_contract(question, contract_text, analysis_results)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@router.post("/ai-chat/explain-clause")
async def explain_clause(
    clause_text: str = Form(...),
    clause_analysis: Optional[str] = Form(None)
):
    """
    Get detailed explanation of a specific clause
    
    Args:
        clause_text: The clause text to explain
        clause_analysis: Optional risk analysis for the clause
        
    Returns:
        Detailed explanation of the clause
    """
    try:
        # Parse clause analysis if provided
        analysis_dict = None
        if clause_analysis:
            analysis_dict = json.loads(clause_analysis)
        
        response = await ai_chat_agent.explain_clause(clause_text, analysis_dict)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to explain clause: {str(e)}")

@router.post("/ai-chat/suggest-improvements")
async def suggest_improvements(
    clause_text: str = Form(...),
    risk_analysis: str = Form(...)
):
    """
    Get improvement suggestions for a risky clause
    
    Args:
        clause_text: The clause text to improve
        risk_analysis: Risk analysis identifying issues
        
    Returns:
        Improvement suggestions for the clause
    """
    try:
        # Parse risk analysis
        analysis_dict = json.loads(risk_analysis)
        
        response = await ai_chat_agent.suggest_improvements(clause_text, analysis_dict)
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate improvements: {str(e)}")

@router.post("/ai-chat/chat-with-analysis/{analysis_id}")
async def chat_with_analysis(analysis_id: str, question: str = Form(...)):
    """
    Chat about a specific contract analysis
    
    Args:
        analysis_id: ID of the contract analysis
        question: User's question about the analysis
        
    Returns:
        Context-aware AI response
    """
    try:
        # Get analysis results
        analysis_store = get_analysis_store()
        if analysis_id not in analysis_store:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis_results = analysis_store[analysis_id].get("results", {})
        contract_text = analysis_results.get("document_parsed", {}).get("text", "")
        
        # Get AI response with full context
        response = await ai_chat_agent.ask_about_contract(question, contract_text, analysis_results)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")
