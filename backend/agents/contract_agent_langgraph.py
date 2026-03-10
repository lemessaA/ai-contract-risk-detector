"""
Multi-Agent Contract Analysis Orchestrator
Uses LangGraph to coordinate multiple AI agents for comprehensive contract analysis
"""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import asyncio
import json
from dataclasses import dataclass, field
from typing_extensions import Annotated, TypedDict

from services.document_parser import DocumentParserAgent
from services.clause_extractor import ClauseExtractorAgent
from services.risk_analyzer import RiskAnalyzerAgent
from services.compliance_checker import ComplianceCheckerAgent
from services.before_sign_report import BeforeSignReportAgent


class ContractAnalysisState(TypedDict):
    """State for the contract analysis workflow"""
    messages: Annotated[List[BaseMessage], add_messages]
    file_path: str
    document_parsed: Optional[Dict[str, Any]]
    clauses_extracted: Optional[Dict[str, Any]]
    risks_analyzed: Optional[Dict[str, Any]]
    compliance_checked: Optional[Dict[str, Any]]
    report_generated: Optional[Dict[str, Any]]
    current_step: str
    error: Optional[str]
    progress: Dict[str, bool]


class ContractAnalysisOrchestrator:
    """Multi-agent orchestrator for contract analysis using LangGraph"""
    
    def __init__(self):
        """Initialize the orchestrator with all agents"""
        self.document_parser = DocumentParserAgent()
        self.clause_extractor = ClauseExtractorAgent()
        self.risk_analyzer = RiskAnalyzerAgent()
        self.compliance_checker = ComplianceCheckerAgent()
        self.report_generator = BeforeSignReportAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for contract analysis"""
        
        # Create the graph
        workflow = StateGraph(ContractAnalysisState)
        
        # Add nodes for each agent
        workflow.add_node("parse_document", self._parse_document_node)
        workflow.add_node("extract_clauses", self._extract_clauses_node)
        workflow.add_node("analyze_risks", self._analyze_risks_node)
        workflow.add_node("check_compliance", self._check_compliance_node)
        workflow.add_node("generate_report", self._generate_report_node)
        
        # Define the flow
        workflow.set_entry_point("parse_document")
        
        # Normal flow
        workflow.add_edge("parse_document", "extract_clauses")
        workflow.add_edge("extract_clauses", "analyze_risks")
        workflow.add_edge("analyze_risks", "check_compliance")
        workflow.add_edge("check_compliance", "generate_report")
        workflow.add_edge("generate_report", END)
        
        return workflow.compile()
    
    async def _parse_document_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for document parsing"""
        try:
            # Parse the document
            result = await self.document_parser.parse_document(state["file_path"])
            
            if result.get("success", False):
                return {
                    **state,
                    "document_parsed": result,
                    "current_step": "Document parsed successfully",
                    "progress": {**state["progress"], "document_parsing": True},
                    "messages": state["messages"] + [AIMessage(content=f"✅ Document parsed successfully. Extracted {result.get('word_count', 0)} words.")]
                }
            else:
                return {
                    **state,
                    "error": result.get("error", "Document parsing failed"),
                    "messages": state["messages"] + [AIMessage(content=f"❌ Document parsing failed: {result.get('error', 'Unknown error')}")]
                }
            
        except Exception as e:
            return {
                **state,
                "error": f"Document parsing error: {str(e)}",
                "messages": state["messages"] + [AIMessage(content=f"❌ Document parsing error: {str(e)}")]
            }
    
    async def _extract_clauses_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for clause extraction"""
        try:
            if not state.get("document_parsed"):
                return {
                    **state,
                    "error": "No document parsed to extract clauses from",
                    "messages": state["messages"] + [AIMessage(content="❌ No document parsed to extract clauses from")]
                }
            
            contract_text = state["document_parsed"].get("text", "")
            result = await self.clause_extractor.extract_clauses(contract_text)
            
            if result.get("success", False):
                clauses = result.get("clauses", [])
                return {
                    **state,
                    "clauses_extracted": result,
                    "current_step": f"Extracted {len(clauses)} clauses",
                    "progress": {**state["progress"], "clause_extraction": True},
                    "messages": state["messages"] + [AIMessage(content=f"✅ Successfully extracted {len(clauses)} clauses from the contract.")]
                }
            else:
                return {
                    **state,
                    "error": result.get("error", "Clause extraction failed"),
                    "messages": state["messages"] + [AIMessage(content=f"❌ Clause extraction failed: {result.get('error', 'Unknown error')}")]
                }
            
        except Exception as e:
            return {
                **state,
                "error": f"Clause extraction error: {str(e)}",
                "messages": state["messages"] + [AIMessage(content=f"❌ Clause extraction error: {str(e)}")]
            }
    
    async def _analyze_risks_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for risk analysis"""
        try:
            if not state.get("clauses_extracted"):
                return {
                    **state,
                    "error": "No clauses extracted to analyze risks",
                    "messages": state["messages"] + [AIMessage(content="❌ No clauses extracted to analyze risks")]
                }
            
            clauses = state["clauses_extracted"].get("clauses", [])
            risk_results = []
            
            # Analyze each clause for risks
            for clause in clauses:
                result = await self.risk_analyzer.analyze_risk(clause)
                if result.get("success", False):
                    risk_results.append(result.get("clause_analysis", {}))
            
            if risk_results:
                return {
                    **state,
                    "risks_analyzed": {"success": True, "risk_analyses": risk_results},
                    "current_step": f"Analyzed risks for {len(risk_results)} clauses",
                    "progress": {**state["progress"], "risk_analysis": True},
                    "messages": state["messages"] + [AIMessage(content=f"✅ Risk analysis completed for {len(risk_results)} clauses.")]
                }
            else:
                return {
                    **state,
                    "error": "No risk analyses completed",
                    "messages": state["messages"] + [AIMessage(content="❌ No risk analyses were completed")]
                }
            
        except Exception as e:
            return {
                **state,
                "error": f"Risk analysis error: {str(e)}",
                "messages": state["messages"] + [AIMessage(content=f"❌ Risk analysis error: {str(e)}")]
            }
    
    async def _check_compliance_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for compliance checking"""
        try:
            if not state.get("clauses_extracted"):
                return {
                    **state,
                    "error": "No clauses extracted to check compliance",
                    "messages": state["messages"] + [AIMessage(content="❌ No clauses extracted to check compliance")]
                }
            
            clauses = state["clauses_extracted"].get("clauses", [])
            result = await self.compliance_checker.check_compliance(clauses)
            
            if result.get("success", False):
                return {
                    **state,
                    "compliance_checked": result,
                    "current_step": "Compliance check completed",
                    "progress": {**state["progress"], "compliance_checking": True},
                    "messages": state["messages"] + [AIMessage(content="✅ Compliance checking completed successfully.")]
                }
            else:
                return {
                    **state,
                    "error": result.get("error", "Compliance check failed"),
                    "messages": state["messages"] + [AIMessage(content=f"❌ Compliance check failed: {result.get('error', 'Unknown error')}")]
                }
            
        except Exception as e:
            return {
                **state,
                "error": f"Compliance check error: {str(e)}",
                "messages": state["messages"] + [AIMessage(content=f"❌ Compliance check error: {str(e)}")]
            }
    
    async def _generate_report_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node for report generation"""
        try:
            if not state.get("risks_analyzed") or not state.get("compliance_checked"):
                return {
                    **state,
                    "error": "Missing risk analysis or compliance check for report generation",
                    "messages": state["messages"] + [AIMessage(content="❌ Missing required analysis for report generation")]
                }
            
            risk_analyses = state["risks_analyzed"].get("risk_analyses", [])
            compliance_result = state["compliance_checked"]
            
            result = await self.report_generator.generate_report(risk_analyses, compliance_result)
            
            if result.get("success", False):
                return {
                    **state,
                    "report_generated": result,
                    "current_step": "Before-sign report generated",
                    "progress": {**state["progress"], "report_generation": True},
                    "messages": state["messages"] + [AIMessage(content="✅ Before-sign report generated successfully.")]
                }
            else:
                return {
                    **state,
                    "error": result.get("error", "Report generation failed"),
                    "messages": state["messages"] + [AIMessage(content=f"❌ Report generation failed: {result.get('error', 'Unknown error')}")]
                }
            
        except Exception as e:
            return {
                **state,
                "error": f"Report generation error: {str(e)}",
                "messages": state["messages"] + [AIMessage(content=f"❌ Report generation error: {str(e)}")]
            }
    
    async def analyze_contract(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a contract file using the multi-agent workflow
        
        Args:
            file_path: Path to the contract file
            
        Returns:
            Dictionary containing the complete analysis results
        """
        try:
            # Initialize state as dictionary
            initial_state = {
                "messages": [HumanMessage(content=f"Starting contract analysis for: {file_path}")],
                "file_path": file_path,
                "document_parsed": None,
                "clauses_extracted": None,
                "risks_analyzed": None,
                "compliance_checked": None,
                "report_generated": None,
                "current_step": "Initializing...",
                "error": None,
                "progress": {
                    "document_parsing": False,
                    "clause_extraction": False,
                    "risk_analysis": False,
                    "compliance_checking": False,
                    "report_generation": False
                }
            }
            
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Prepare the result
            result = {
                "success": not bool(final_state.get("error")),
                "workflow_completed": all(final_state.get("progress", {}).values()),
                "file_path": file_path,
                "current_step": final_state.get("current_step", "Completed"),
                "error": final_state.get("error"),
                "progress": final_state.get("progress", {}),
                "messages": [msg.content for msg in final_state.get("messages", [])],
                "results": {
                    "document_parsed": final_state.get("document_parsed"),
                    "clauses_extracted": final_state.get("clauses_extracted"),
                    "risks_analyzed": final_state.get("risks_analyzed"),
                    "compliance_checked": final_state.get("compliance_checked"),
                    "report_generated": final_state.get("report_generated")
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "workflow_completed": False,
                "file_path": file_path,
                "current_step": "Initialization failed",
                "error": f"Workflow initialization error: {str(e)}",
                "progress": {},
                "messages": [f"Failed to start contract analysis: {str(e)}"],
                "results": {}
            }
    
    async def get_workflow_status(self, file_path: str) -> Dict[str, Any]:
        """
        Get the status of the workflow (for progress tracking)
        
        Args:
            file_path: Path to the contract file
            
        Returns:
            Dictionary containing workflow status information
        """
        # This would be implemented with actual workflow state tracking
        # For now, return a placeholder
        return {
            "file_path": file_path,
            "status": "ready",
            "progress": {
                "document_parsing": False,
                "clause_extraction": False,
                "risk_analysis": False,
                "compliance_checking": False,
                "report_generation": False
            }
        }
