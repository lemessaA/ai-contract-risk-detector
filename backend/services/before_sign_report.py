"""
Before Sign Report Service - Agent 5
Generates user-friendly "Before You Sign" report with top 3 risky clauses
"""
import json
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings

class BeforeSignReportAgent:
    """Agent responsible for generating user-friendly before-sign reports"""
    
    def __init__(self):
        """Initialize the before-sign report agent"""
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
        self.system_prompt = """
You are an AI legal advisor specializing in creating clear, actionable "Before You Sign" reports for business users. Your task is to analyze contract risks and create a user-friendly report highlighting the most critical issues.

Your report should:
1. Focus on the top 3 most risky clauses that require immediate attention
2. Use simple, business-friendly language (avoid legal jargon)
3. Provide clear explanations of risks in terms business users understand
4. Offer practical, actionable alternatives
5. Include a clear recommendation on whether to sign, negotiate, or seek legal help

Report Structure:
- Executive Summary: Brief overview of contract risk level
- Top 3 Risky Clauses: Detailed analysis of each
- Quick Recommendations: Actionable next steps
- Overall Recommendation: Sign/Negotiate/Legal Review

Risk Communication Guidelines:
- Use clear headings and bullet points
- Explain risks in terms of financial impact, business risk, or legal exposure
- Provide specific alternative language when possible
- Include urgency indicators (Immediate Attention, Recommended, Consider)

Return the report in this exact JSON format:
{
    "success": true,
    "before_sign_report": {
        "executive_summary": {
            "overall_risk_level": "High/Medium/Low",
            "risk_score": 0-100,
            "key_takeaway": "One-sentence summary of the main concern",
            "recommended_action": "Sign/Negotiate/Legal Review/Don't Sign"
        },
        "top_risky_clauses": [
            {
                "rank": 1,
                "clause_name": "Name of the clause",
                "risk_level": "High/Medium/Low",
                "urgency": "Immediate Attention/Recommended/Consider",
                "problem_explained": "Simple explanation of what's wrong",
                "business_impact": "How this affects your business",
                "suggested_fix": "Specific alternative language or approach",
                "negotiation_tips": "How to discuss this with the other party"
            }
        ],
        "quick_recommendations": [
            "Immediate action item 1",
            "Action item 2",
            "Follow-up item 3"
        ],
        "overall_recommendation": {
            "action": "Sign/Negotiate/Legal Review/Don't Sign",
            "reasoning": "Clear explanation of why this action is recommended",
            "timeline": "Immediate/Within 24 hours/Within 3 days/Within 1 week"
        },
        "red_flags": [
            "Critical issue 1",
            "Critical issue 2"
        ],
        "green_flags": [
            "Positive aspect 1",
            "Positive aspect 2"
        ]
    }
}

If the contract appears safe with minimal risks:
{
    "success": true,
    "before_sign_report": {
        "executive_summary": {
            "overall_risk_level": "Low",
            "risk_score": 0-30,
            "key_takeaway": "This contract appears standard with minimal risks",
            "recommended_action": "Sign"
        },
        "top_risky_clauses": [],
        "quick_recommendations": ["Review final terms", "Keep records"],
        "overall_recommendation": {
            "action": "Sign",
            "reasoning": "Contract terms are fair and standard",
            "timeline": "When ready"
        },
        "red_flags": [],
        "green_flags": ["Standard terms", "Clear obligations"]
    }
}
"""
    
    async def generate_before_sign_report(
        self, 
        risk_analyses: List[Dict[str, Any]], 
        compliance_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a user-friendly before-sign report
        
        Args:
            risk_analyses: List of risk analysis results from RiskAnalyzerAgent
            compliance_analysis: Compliance analysis results from ComplianceCheckerAgent
            
        Returns:
            Dictionary containing the before-sign report
        """
        try:
            # Prepare data for analysis
            analysis_summary = self._prepare_analysis_summary(risk_analyses, compliance_analysis)
            
            # Prepare the message for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"""
Please generate a "Before You Sign" report based on the following contract analysis:

Risk Analyses:
{analysis_summary['risk_summary']}

Compliance Analysis:
{analysis_summary['compliance_summary']}

Create a user-friendly report focusing on the top 3 most critical risks that a business user needs to understand before signing.
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
                
                if result.get("success", False) and "before_sign_report" in result:
                    report = result["before_sign_report"]
                    
                    # Validate and ensure all required fields exist
                    validated_report = {
                        "executive_summary": {
                            "overall_risk_level": report.get("executive_summary", {}).get("overall_risk_level", "Low"),
                            "risk_score": report.get("executive_summary", {}).get("risk_score", 0),
                            "key_takeaway": report.get("executive_summary", {}).get("key_takeaway", "Contract analysis completed"),
                            "recommended_action": report.get("executive_summary", {}).get("recommended_action", "Legal Review")
                        },
                        "top_risky_clauses": report.get("top_risky_clauses", []),
                        "quick_recommendations": report.get("quick_recommendations", []),
                        "overall_recommendation": {
                            "action": report.get("overall_recommendation", {}).get("action", "Legal Review"),
                            "reasoning": report.get("overall_recommendation", {}).get("reasoning", "Professional review recommended"),
                            "timeline": report.get("overall_recommendation", {}).get("timeline", "Within 24 hours")
                        },
                        "red_flags": report.get("red_flags", []),
                        "green_flags": report.get("green_flags", [])
                    }
                    
                    result["before_sign_report"] = validated_report
                    return result
                else:
                    # Fallback to basic report generation
                    return self._fallback_report_generation(risk_analyses, compliance_analysis, result.get("error", "Unknown error"))
                    
            except json.JSONDecodeError as e:
                return self._fallback_report_generation(risk_analyses, compliance_analysis, f"JSON parsing error: {str(e)}")
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Report generation failed: {str(e)}",
                "before_sign_report": {}
            }
    
    def _prepare_analysis_summary(self, risk_analyses: List[Dict[str, Any]], compliance_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Prepare summaries of risk and compliance analyses for LLM processing"""
        
        # Prepare risk summary
        risk_summary = f"Total clauses analyzed: {len(risk_analyses)}\n\n"
        
        for i, analysis in enumerate(risk_analyses, 1):
            clause_name = analysis.get("clause_name", f"Clause {i}")
            risk_level = analysis.get("risk_level", "Low")
            risk_score = analysis.get("risk_score", 0)
            explanation = analysis.get("explanation", "No explanation provided")
            suggested_alt = analysis.get("suggested_alternative", "No alternative suggested")
            
            risk_summary += f"{i}. {clause_name}\n"
            risk_summary += f"   Risk Level: {risk_level} (Score: {risk_score})\n"
            risk_summary += f"   Explanation: {explanation}\n"
            risk_summary += f"   Suggested Alternative: {suggested_alt}\n\n"
        
        # Prepare compliance summary
        compliance_score = compliance_analysis.get("compliance_analysis", {}).get("overall_score", 0)
        compliance_grade = compliance_analysis.get("compliance_analysis", {}).get("compliance_grade", "F")
        
        present_clauses = compliance_analysis.get("compliance_analysis", {}).get("essential_clauses", {}).get("present", [])
        missing_clauses = compliance_analysis.get("compliance_analysis", {}).get("essential_clauses", {}).get("missing", [])
        compliance_issues = compliance_analysis.get("compliance_analysis", {}).get("compliance_issues", [])
        
        compliance_summary = f"Overall Compliance Score: {compliance_score}/100 (Grade: {compliance_grade})\n\n"
        compliance_summary += f"Essential Clauses Present: {len(present_clauses)}\n"
        compliance_summary += f"Essential Clauses Missing: {len(missing_clauses)}\n"
        compliance_summary += f"Compliance Issues: {len(compliance_issues)}\n\n"
        
        if present_clauses:
            compliance_summary += "Present Essential Clauses:\n"
            for clause in present_clauses[:5]:  # Limit to first 5
                compliance_summary += f"- {clause.get('clause_type', 'Unknown')}: {clause.get('adequacy', 'Unknown adequacy')}\n"
        
        if missing_clauses:
            compliance_summary += "\nMissing Essential Clauses:\n"
            for clause in missing_clauses[:5]:  # Limit to first 5
                compliance_summary += f"- {clause.get('clause_type', 'Unknown')}: {clause.get('importance', 'Unknown importance')}\n"
        
        return {
            "risk_summary": risk_summary,
            "compliance_summary": compliance_summary
        }
    
    def _fallback_report_generation(
        self, 
        risk_analyses: List[Dict[str, Any]], 
        compliance_analysis: Dict[str, Any], 
        error_message: str
    ) -> Dict[str, Any]:
        """
        Fallback method for basic report generation when LLM fails
        
        Args:
            risk_analyses: List of risk analysis results
            compliance_analysis: Compliance analysis results
            error_message: Error message from LLM processing
            
        Returns:
            Dictionary with basic before-sign report
        """
        # Sort risk analyses by risk score (descending)
        sorted_risks = sorted(risk_analyses, key=lambda x: x.get("risk_score", 0), reverse=True)
        top_3_risks = sorted_risks[:3]
        
        # Calculate overall risk metrics
        total_risk_score = sum(analysis.get("risk_score", 0) for analysis in risk_analyses)
        avg_risk_score = total_risk_score / len(risk_analyses) if risk_analyses else 0
        high_risk_count = sum(1 for analysis in risk_analyses if analysis.get("risk_level") == "High")
        
        # Determine overall risk level
        if avg_risk_score >= 70 or high_risk_count >= 2:
            overall_risk_level = "High"
            recommended_action = "Legal Review"
        elif avg_risk_score >= 40 or high_risk_count >= 1:
            overall_risk_level = "Medium"
            recommended_action = "Negotiate"
        else:
            overall_risk_level = "Low"
            recommended_action = "Sign"
        
        # Generate top risky clauses
        top_risky_clauses = []
        for i, risk in enumerate(top_3_risks, 1):
            if risk.get("risk_score", 0) > 20:  # Only include if there's actual risk
                top_risky_clauses.append({
                    "rank": i,
                    "clause_name": risk.get("clause_name", f"Clause {i}"),
                    "risk_level": risk.get("risk_level", "Low"),
                    "urgency": "Immediate Attention" if risk.get("risk_level") == "High" else "Recommended",
                    "problem_explained": risk.get("explanation", "Risk identified"),
                    "business_impact": "Potential legal or financial impact",
                    "suggested_fix": risk.get("suggested_alternative", "Review and revise clause"),
                    "negotiation_tips": "Discuss with legal counsel before signing"
                })
        
        # Generate quick recommendations
        quick_recommendations = []
        if high_risk_count > 0:
            quick_recommendations.append(f"Address {high_risk_count} high-risk clause(s) immediately")
        if len(compliance_analysis.get("compliance_analysis", {}).get("essential_clauses", {}).get("missing", [])) > 0:
            quick_recommendations.append("Add missing essential clauses")
        quick_recommendations.append("Review all suggested alternatives")
        
        # Determine red flags and green flags
        red_flags = []
        green_flags = []
        
        if high_risk_count > 0:
            red_flags.append(f"{high_risk_count} high-risk clause(s) identified")
        
        compliance_score = compliance_analysis.get("compliance_analysis", {}).get("overall_score", 0)
        if compliance_score < 50:
            red_flags.append("Low compliance score")
        elif compliance_score > 80:
            green_flags.append("Good compliance score")
        
        if len(risk_analyses) > 0:
            green_flags.append("Contract structure analyzed")
        
        return {
            "success": True,
            "before_sign_report": {
                "executive_summary": {
                    "overall_risk_level": overall_risk_level,
                    "risk_score": int(avg_risk_score),
                    "key_takeaway": f"Contract has {high_risk_count} high-risk clauses and compliance score of {compliance_score}",
                    "recommended_action": recommended_action
                },
                "top_risky_clauses": top_risky_clauses,
                "quick_recommendations": quick_recommendations,
                "overall_recommendation": {
                    "action": recommended_action,
                    "reasoning": f"Based on {high_risk_count} high-risk clauses and compliance score of {compliance_score}",
                    "timeline": "Within 24 hours" if recommended_action != "Sign" else "When ready"
                },
                "red_flags": red_flags,
                "green_flags": green_flags,
                "warning": f"Used fallback report generation due to: {error_message}"
            }
        }
