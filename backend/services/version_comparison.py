"""
Version Comparison Service
Compares different versions of contracts and highlights changes
"""
import json
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher, unified_diff
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import settings


class VersionComparisonAgent:
    """Agent for comparing different versions of contracts"""
    
    def __init__(self):
        """Initialize version comparison agent"""
        self.llm = ChatGroq(
            model=settings.groq_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            groq_api_key=settings.groq_api_key
        )
    
    async def compare_versions(self, original_text: str, modified_text: str, version_labels: Tuple[str, str] = ("Original", "Modified")) -> Dict[str, Any]:
        """
        Compare two versions of a contract
        
        Args:
            original_text: Original contract text
            modified_text: Modified contract text
            version_labels: Tuple of labels for versions (original, modified)
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            # Get text-based diff
            text_diff = self._get_text_diff(original_text, modified_text, version_labels)
            
            # Get AI analysis of changes
            ai_analysis = await self._analyze_changes_with_ai(original_text, modified_text, version_labels)
            
            # Get clause-level changes
            clause_changes = await self._compare_clauses(original_text, modified_text)
            
            return {
                "success": True,
                "version_labels": list(version_labels),
                "text_diff": text_diff,
                "ai_analysis": ai_analysis,
                "clause_changes": clause_changes,
                "similarity_score": self._calculate_similarity(original_text, modified_text),
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Version comparison failed: {str(e)}",
                "timestamp": self._get_timestamp()
            }
    
    async def compare_analyses(self, original_analysis: Dict[str, Any], modified_analysis: Dict[str, Any], version_labels: Tuple[str, str] = ("Original", "Modified")) -> Dict[str, Any]:
        """
        Compare analysis results of two contract versions
        
        Args:
            original_analysis: Analysis of original contract
            modified_analysis: Analysis of modified contract
            version_labels: Tuple of labels for versions
            
        Returns:
            Dictionary containing analysis comparison
        """
        try:
            comparison = {
                "risk_comparison": self._compare_risks(original_analysis, modified_analysis),
                "compliance_comparison": self._compare_compliance(original_analysis, modified_analysis),
                "clause_comparison": self._compare_clause_counts(original_analysis, modified_analysis)
            }
            
            # Get summary comparison asynchronously
            summary_comparison = await self._compare_summaries(original_analysis, modified_analysis, version_labels)
            comparison["summary_comparison"] = summary_comparison
            
            return {
                "success": True,
                "version_labels": list(version_labels),
                "comparison": comparison,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis comparison failed: {str(e)}",
                "timestamp": self._get_timestamp()
            }
    
    def _get_text_diff(self, original: str, modified: str, version_labels: Tuple[str, str]) -> Dict[str, Any]:
        """Generate text-based diff between two versions"""
        try:
            original_lines = original.splitlines(keepends=True)
            modified_lines = modified.splitlines(keepends=True)
            
            diff = list(unified_diff(
                original_lines, 
                modified_lines,
                fromfile=f"{version_labels[0]}",
                tofile=f"{version_labels[1]}",
                lineterm=''
            ))
            
            return {
                "diff_text": ''.join(diff),
                "has_changes": len(diff) > 0,
                "lines_added": self._count_added_lines(diff),
                "lines_removed": self._count_removed_lines(diff),
                "lines_modified": self._count_modified_lines(diff)
            }
            
        except Exception as e:
            return {"error": f"Text diff generation failed: {str(e)}"}
    
    async def _analyze_changes_with_ai(self, original: str, modified: str, version_labels: Tuple[str, str]) -> Dict[str, Any]:
        """Use AI to analyze and explain the changes"""
        try:
            system_prompt = """You are a legal document analyst specializing in contract changes. Your task is to:

1. Identify what changed between contract versions
2. Explain the legal and business implications
3. Highlight any new risks or benefits
4. Assess if changes are favorable or unfavorable
5. Provide recommendations

Structure your response as:
- **Summary of Changes**: Brief overview
- **Key Modifications**: Important changes with details
- **Risk Implications**: New or changed risks
- **Business Impact**: How changes affect parties
- **Recommendations**: Suggestions for further action"""
            
            human_message = f"""
ORIGINAL VERSION ({version_labels[0]}):
{original[:3000]}...

MODIFIED VERSION ({version_labels[1]}):
{modified[:3000]}...

