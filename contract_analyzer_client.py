"""
AI Contract Risk Detector - Python Client Library
Simple Python client for interacting with the Contract Analysis API
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path


class ContractAnalyzerClient:
    """Python client for AI Contract Risk Detector API"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the API service
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the API service is healthy"""
        response = self.session.get(f"{self.base_url.replace('/api', '')}/health")
        response.raise_for_status()
        return response.json()
    
    def analyze_contract(self, file_path: str) -> str:
        """
        Upload and analyze a contract file
        
        Args:
            file_path: Path to the contract file (PDF, DOCX, or TXT)
            
        Returns:
            Analysis ID for tracking the analysis
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Contract file not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(f"{self.base_url}/analyze-contract", files=files)
        
        if response.status_code == 200:
            data = response.json()
            return data['analysis_id']
        else:
            raise Exception(f"Analysis failed: {response.text}")
    
    def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get the current status of a contract analysis
        
        Args:
            analysis_id: Analysis ID returned by analyze_contract()
            
        Returns:
            Status information including progress percentage
        """
        response = self.session.get(f"{self.base_url}/analysis-status/{analysis_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_analysis(self, analysis_id: str, timeout: int = 600, poll_interval: int = 10) -> Dict[str, Any]:
        """
        Wait for analysis to complete and return results
        
        Args:
            analysis_id: Analysis ID
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            Complete analysis results
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                results = self.get_analysis_results(analysis_id)
                if results.get('success'):
                    return results
                elif results.get('status') == 'failed':
                    raise Exception(f"Analysis failed: {results.get('error')}")
            except:
                # Analysis still processing
                pass
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Analysis did not complete within {timeout} seconds")
    
    def get_analysis_results(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get complete analysis results
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Complete analysis results
        """
        response = self.session.get(f"{self.base_url}/analysis-results/{analysis_id}")
        response.raise_for_status()
        return response.json()
    
    def get_analysis_summary(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get analysis summary with key metrics
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Summary of analysis results
        """
        response = self.session.get(f"{self.base_url}/analysis-summary/{analysis_id}")
        response.raise_for_status()
        return response.json()
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis and its associated files
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            True if deletion was successful
        """
        response = self.session.delete(f"{self.base_url}/analysis/{analysis_id}")
        response.raise_for_status()
        return response.json().get('success', False)
    
    # AI Chat Methods
    def ask_about_contract(self, question: str, analysis_id: Optional[str] = None, 
                          contract_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask AI a question about a contract
        
        Args:
            question: Your question about the contract
            analysis_id: Optional analysis ID for context
            contract_text: Optional raw contract text
            
        Returns:
            AI response to your question
        """
        data = {
            'question': question,
            'analysis_id': analysis_id or '',
            'contract_text': contract_text or ''
        }
        response = self.session.post(f"{self.base_url}/ai-chat/ask", data=data)
        response.raise_for_status()
        return response.json()
    
    def explain_clause(self, clause_text: str, analysis_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get AI explanation of a specific clause
        
        Args:
            clause_text: The clause text to explain
            analysis_id: Optional analysis ID for context
            
        Returns:
            AI explanation of the clause
        """
        data = {
            'clause_text': clause_text,
            'analysis_id': analysis_id or ''
        }
        response = self.session.post(f"{self.base_url}/ai-chat/explain-clause", data=data)
        response.raise_for_status()
        return response.json()
    
    def suggest_improvements(self, clause_text: str, analysis_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get AI suggestions for improving a clause
        
        Args:
            clause_text: The clause text to improve
            analysis_id: Optional analysis ID for context
            
        Returns:
            AI suggestions for improvement
        """
        data = {
            'clause_text': clause_text,
            'analysis_id': analysis_id or ''
        }
        response = self.session.post(f"{self.base_url}/ai-chat/suggest-improvements", data=data)
        response.raise_for_status()
        return response.json()
    
    # Version Comparison Methods
    def compare_texts(self, original_text: str, modified_text: str,
                     original_label: str = "Original", modified_label: str = "Modified") -> Dict[str, Any]:
        """
        Compare two contract text versions
        
        Args:
            original_text: Original contract text
            modified_text: Modified contract text
            original_label: Label for original version
            modified_label: Label for modified version
            
        Returns:
            Comparison results with AI analysis
        """
        data = {
            'original_text': original_text,
            'modified_text': modified_text,
            'original_label': original_label,
            'modified_label': modified_label
        }
        response = self.session.post(f"{self.base_url}/version-comparison/compare-texts", data=data)
        response.raise_for_status()
        return response.json()
    
    def compare_files(self, original_file: str, modified_file: str,
                     original_label: str = "Original", modified_label: str = "Modified") -> Dict[str, Any]:
        """
        Compare two contract files
        
        Args:
            original_file: Path to original contract file
            modified_file: Path to modified contract file
            original_label: Label for original version
            modified_label: Label for modified version
            
        Returns:
            Comparison results with AI analysis
        """
        with open(original_file, 'rb') as f1, open(modified_file, 'rb') as f2:
            files = {
                'original_file': f1,
                'modified_file': f2
            }
            data = {
                'original_label': original_label,
                'modified_label': modified_label
            }
            response = self.session.post(f"{self.base_url}/version-comparison/compare-files", 
                                       files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    # Report Generation Methods
    def generate_pdf_report(self, analysis_id: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Generate PDF report"""
        data = {'analysis_id': analysis_id, 'filename': filename or ''}
        response = self.session.post(f"{self.base_url}/reports/generate-pdf", data=data)
        response.raise_for_status()
        return response.json()
    
    def generate_html_report(self, analysis_id: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Generate HTML report"""
        data = {'analysis_id': analysis_id, 'filename': filename or ''}
        response = self.session.post(f"{self.base_url}/reports/generate-html", data=data)
        response.raise_for_status()
        return response.json()
    
    def generate_json_report(self, analysis_id: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Generate JSON report"""
        data = {'analysis_id': analysis_id, 'filename': filename or ''}
        response = self.session.post(f"{self.base_url}/reports/generate-json", data=data)
        response.raise_for_status()
        return response.json()
    
    def generate_word_report(self, analysis_id: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Generate Word (RTF) report"""
        data = {'analysis_id': analysis_id, 'filename': filename or ''}
        response = self.session.post(f"{self.base_url}/reports/generate-word", data=data)
        response.raise_for_status()
        return response.json()
    
    def generate_all_reports(self, analysis_id: str, base_filename: Optional[str] = None) -> Dict[str, Any]:
        """Generate reports in all formats"""
        data = {'analysis_id': analysis_id, 'base_filename': base_filename or ''}
        response = self.session.post(f"{self.base_url}/reports/generate-all-formats", data=data)
        response.raise_for_status()
        return response.json()
    
    def get_available_formats(self) -> Dict[str, Any]:
        """Get list of available report formats"""
        response = self.session.get(f"{self.base_url}/reports/available-formats")
        response.raise_for_status()
        return response.json()
    
    def save_report(self, report_data: Dict[str, Any], output_path: str):
        """
        Save a report to file
        
        Args:
            report_data: Report data from generate_*_report methods
            output_path: Path where to save the report
        """
        import base64
        
        if 'content_base64' not in report_data:
            raise ValueError("Invalid report data - missing content_base64")
        
        content = base64.b64decode(report_data['content_base64'])
        
        with open(output_path, 'wb') as f:
            f.write(content)
        
        print(f"Report saved to: {output_path}")


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = ContractAnalyzerClient()
    
    try:
        # Check API health
        health = client.health_check()
        print(f"API Status: {health['status']}")
        
        # Analyze contract
        print("Analyzing contract...")
        analysis_id = client.analyze_contract("sample-contracts/Sample_Service_Agreement.txt")
        print(f"Analysis started: {analysis_id}")
        
        # Wait for completion
        print("Waiting for analysis to complete...")
        results = client.wait_for_analysis(analysis_id, timeout=300)
        print("Analysis complete!")
        
        # Get summary
        summary = client.get_analysis_summary(analysis_id)
        print(f"Total clauses: {summary['summary']['total_clauses']}")
        print(f"High risk clauses: {summary['summary']['high_risk_clauses']}")
        
        # Ask AI about contract
        answer = client.ask_about_contract("What are the main risks?", analysis_id)
        print(f"AI Answer: {answer['answer']}")
        
        # Generate PDF report
        pdf_report = client.generate_pdf_report(analysis_id)
        client.save_report(pdf_report, "contract_analysis.pdf")
        
    except Exception as e:
        print(f"Error: {e}")
