"""
Clause Extractor Service - Agent 2
Splits contract text into individual clauses and returns structured JSON
"""
import json
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings

class ClauseExtractorAgent:
    """Agent responsible for extracting individual clauses from contract text"""
    
    def __init__(self):
        """Initialize the clause extractor agent"""
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
        self.system_prompt = """
You are an AI legal document analyst specializing in contract clause extraction.

Your task is to analyze the provided contract text and identify individual clauses. A clause is a distinct section or provision that addresses a specific topic, right, obligation, or condition.

Instructions:
1. Read through the entire contract text carefully
2. Identify and extract individual clauses based on:
   - Numbered sections (1., 2., etc.)
   - Lettered subsections (a., b., etc.)
   - Paragraph breaks that indicate topic changes
   - Common clause patterns (e.g., "Termination", "Payment", "Liability", etc.)
3. For each clause, provide:
   - A descriptive name/title
   - The full clause text
   - The clause type (e.g., Payment, Termination, Liability, Confidentiality, etc.)
   - Position in document (clause number/section)
4. Ensure each clause is complete and doesn't cut off mid-sentence
5. Ignore headers, footers, and page numbers

Return the result in this exact JSON format:
{
    "success": true,
    "total_clauses": number_of_clauses,
    "clauses": [
        {
            "clause_id": "unique_identifier",
            "clause_name": "Descriptive title of the clause",
            "clause_type": "Payment/Termination/Liability/etc.",
            "clause_text": "Full text of the clause",
            "position": "Section number or position",
            "word_count": number_of_words_in_clause
        }
    ]
}

If the text doesn't appear to be a contract or you cannot identify clear clauses, return:
{
    "success": false,
    "error": "Unable to identify clear contract clauses in the provided text"
}
"""
    
    async def extract_clauses(self, contract_text: str) -> Dict[str, Any]:
        """
        Extract individual clauses from contract text
        
        Args:
            contract_text: The full text of the contract
            
        Returns:
            Dictionary containing extracted clauses with metadata
        """
        try:
            # Prepare the message for LLM
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Please extract all clauses from the following contract text:\n\n{contract_text}")
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
                
                if result.get("success", False) and "clauses" in result:
                    # Validate clause structure
                    clauses = result["clauses"]
                    if not isinstance(clauses, list):
                        raise ValueError("Clauses field must be a list")
                    
                    # Add validation for each clause
                    validated_clauses = []
                    for i, clause in enumerate(clauses):
                        if not isinstance(clause, dict):
                            continue
                        
                        # Ensure required fields exist
                        validated_clause = {
                            "clause_id": clause.get("clause_id", f"clause_{i+1}"),
                            "clause_name": clause.get("clause_name", f"Clause {i+1}"),
                            "clause_type": clause.get("clause_type", "General"),
                            "clause_text": clause.get("clause_text", ""),
                            "position": clause.get("position", f"Section {i+1}"),
                            "word_count": clause.get("word_count", len(clause.get("clause_text", "").split()))
                        }
                        validated_clauses.append(validated_clause)
                    
                    result["clauses"] = validated_clauses
                    result["total_clauses"] = len(validated_clauses)
                    
                    return result
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Failed to extract clauses"),
                        "clauses": [],
                        "total_clauses": 0
                    }
                    
            except json.JSONDecodeError as e:
                # Try to extract clauses using basic text processing as fallback
                return self._fallback_extraction(contract_text, f"JSON parsing error: {str(e)}")
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Clause extraction failed: {str(e)}",
                "clauses": [],
                "total_clauses": 0
            }
    
    def _fallback_extraction(self, contract_text: str, error_message: str) -> Dict[str, Any]:
        """
        Fallback method for basic clause extraction when LLM fails
        
        Args:
            contract_text: The contract text to process
            error_message: Error message from LLM processing
            
        Returns:
            Dictionary with basic clause extraction
        """
        try:
            # Split by common delimiters
            import re
            
            # Try to split by numbered sections
            sections = re.split(r'\n\s*(\d+\.|\d+\.\s+)', contract_text)
            
            clauses = []
            if len(sections) > 1:
                # Reconstruct sections with their numbers
                for i in range(1, len(sections), 2):
                    if i + 1 < len(sections):
                        section_num = sections[i].strip()
                        section_text = sections[i + 1].strip()
                        
                        if len(section_text) > 20:  # Ignore very short sections
                            clauses.append({
                                "clause_id": f"clause_{len(clauses) + 1}",
                                "clause_name": f"Section {section_num}",
                                "clause_type": "General",
                                "clause_text": section_text,
                                "position": section_num,
                                "word_count": len(section_text.split())
                            })
            
            # If no numbered sections found, split by double newlines
            if not clauses:
                paragraphs = [p.strip() for p in contract_text.split('\n\n') if len(p.strip()) > 50]
                
                for i, paragraph in enumerate(paragraphs):
                    clauses.append({
                        "clause_id": f"clause_{i + 1}",
                        "clause_name": f"Paragraph {i + 1}",
                        "clause_type": "General",
                        "clause_text": paragraph,
                        "position": f"Paragraph {i + 1}",
                        "word_count": len(paragraph.split())
                    })
            
            return {
                "success": True,
                "total_clauses": len(clauses),
                "clauses": clauses,
                "warning": f"Used fallback extraction due to: {error_message}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback extraction also failed: {str(e)}",
                "clauses": [],
                "total_clauses": 0
            }