Please analyze the changes and provide a comprehensive comparison."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_message)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "ai_analysis": response.content,
                "analysis_type": "comprehensive_change_analysis"
            }
            
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    async def _compare_clauses(self, original: str, modified: str) -> Dict[str, Any]:
        """Compare clauses between two versions"""
        try:
            # Extract clauses from both versions (simplified extraction)
            original_clauses = self._extract_clauses_simple(original)
            modified_clauses = self._extract_clauses_simple(modified)
            
            # Find added, removed, and modified clauses
            added_clauses = []
            removed_clauses = []
            modified_clauses = []
            
            for clause in modified_clauses:
                similar_original = self._find_similar_clause(clause, original_clauses)
                if similar_original:
                    if clause["text"] != similar_original["text"]:
                        modified_clauses.append({
                            "clause_id": clause["id"],
                            "original_text": similar_original["text"],
                            "modified_text": clause["text"],
                            "change_type": "modified"
                        })
                else:
                    added_clauses.append({
                        "clause_id": clause["id"],
                        "text": clause["text"],
                        "change_type": "added"
                    })
            
            for clause in original_clauses:
                similar_modified = self._find_similar_clause(clause, modified_clauses)
                if not similar_modified:
                    removed_clauses.append({
                        "clause_id": clause["id"],
                        "text": clause["text"],
                        "change_type": "removed"
                    })
            
            return {
                "added_clauses": added_clauses,
                "removed_clauses": removed_clauses,
                "modified_clauses": modified_clauses,
                "total_changes": len(added_clauses) + len(removed_clauses) + len(modified_clauses)
            }
            
        except Exception as e:
            return {"error": f"Clause comparison failed: {str(e)}"}
    
    def _extract_clauses_simple(self, text: str) -> List[Dict[str, Any]]:
        """Simple clause extraction for comparison purposes"""
        import re
        
        # Split by numbered sections
        sections = re.split(r'\n(\d+\.\s+)', text)
        clauses = []
        
        clause_id = 1
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                section_num = sections[i].strip()
                section_text = sections[i + 1].strip()
                
                if section_text:
                    clauses.append({
                        "id": clause_id,
                        "number": section_num,
                        "text": f"{section_num} {section_text}"
                    })
                    clause_id += 1
        
        return clauses
    
    def _find_similar_clause(self, clause: Dict[str, Any], clause_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find similar clause in a list"""
        threshold = 0.7  # Similarity threshold
        
        for other_clause in clause_list:
            similarity = self._calculate_text_similarity(clause["text"], other_clause["text"])
            if similarity > threshold:
                return other_clause
        
        return None
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate overall similarity score"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _count_added_lines(self, diff: List[str]) -> int:
        """Count added lines in diff"""
        return sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    
    def _count_removed_lines(self, diff: List[str]) -> int:
        """Count removed lines in diff"""
        return sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
    
    def _count_modified_lines(self, diff: List[str]) -> int:
        """Count modified lines in diff"""
        # This is simplified - a more sophisticated approach would track context
        return min(self._count_added_lines(diff), self._count_removed_lines(diff))
    
    def _compare_risks(self, original_analysis: Dict[str, Any], modified_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare risk analyses between versions"""
        try:
            original_risks = original_analysis.get("risks_analyzed", {}).get("risk_analyses", [])
            modified_risks = modified_analysis.get("risks_analyzed", {}).get("risk_analyses", [])
            
            # Calculate risk metrics
            original_high_risks = len([r for r in original_risks if r.get("risk_level") == "High"])
            modified_high_risks = len([r for r in modified_risks if r.get("risk_level") == "High"])
            
            original_avg_score = sum(r.get("risk_score", 0) for r in original_risks) / len(original_risks) if original_risks else 0
            modified_avg_score = sum(r.get("risk_score", 0) for r in modified_risks) / len(modified_risks) if modified_risks else 0
            
            return {
                "original_high_risks": original_high_risks,
                "modified_high_risks": modified_high_risks,
                "risk_change": modified_high_risks - original_high_risks,
                "original_avg_score": round(original_avg_score, 1),
                "modified_avg_score": round(modified_avg_score, 1),
                "score_change": round(modified_avg_score - original_avg_score, 1),
                "risk_trend": "increased" if modified_avg_score > original_avg_score else "decreased" if modified_avg_score < original_avg_score else "unchanged"
            }
            
        except Exception as e:
            return {"error": f"Risk comparison failed: {str(e)}"}
    
    def _compare_compliance(self, original_analysis: Dict[str, Any], modified_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare compliance between versions"""
        try:
            original_compliance = original_analysis.get("compliance_checked", {})
            modified_compliance = modified_analysis.get("compliance_checked", {})
            
            return {
                "original_compliance": original_compliance.get("overall_compliance", "Unknown"),
                "modified_compliance": modified_compliance.get("overall_compliance", "Unknown"),
                "original_missing_clauses": original_compliance.get("missing_clauses", []),
                "modified_missing_clauses": modified_compliance.get("missing_clauses", []),
                "compliance_change": "improved" if len(modified_compliance.get("missing_clauses", [])) < len(original_compliance.get("missing_clauses", [])) else "degraded"
            }
            
        except Exception as e:
            return {"error": f"Compliance comparison failed: {str(e)}"}
    
    def _compare_clause_counts(self, original_analysis: Dict[str, Any], modified_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare clause counts and categories"""
        try:
            original_clauses = original_analysis.get("clauses_extracted", {}).get("clauses", [])
            modified_clauses = modified_analysis.get("clauses_extracted", {}).get("clauses", [])
            
            return {
                "original_clause_count": len(original_clauses),
                "modified_clause_count": len(modified_clauses),
                "clause_count_change": len(modified_clauses) - len(original_clauses),
                "categories_added": self._get_category_changes(original_clauses, modified_clauses, "added"),
                "categories_removed": self._get_category_changes(original_clauses, modified_clauses, "removed")
            }
            
        except Exception as e:
            return {"error": f"Clause count comparison failed: {str(e)}"}
    
    def _get_category_changes(self, original: List[Dict[str, Any]], modified: List[Dict[str, Any]], change_type: str) -> List[str]:
        """Get category changes between versions"""
        original_categories = set(clause.get("clause_category", "") for clause in original)
        modified_categories = set(clause.get("clause_category", "") for clause in modified)
        
        if change_type == "added":
            return list(modified_categories - original_categories)
        else:
            return list(original_categories - modified_categories)
    
    async def _compare_summaries(self, original: Dict[str, Any], modified: Dict[str, Any], version_labels: Tuple[str, str]) -> Dict[str, Any]:
        """Use AI to compare overall summaries"""
        try:
            system_prompt = """You are a contract analyst comparing two contract versions. Provide a concise comparison of the overall changes and their implications.

Focus on:
1. Overall risk level changes
2. Compliance improvements or degradations
3. Structural changes (added/removed clauses)
4. Business impact assessment
5. Recommendations for the user

Keep your response structured and actionable."""
            
            # Create summary of both versions
            original_summary = self._create_version_summary(original, version_labels[0])
            modified_summary = self._create_version_summary(modified, version_labels[1])
            
            human_message = f"""
{version_labels[0]} VERSION SUMMARY:
{original_summary}

{version_labels[1]} VERSION SUMMARY:
{modified_summary}

Please provide a comprehensive comparison of these two contract versions."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_message)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                "comparison_summary": response.content,
                "analysis_type": "overall_comparison"
            }
            
        except Exception as e:
            return {"error": f"Summary comparison failed: {str(e)}"}
    
    def _create_version_summary(self, analysis: Dict[str, Any], version_label: str) -> str:
        """Create a summary of a contract version"""
        try:
            clauses = analysis.get("clauses_extracted", {}).get("clauses", [])
            risks = analysis.get("risks_analyzed", {}).get("risk_analyses", [])
            compliance = analysis.get("compliance_checked", {})
            
            summary = f"{version_label} Version:\n"
            summary += f"- Total clauses: {len(clauses)}\n"
            
            if risks:
                high_risks = len([r for r in risks if r.get("risk_level") == "High"])
                avg_score = sum(r.get("risk_score", 0) for r in risks) / len(risks) if risks else 0
                summary += f"- High-risk clauses: {high_risks}\n"
                summary += f"- Average risk score: {avg_score:.1f}\n"
            
            if compliance:
                summary += f"- Overall compliance: {compliance.get('overall_compliance', 'Unknown')}\n"
                missing = compliance.get("missing_clauses", [])
                if missing:
                    summary += f"- Missing essential clauses: {', '.join(missing)}\n"
            
            return summary
            
        except Exception as e:
            return f"Error creating summary for {version_label}: {str(e)}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
