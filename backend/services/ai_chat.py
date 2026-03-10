"""
AI Chat Service - Contract Q&A Assistant
Provides intelligent answers about contract content and analysis
"""
import json
from typing import Dict, Any, List, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings


class AIChatAgent:
    """AI agent for answering questions about contracts and analysis results"""
    
    def __init__(self):
        """Initialize the AI chat agent"""
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
    
    async def ask_about_contract(self, question: str, contract_text: str = None, analysis_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Answer a question about the contract or its analysis
        
        Args:
            question: User's question about the contract
            contract_text: Full contract text (optional)
            analysis_results: Complete analysis results (optional)
            
        Returns:
            Dictionary containing the AI response
        """
        try:
            # Build context from available information
            context_parts = []
            
            if contract_text:
                context_parts.append(f"CONTRACT TEXT:\n{contract_text[:2000]}...")
            
            if analysis_results:
                # Add analysis summary
                clauses = analysis_results.get("clauses_extracted", {}).get("clauses", [])
                risks = analysis_results.get("risks_analyzed", {}).get("risk_analyses", [])
                compliance = analysis_results.get("compliance_checked", {})
                
                context_parts.append(f"ANALYSIS SUMMARY:")
                context_parts.append(f"- Total clauses: {len(clauses)}")
                
                if risks:
                    high_risks = [r for r in risks if r.get("risk_level") == "High"]
                    context_parts.append(f"- High-risk clauses: {len(high_risks)}")
                
                if compliance:
                    context_parts.append(f"- Overall compliance: {compliance.get('overall_compliance', 'Unknown')}")
                    missing_clauses = compliance.get("missing_clauses", [])
                    if missing_clauses:
                        context_parts.append(f"- Missing essential clauses: {', '.join(missing_clauses)}")
            
            # Create system prompt
            system_prompt = """You are a helpful AI assistant specialized in contract analysis and legal document interpretation. 

Your role is to:
1. Answer questions about contract content accurately
2. Explain complex legal terms in simple language
3. Highlight potential risks or issues when relevant
4. Provide practical advice based on the contract analysis
5. Be clear, concise, and professional

Guidelines:
- Always base answers on the provided contract text and analysis
- If you don't know something, say so clearly
- For legal advice, recommend consulting a qualified attorney
- Use bullet points for complex explanations
- Be helpful and educational

Context information is provided below. Use it to answer the user's question accurately."""
            
            # Create human message with context and question
            human_message = f"""
{chr(10).join(context_parts)}

USER QUESTION: {question}

Please provide a helpful and accurate response based on the contract information above."""
            
            # Get response from LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_message)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "question": question,
                "answer": response.content,
                "context_used": bool(contract_text or analysis_results),
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "question": question,
                "error": f"Failed to get AI response: {str(e)}",
                "timestamp": self._get_timestamp()
            }
    
    async def explain_clause(self, clause_text: str, clause_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Provide detailed explanation of a specific clause
        
        Args:
            clause_text: The clause text to explain
            clause_analysis: Risk analysis for this clause (optional)
            
        Returns:
            Dictionary containing the explanation
        """
        try:
            system_prompt = """You are a legal document expert specializing in explaining contract clauses in clear, simple language.

Your task is to:
1. Explain what the clause means in plain English
2. Identify any potential risks or concerns
3. Explain the practical implications
4. Suggest improvements if needed

Structure your response with:
- **What it means**: Simple explanation
- **Key points**: Important details to note
- **Potential risks**: Any concerns to be aware of
- **Practical advice**: How this affects the parties"""
            
            context = f"CLAUSE TO EXPLAIN:\n{clause_text}"
            
            if clause_analysis:
                context += f"\n\nRISK ANALYSIS:\n"
                context += f"- Risk Level: {clause_analysis.get('risk_level', 'Unknown')}\n"
                context += f"- Risk Score: {clause_analysis.get('risk_score', 'Unknown')}\n"
                context += f"- Categories: {', '.join(clause_analysis.get('risk_categories', []))}\n"
                if clause_analysis.get('explanation'):
                    context += f"- Analysis: {clause_analysis['explanation']}"
            
            human_message = f"{context}\n\nPlease explain this clause clearly and thoroughly."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_message)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "clause_text": clause_text,
                "explanation": response.content,
                "analysis_summary": clause_analysis,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "clause_text": clause_text,
                "error": f"Failed to explain clause: {str(e)}",
                "timestamp": self._get_timestamp()
            }
    
    async def suggest_improvements(self, clause_text: str, risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest improvements for a risky clause
        
        Args:
            clause_text: The clause text to improve
            risk_analysis: Risk analysis identifying the issues
            
        Returns:
            Dictionary containing improvement suggestions
        """
        try:
            system_prompt = """You are a contract improvement specialist. Your task is to suggest specific improvements for contract clauses that have identified risks.

For each suggestion, provide:
1. **Current issue**: What's wrong with the current clause
2. **Suggested improvement**: Specific wording changes
3. **Why it helps**: How the improvement reduces risk
4. **Alternative options**: Different approaches if applicable

Focus on:
- Reducing ambiguity
- Adding protective language
- Clarifying obligations
- Balancing risk between parties
- Ensuring enforceability"""
            
            context = f"RISKY CLAUSE:\n{clause_text}\n\n"
            context += f"RISK ANALYSIS:\n"
            context += f"- Risk Level: {risk_analysis.get('risk_level', 'Unknown')}\n"
            context += f"- Risk Score: {risk_analysis.get('risk_score', 'Unknown')}\n"
            context += f"- Risk Categories: {', '.join(risk_analysis.get('risk_categories', []))}\n"
            if risk_analysis.get('explanation'):
                context += f"- Risk Explanation: {risk_analysis['explanation']}\n"
            
            human_message = f"{context}\n\nPlease suggest specific improvements to make this clause safer and clearer."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_message)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "success": True,
                "clause_text": clause_text,
                "risk_analysis": risk_analysis,
                "improvement_suggestions": response.content,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "clause_text": clause_text,
                "error": f"Failed to generate improvements: {str(e)}",
                "timestamp": self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
