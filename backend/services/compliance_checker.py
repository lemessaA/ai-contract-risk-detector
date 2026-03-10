"""
Compliance Checker Service - Agent 4
Ensures essential clauses exist and checks regulatory compliance
"""
import json
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings

class ComplianceCheckerAgent:
    """Agent responsible for checking contract compliance and essential clauses"""
    
    def __init__(self):
        """Initialize the compliance checker agent"""
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
        self.system_prompt = """
You are an AI legal compliance specialist with expertise in contract requirements and regulatory compliance. Your task is to analyze contracts for essential clauses and compliance issues.

Essential Clauses to Check:
1. **Payment Terms** - Clear payment schedules, amounts, and methods
2. **Termination Clause** - Conditions and procedures for ending the contract
3. **Liability Limitation** - Limits on liability and damages
4. **Confidentiality** - Protection of sensitive information
5. **Governing Law** - Jurisdiction and applicable laws
6. **Dispute Resolution** - Methods for resolving conflicts
7. **Force Majeure** - Protection against unforeseeable events
8. **Intellectual Property** - Ownership and usage rights
9. **Indemnification** - Protection against third-party claims
10. **Warranties** - Guarantees and representations

Compliance Areas to Check:
- Data protection (GDPR, CCPA, etc.)
- Consumer protection laws
- Employment regulations
- Industry-specific regulations
- Antitrust and competition laws
- International trade compliance

Instructions:
1. Review all provided clauses systematically
2. Identify which essential clauses are present or missing
3. Assess the quality and completeness of existing clauses
4. Flag potential compliance issues
5. Provide specific recommendations for improvements
6. Rate overall compliance score (0-100)

Return the analysis in this exact JSON format:
{
    "success": true,
    "compliance_analysis": {
        "overall_score": 0-100,
        "compliance_grade": "A/B/C/D/F",
        "essential_clauses": {
            "present": [
                {
                    "clause_type": "Payment Terms",
                    "found_in": "clause_id_or_name",
                    "adequacy": "Adequate/Partial/Inadequate",
                    "assessment": "Brief assessment of quality"
                }
            ],
            "missing": [
                {
                    "clause_type": "Termination Clause",
                    "importance": "Critical/Important/Recommended",
                    "recommendation": "Specific recommendation for inclusion"
                }
            ]
        },
        "compliance_issues": [
            {
                "issue_type": "Data Protection/Consumer Protection/etc.",
                "severity": "High/Medium/Low",
                "description": "Clear description of the issue",
                "regulation": "Applicable law or regulation",
                "recommendation": "Specific fix recommendation"
            }
        ],
        "risk_factors": [
            {
                "factor": "Description of risk factor",
                "impact": "High/Medium/Low",
                "mitigation": "Mitigation strategy"
            }
        ],
        "recommendations": [
            "Specific recommendation 1",
            "Specific recommendation 2"
        ],
        "next_steps": [
            "Immediate action needed",
            "Legal review recommended",
            "Negotiation points"
        ]
    }
}

If the contract appears complete and compliant, return:
{
    "success": true,
    "compliance_analysis": {
        "overall_score": 85-100,
        "compliance_grade": "A",
        "essential_clauses": {
            "present": [...],
            "missing": []
        },
        "compliance_issues": [],
        "risk_factors": [],
        "recommendations": ["Minor improvements suggested"],
        "next_steps": ["Ready for execution"]
    }
}
"""
    
    async def check_compliance(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check contract compliance and essential clauses
        
        Args:
            clauses: List of clause dictionaries from clause extraction
            
        Returns:
            Dictionary containing compliance analysis
        """
        try:
            # Prepare clauses text for analysis
            clauses_summary = self._prepare_clauses_summary(clauses)
            
            # Prepare the message for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
Please analyze the following contract for compliance and essential clauses:

Contract Clauses Summary:
{clauses_summary}

Provide a comprehensive compliance analysis following the specified JSON format.
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
                
                if result.get("success", False) and "compliance_analysis" in result:
                    analysis = result["compliance_analysis"]
                    
                    # Validate and ensure all required fields exist
                    validated_analysis = {
                        "overall_score": analysis.get("overall_score", 0),
                        "compliance_grade": analysis.get("compliance_grade", "F"),
                        "essential_clauses": {
                            "present": analysis.get("essential_clauses", {}).get("present", []),
                            "missing": analysis.get("essential_clauses", {}).get("missing", [])
                        },
                        "compliance_issues": analysis.get("compliance_issues", []),
                        "risk_factors": analysis.get("risk_factors", []),
                        "recommendations": analysis.get("recommendations", []),
                        "next_steps": analysis.get("next_steps", [])
                    }
                    
                    result["compliance_analysis"] = validated_analysis
                    return result
                else:
                    # Fallback to basic compliance check
                    return self._fallback_compliance_check(clauses, result.get("error", "Unknown error"))
                    
            except json.JSONDecodeError as e:
                return self._fallback_compliance_check(clauses, f"JSON parsing error: {str(e)}")
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Compliance check failed: {str(e)}",
                "compliance_analysis": {}
            }
    
    def _prepare_clauses_summary(self, clauses: List[Dict[str, Any]]) -> str:
        """Prepare a summary of all clauses for analysis"""
        summary = f"Total Clauses: {len(clauses)}\n\n"
        
        for i, clause in enumerate(clauses, 1):
            clause_id = clause.get("clause_id", f"clause_{i}")
            clause_name = clause.get("clause_name", f"Clause {i}")
            clause_type = clause.get("clause_type", "General")
            clause_text = clause.get("clause_text", "")[:500]  # Limit text length
            
            summary += f"{i}. {clause_name} (ID: {clause_id})\n"
            summary += f"   Type: {clause_type}\n"
            summary += f"   Text: {clause_text}...\n\n"
        
        return summary
    
    def _fallback_compliance_check(self, clauses: List[Dict[str, Any]], error_message: str) -> Dict[str, Any]:
        """
        Fallback method for basic compliance checking when LLM fails
        
        Args:
            clauses: List of clause dictionaries
            error_message: Error message from LLM processing
            
        Returns:
            Dictionary with basic compliance analysis
        """
        # Essential clause keywords for basic detection
        essential_clause_patterns = {
            "Payment Terms": ["payment", "fee", "cost", "invoice", "billing"],
            "Termination Clause": ["terminate", "termination", "end", "cancel"],
            "Liability Limitation": ["liability", "limit", "damage", "responsibility"],
            "Confidentiality": ["confidential", "proprietary", "trade secret", "non-disclosure"],
            "Governing Law": ["governing law", "jurisdiction", "applicable law"],
            "Dispute Resolution": ["dispute", "arbitration", "mediation", "litigation"],
            "Force Majeure": ["force majeure", "act of god", "unforeseeable"],
            "Intellectual Property": ["intellectual property", "copyright", "trademark", "patent"],
            "Indemnification": ["indemnify", "indemnification", "hold harmless"],
            "Warranties": ["warranty", "guarantee", "represent", "warrant"]
        }
        
        present_clauses = []
        missing_clauses = []
        total_score = 0
        
        all_clause_text = " ".join([clause.get("clause_text", "").lower() for clause in clauses])
        
        for clause_type, keywords in essential_clause_patterns.items():
            found = any(keyword in all_clause_text for keyword in keywords)
            
            if found:
                present_clauses.append({
                    "clause_type": clause_type,
                    "found_in": "detected in contract",
                    "adequacy": "Partial",
                    "assessment": f"Detected keywords: {', '.join([k for k in keywords if k in all_clause_text])}"
                })
                total_score += 10
            else:
                importance = "Critical" if clause_type in ["Payment Terms", "Termination Clause", "Liability Limitation"] else "Important"
                missing_clauses.append({
                    "clause_type": clause_type,
                    "importance": importance,
                    "recommendation": f"Consider adding a {clause_type} clause"
                })
        
        # Calculate overall score and grade
        overall_score = min(total_score, 100)
        if overall_score >= 80:
            grade = "A"
        elif overall_score >= 60:
            grade = "B"
        elif overall_score >= 40:
            grade = "C"
        elif overall_score >= 20:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "success": True,
            "compliance_analysis": {
                "overall_score": overall_score,
                "compliance_grade": grade,
                "essential_clauses": {
                    "present": present_clauses,
                    "missing": missing_clauses
                },
                "compliance_issues": [],
                "risk_factors": [
                    {
                        "factor": "Limited analysis due to processing error",
                        "impact": "Medium",
                        "mitigation": "Manual legal review recommended"
                    }
                ],
                "recommendations": [
                    "Comprehensive legal review recommended",
                    "Consider adding missing essential clauses"
                ],
                "next_steps": [
                    "Review with legal counsel",
                    "Negotiate missing clauses"
                ],
                "warning": f"Used fallback compliance check due to: {error_message}"
            }
        }
