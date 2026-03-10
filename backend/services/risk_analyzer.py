"""
Risk Analyzer Service - Agent 3
Analyzes each clause for potential legal risks and returns structured JSON
"""
import json
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings

class RiskAnalyzerAgent:
    """Agent responsible for analyzing legal risks in contract clauses"""
    
    def __init__(self):
        """Initialize the risk analyzer agent"""
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
        self.system_prompt = """
You are an AI legal risk analyst with expertise in contract law and risk assessment. Your task is to analyze contract clauses for potential legal risks.

Instructions:
1. Carefully read and understand each clause
2. Identify potential legal risks, liabilities, or unfavorable terms
3. Assess the risk level based on:
   - Potential financial impact
   - Legal exposure
   - Business operational impact
   - Regulatory compliance issues
   - Ambiguity or vagueness that could lead to disputes
4. Provide clear explanations in simple, business-friendly language
5. Suggest practical alternatives to mitigate identified risks

Risk Level Guidelines:
- HIGH: Significant financial exposure, major legal liability, regulatory violations, or terms that could severely impact business operations
- MEDIUM: Moderate financial exposure, potential legal disputes, or terms that could impact normal business operations
- LOW: Minor risks, standard business terms, or minimal exposure

Return the analysis in this exact JSON format:
{
    "success": true,
    "clause_analysis": {
        "clause_id": "matching_clause_id",
        "clause_name": "clause_title",
        "risk_level": "High/Medium/Low",
        "risk_score": 0-100,
        "risk_categories": ["financial", "legal", "operational", "compliance"],
        "explanation": "Clear explanation of the risks in simple language",
        "key_concerns": ["specific concern 1", "specific concern 2"],
        "suggested_alternative": "Specific alternative language or approach",
        "mitigation_steps": ["step 1", "step 2"],
        "precedent_cases": ["relevant case law if applicable"],
        "regulatory_references": ["relevant laws or regulations"]
    }
}

If no significant risks are found, return:
{
    "success": true,
    "clause_analysis": {
        "clause_id": "matching_clause_id",
        "clause_name": "clause_title",
        "risk_level": "Low",
        "risk_score": 0-20,
        "risk_categories": [],
        "explanation": "This clause appears to be standard with minimal risks",
        "key_concerns": [],
        "suggested_alternative": "No changes needed",
        "mitigation_steps": [],
        "precedent_cases": [],
        "regulatory_references": []
    }
}
"""
    
    async def analyze_clause_risk(self, clause: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single clause for legal risks
        
        Args:
            clause: Dictionary containing clause information
            
        Returns:
            Dictionary containing risk analysis
        """
        try:
            # Prepare clause information for analysis
            clause_text = clause.get("clause_text", "")
            clause_name = clause.get("clause_name", "Unknown Clause")
            clause_id = clause.get("clause_id", "unknown")
            
            if not clause_text.strip():
                return {
                    "success": False,
                    "error": "Empty clause text provided",
                    "clause_analysis": {}
                }
            
            # Prepare the message for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
Please analyze the following contract clause for legal risks:

Clause ID: {clause_id}
Clause Name: {clause_name}
Clause Text: {clause_text}

Provide a comprehensive risk analysis following the specified JSON format.
""")
            ]
            
            # Get response from LLM
            response = await self.llm.ainvoke(messages)
            result_text = response.content
            
            # Parse JSON response
            try:
                result = json.loads(result_text)
                
                # Validate response structure
                if not isinstance(result, dict):
                    raise ValueError("Response is not a valid JSON object")
                
                if result.get("success", False) and "clause_analysis" in result:
                    analysis = result["clause_analysis"]
                    
                    # Ensure the analysis matches the clause
                    analysis["clause_id"] = clause_id
                    analysis["clause_name"] = clause_name
                    
                    # Validate and set risk score
                    if "risk_score" not in analysis:
                        risk_level = analysis.get("risk_level", "Low")
                        analysis["risk_score"] = self._calculate_risk_score(risk_level)
                    
                    # Ensure all required fields exist
                    validated_analysis = {
                        "clause_id": analysis.get("clause_id", clause_id),
                        "clause_name": analysis.get("clause_name", clause_name),
                        "risk_level": analysis.get("risk_level", "Low"),
                        "risk_score": analysis.get("risk_score", 0),
                        "risk_categories": analysis.get("risk_categories", []),
                        "explanation": analysis.get("explanation", "No specific risks identified"),
                        "key_concerns": analysis.get("key_concerns", []),
                        "suggested_alternative": analysis.get("suggested_alternative", "No changes needed"),
                        "mitigation_steps": analysis.get("mitigation_steps", []),
                        "precedent_cases": analysis.get("precedent_cases", []),
                        "regulatory_references": analysis.get("regulatory_references", [])
                    }
                    
                    result["clause_analysis"] = validated_analysis
                    return result
                else:
                    # Fallback to basic analysis
                    return self._fallback_analysis(clause, result.get("error", "Unknown error"))
                    
            except json.JSONDecodeError as e:
                return self._fallback_analysis(clause, f"JSON parsing error: {str(e)}")
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Risk analysis failed: {str(e)}",
                "clause_analysis": {}
            }
    
    async def analyze_multiple_clauses(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze multiple clauses for risks
        
        Args:
            clauses: List of clause dictionaries
            
        Returns:
            Dictionary containing all clause analyses
        """
        try:
            analyses = []
            errors = []
            
            for clause in clauses:
                result = await self.analyze_clause_risk(clause)
                if result.get("success", False):
                    analyses.append(result["clause_analysis"])
                else:
                    errors.append({
                        "clause_id": clause.get("clause_id", "unknown"),
                        "error": result.get("error", "Unknown error")
                    })
            
            return {
                "success": True,
                "total_analyzed": len(analyses),
                "total_errors": len(errors),
                "analyses": analyses,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Batch analysis failed: {str(e)}",
                "analyses": [],
                "errors": []
            }
    
    def _calculate_risk_score(self, risk_level: str) -> int:
        """Calculate numeric risk score from risk level"""
        risk_scores = {
            "High": 80,
            "Medium": 50,
            "Low": 20
        }
        return risk_scores.get(risk_level, 20)
    
    def _fallback_analysis(self, clause: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """
        Fallback method for basic risk assessment when LLM fails
        
        Args:
            clause: Clause dictionary
            error_message: Error message from LLM processing
            
        Returns:
            Dictionary with basic risk analysis
        """
        clause_text = clause.get("clause_text", "").lower()
        clause_id = clause.get("clause_id", "unknown")
        clause_name = clause.get("clause_name", "Unknown Clause")
        
        # Basic keyword-based risk assessment
        high_risk_keywords = [
            "unlimited liability", "personal guarantee", "indemnify", "waive",
            "irrevocable", "perpetual", "exclusive", "sole discretion",
            "liquidated damages", "penalty", "forfeit", "terminate without cause"
        ]
        
        medium_risk_keywords = [
            "reasonable", "material breach", "confidential", "non-compete",
            "non-solicitation", "governing law", "jurisdiction", "arbitration"
        ]
        
        risk_score = 0
        risk_level = "Low"
        key_concerns = []
        
        # Check for high-risk keywords
        for keyword in high_risk_keywords:
            if keyword in clause_text:
                risk_score += 25
                key_concerns.append(f"Contains high-risk term: '{keyword}'")
        
        # Check for medium-risk keywords
        for keyword in medium_risk_keywords:
            if keyword in clause_text:
                risk_score += 10
                key_concerns.append(f"Contains medium-risk term: '{keyword}'")
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = "High"
        elif risk_score >= 25:
            risk_level = "Medium"
        
        return {
            "success": True,
            "clause_analysis": {
                "clause_id": clause_id,
                "clause_name": clause_name,
                "risk_level": risk_level,
                "risk_score": min(risk_score, 100),
                "risk_categories": ["keyword_analysis"],
                "explanation": f"Basic keyword-based analysis. {error_message}",
                "key_concerns": key_concerns,
                "suggested_alternative": "Review clause carefully with legal counsel",
                "mitigation_steps": ["Seek legal review", "Clarify ambiguous terms"],
                "precedent_cases": [],
                "regulatory_references": [],
                "warning": f"Used fallback analysis due to: {error_message}"
            }
        }
