"""
Multi-Agent Contract Analysis Orchestrator (Simplified)
Sequential execution without LangGraph for testing
"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import asyncio
import json

from services.document_parser import DocumentParserAgent
from services.clause_extractor import ClauseExtractorAgent
from services.risk_analyzer import RiskAnalyzerAgent
from services.compliance_checker import ComplianceCheckerAgent
from services.before_sign_report import BeforeSignReportAgent


class ContractAnalysisOrchestrator:
    """Multi-agent orchestrator for contract analysis using sequential execution"""
    
    def __init__(self):
        """Initialize the orchestrator with all agents"""
        self.document_parser = DocumentParserAgent()
        self.clause_extractor = ClauseExtractorAgent()
        self.risk_analyzer = RiskAnalyzerAgent()
        self.compliance_checker = ComplianceCheckerAgent()
        self.report_generator = BeforeSignReportAgent()
    
    async def analyze_contract(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a contract file using sequential multi-agent workflow
        
        Args:
            file_path: Path to the contract file
            
        Returns:
            Dictionary containing the complete analysis results
        """
        try:
            # Initialize progress tracking
            progress = {
                "document_parsing": False,
                "clause_extraction": False,
                "risk_analysis": False,
                "compliance_checking": False,
                "report_generation": False
            }
            
            messages = [HumanMessage(content=f"Starting contract analysis for: {file_path}")]
            current_step = "Initializing..."
            error = None
            results = {}
            
            # Step 1: Document Parsing
            try:
                current_step = "Parsing document..."
                messages.append(AIMessage(content="📄 Parsing document..."))
                
                parse_result = await self.document_parser.parse_document(file_path)
                
                if parse_result.get("success", False):
                    results["document_parsed"] = parse_result
                    progress["document_parsing"] = True
                    messages.append(AIMessage(content=f"✅ Document parsed successfully. Extracted {parse_result.get('word_count', 0)} words."))
                else:
                    error = parse_result.get("error", "Document parsing failed")
                    messages.append(AIMessage(content=f"❌ Document parsing failed: {error}"))
                    return self._create_error_result(file_path, error, messages, progress, current_step)
                    
            except Exception as e:
                error = f"Document parsing error: {str(e)}"
                messages.append(AIMessage(content=f"❌ {error}"))
                return self._create_error_result(file_path, error, messages, progress, current_step)
            
            # Step 2: Clause Extraction
            try:
                current_step = "Extracting clauses..."
                messages.append(AIMessage(content="🔍 Extracting clauses..."))
                
                contract_text = results["document_parsed"].get("text", "")
                extract_result = await self.clause_extractor.extract_clauses(contract_text)
                
                if extract_result.get("success", False):
                    results["clauses_extracted"] = extract_result
                    progress["clause_extraction"] = True
                    clauses = extract_result.get("clauses", [])
                    messages.append(AIMessage(content=f"✅ Successfully extracted {len(clauses)} clauses from the contract."))
                else:
                    error = extract_result.get("error", "Clause extraction failed")
                    messages.append(AIMessage(content=f"❌ Clause extraction failed: {error}"))
                    return self._create_error_result(file_path, error, messages, progress, current_step)
                    
            except Exception as e:
                error = f"Clause extraction error: {str(e)}"
                messages.append(AIMessage(content=f"❌ {error}"))
                return self._create_error_result(file_path, error, messages, progress, current_step)
            
            # Step 3: Risk Analysis
            try:
                current_step = "Analyzing risks..."
                messages.append(AIMessage(content="⚠️ Analyzing risks..."))
                
                clauses = results["clauses_extracted"].get("clauses", [])
                risk_results = []
                
                # Analyze each clause for risks
                for clause in clauses:
                    try:
                        risk_result = await self.risk_analyzer.analyze_clause_risk(clause)
                        if risk_result.get("success", False):
                            risk_results.append(risk_result.get("clause_analysis", {}))
                    except Exception as e:
                        messages.append(AIMessage(content=f"⚠️ Risk analysis failed for clause {clause.get('clause_id', 'Unknown')}: {str(e)}"))
                
                if risk_results:
                    results["risks_analyzed"] = {"success": True, "risk_analyses": risk_results}
                    progress["risk_analysis"] = True
                    messages.append(AIMessage(content=f"✅ Risk analysis completed for {len(risk_results)} clauses."))
                else:
                    error = "No risk analyses completed"
                    messages.append(AIMessage(content="❌ No risk analyses were completed"))
                    return self._create_error_result(file_path, error, messages, progress, current_step)
                    
            except Exception as e:
                error = f"Risk analysis error: {str(e)}"
                messages.append(AIMessage(content=f"❌ {error}"))
                return self._create_error_result(file_path, error, messages, progress, current_step)
            
            # Step 4: Compliance Checking
            try:
                current_step = "Checking compliance..."
                messages.append(AIMessage(content="📋 Checking compliance..."))
                
                clauses = results["clauses_extracted"].get("clauses", [])
                compliance_result = await self.compliance_checker.check_compliance(clauses)
                
                if compliance_result.get("success", False):
                    results["compliance_checked"] = compliance_result
                    progress["compliance_checking"] = True
                    messages.append(AIMessage(content="✅ Compliance checking completed successfully."))
                else:
                    error = compliance_result.get("error", "Compliance check failed")
                    messages.append(AIMessage(content=f"❌ Compliance check failed: {error}"))
                    return self._create_error_result(file_path, error, messages, progress, current_step)
                    
            except Exception as e:
                error = f"Compliance check error: {str(e)}"
                messages.append(AIMessage(content=f"❌ {error}"))
                return self._create_error_result(file_path, error, messages, progress, current_step)
            
            # Step 5: Report Generation
            try:
                current_step = "Generating report..."
                messages.append(AIMessage(content="📊 Generating before-sign report..."))
                
                risk_analyses = results["risks_analyzed"].get("risk_analyses", [])
                compliance_analysis = results["compliance_checked"]
                
                report_result = await self.report_generator.generate_before_sign_report(risk_analyses, compliance_analysis)
                
                if report_result.get("success", False):
                    results["report_generated"] = report_result
                    progress["report_generation"] = True
                    messages.append(AIMessage(content="✅ Before-sign report generated successfully."))
                else:
                    error = report_result.get("error", "Report generation failed")
                    messages.append(AIMessage(content=f"❌ Report generation failed: {error}"))
                    return self._create_error_result(file_path, error, messages, progress, current_step)
                    
            except Exception as e:
                error = f"Report generation error: {str(e)}"
                messages.append(AIMessage(content=f"❌ {error}"))
                return self._create_error_result(file_path, error, messages, progress, current_step)
            
            # Success - all steps completed
            current_step = "Analysis completed successfully"
            messages.append(AIMessage(content="🎉 Contract analysis completed successfully!"))
            
            return {
                "success": True,
                "workflow_completed": all(progress.values()),
                "file_path": file_path,
                "current_step": current_step,
                "error": None,
                "progress": progress,
                "messages": [msg.content for msg in messages],
                "results": results
            }
            
        except Exception as e:
            return self._create_error_result(file_path, f"Workflow initialization error: {str(e)}", [], {}, "Initialization failed")
    
    def _create_error_result(self, file_path: str, error: str, messages: List[str], progress: Dict[str, bool], current_step: str) -> Dict[str, Any]:
        """Create a standardized error result"""
        return {
            "success": False,
            "workflow_completed": False,
            "file_path": file_path,
            "current_step": current_step,
            "error": error,
            "progress": progress,
            "messages": messages,
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
