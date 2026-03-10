"""
Multi-Agent Contract Analysis Orchestrator
Uses LangGraph to coordinate multiple AI agents for comprehensive contract analysis
"""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
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
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Define the flow
        workflow.set_entry_point("parse_document")
        
        # Normal flow
        workflow.add_edge("parse_document", "extract_clauses")
        workflow.add_edge("extract_clauses", "analyze_risks")
        workflow.add_edge("analyze_risks", "check_compliance")
        workflow.add_edge("check_compliance", "generate_report")
        workflow.add_edge("generate_report", END)
        
        # Error handling flow
        workflow.add_conditional_edges(
            "parse_document",
            self._check_for_error,
            {
                "error": "handle_error",
                "continue": "extract_clauses"
            }
        )
        
        workflow.add_conditional_edges(
            "extract_clauses",
            self._check_for_error,
            {
                "error": "handle_error",
                "continue": "analyze_risks"
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_risks",
            self._check_for_error,
            {
                "error": "handle_error",
                "continue": "check_compliance"
            }
        )
        
        workflow.add_conditional_edges(
            "check_compliance",
            self._check_for_error,
            {
                "error": "handle_error",
                "continue": "generate_report"
            }
        )
        
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    async def _parse_document_node(self, state: ContractAnalysisState) -> ContractAnalysisState:
        """Node for document parsing"""
        try:
            # Create new state to avoid modification conflicts
            new_state = state.copy()
            new_state["current_step"] = "Parsing document..."
            new_state["progress"] = new_state["progress"].copy()
            new_state["progress"]["document_parsing"] = False
            
            # Parse the document
            result = await self.document_parser.parse_document(new_state["file_path"])
            
            if result.get("success", False):
                new_state["document_parsed"] = result
                new_state["progress"]["document_parsing"] = True
                new_state["messages"] = new_state["messages"] + [AIMessage(content=f"✅ Document parsed successfully. Extracted {result.get('word_count', 0)} words.")]
            else:
                new_state["error"] = result.get("error", "Document parsing failed")
                new_state["messages"] = new_state["messages"] + [AIMessage(content=f"❌ Document parsing failed: {new_state['error']}")]
            
            return new_state
            
        except Exception as e:
            new_state = state.copy()
            new_state["error"] = f"Document parsing error: {str(e)}"
            new_state["messages"] = new_state["messages"] + [AIMessage(content=f"❌ Document parsing error: {str(e)}")]
            return new_state
    
    async def _extract_clauses_node(self, state: ContractAnalysisState) -> ContractAnalysisState:
        """Node for clause extraction"""
        try:
            state["current_step"] = "Extracting clauses..."
            state["progress"]["clause_extraction"] = False
            
            if not state["document_parsed"]:
                state["error"] = "No document parsed to extract clauses from"
                return state
            
            contract_text = state["document_parsed"].get("text", "")
            result = await self.clause_extractor.extract_clauses(contract_text)
            
            if result.get("success", False):
                state["clauses_extracted"] = result
                state["progress"]["clause_extraction"] = True
                clause_count = result.get("total_clauses", 0)
                state["messages"].append(AIMessage(content=f"✅ Extracted {clause_count} clauses from the contract."))
            else:
                state["error"] = result.get("error", "Clause extraction failed")
                state["messages"].append(AIMessage(content=f"❌ Clause extraction failed: {state['error']}"))
            
            return state
            
        except Exception as e:
            state["error"] = f"Clause extraction error: {str(e)}"
            state["messages"].append(AIMessage(content=f"❌ Clause extraction error: {str(e)}"))
            return state
    
    async def _analyze_risks_node(self, state: ContractAnalysisState) -> ContractAnalysisState:
        """Node for risk analysis"""
        try:
            state["current_step"] = "Analyzing risks..."
            state["progress"]["risk_analysis"] = False
            
            if not state["clauses_extracted"]:
                state["error"] = "No clauses extracted to analyze"
                return state
            
            clauses = state["clauses_extracted"].get("clauses", [])
            result = await self.risk_analyzer.analyze_multiple_clauses(clauses)
            
            if result.get("success", False):
                state["risks_analyzed"] = result
                state["progress"]["risk_analysis"] = True
                analyzed_count = result.get("total_analyzed", 0)
                state["messages"].append(AIMessage(content=f"✅ Analyzed risks for {analyzed_count} clauses."))
            else:
                state["error"] = result.get("error", "Risk analysis failed")
                state["messages"].append(AIMessage(content=f"❌ Risk analysis failed: {state['error']}"))
            
            return state
            
        except Exception as e:
            state["error"] = f"Risk analysis error: {str(e)}"
            state["messages"].append(AIMessage(content=f"❌ Risk analysis error: {str(e)}"))
            return state
    
    async def _check_compliance_node(self, state: ContractAnalysisState) -> ContractAnalysisState:
        """Node for compliance checking"""
        try:
            state["current_step"] = "Checking compliance..."
            state["progress"]["compliance_checking"] = False
            
            if not state["clauses_extracted"]:
                state["error"] = "No clauses extracted to check compliance"
                return state
            
            clauses = state["clauses_extracted"].get("clauses", [])
            result = await self.compliance_checker.check_compliance(clauses)
            
            if result.get("success", False):
                state["compliance_checked"] = result
                state["progress"]["compliance_checking"] = True
                compliance_score = result.get("compliance_analysis", {}).get("overall_score", 0)
                state["messages"].append(AIMessage(content=f"✅ Compliance check completed. Score: {compliance_score}/100."))
            else:
                state["error"] = result.get("error", "Compliance check failed")
                state["messages"].append(AIMessage(content=f"❌ Compliance check failed: {state['error']}"))
            
            return state
            
        except Exception as e:
            state["error"] = f"Compliance check error: {str(e)}"
            state["messages"].append(AIMessage(content=f"❌ Compliance check error: {str(e)}"))
            return state
    
    async def _generate_report_node(self, state: ContractAnalysisState) -> ContractAnalysisState:
        """Node for report generation"""
        try:
            state["current_step"] = "Generating report..."
            state["progress"]["report_generation"] = False
            
            if not state["risks_analyzed"] or not state["compliance_checked"]:
                state["error"] = "Missing risk analysis or compliance check for report generation"
                return state
            
            risk_analyses = state["risks_analyzed"].get("analyses", [])
            compliance_analysis = state["compliance_checked"]
            
            result = await self.report_generator.generate_before_sign_report(risk_analyses, compliance_analysis)
            
            if result.get("success", False):
                state["report_generated"] = result
                state["progress"]["report_generation"] = True
                state["messages"].append(AIMessage(content="✅ Before-sign report generated successfully."))
            else:
                state["error"] = result.get("error", "Report generation failed")
                state["messages"].append(AIMessage(content=f"❌ Report generation failed: {state['error']}"))
            
            return state
            
        except Exception as e:
            state["error"] = f"Report generation error: {str(e)}"
            state["messages"].append(AIMessage(content=f"❌ Report generation error: {str(e)}"))
            return state
    
    async def _handle_error_node(self, state: ContractAnalysisState) -> ContractAnalysisState:
        """Node for error handling"""
        error_msg = state.get("error", "Unknown error occurred")
        state["messages"].append(AIMessage(content=f"🛑 Workflow stopped due to error: {error_msg}"))
        return state
    
    def _check_for_error(self, state: ContractAnalysisState) -> str:
        """Check if there's an error and decide next step"""
        if state.get("error"):
            return "error"
        return "continue"
    
    async def analyze_contract(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a contract file using the multi-agent workflow
        
        Args:
            file_path: Path to the contract file
            
        Returns:
            Dictionary containing the complete analysis results
        """
        try:
            # Initialize state
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
            },
            "current_step": "Ready to start",
            "estimated_time_remaining": "5-10 minutes"
        }
