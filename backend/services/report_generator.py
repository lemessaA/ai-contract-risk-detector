"""
Report Generator Service
Creates downloadable reports in various formats (PDF, Word, HTML)
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import base64

# For PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# For HTML generation
try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


class ReportGenerator:
    """Generates downloadable contract analysis reports"""
    
    def __init__(self):
        """Initialize report generator"""
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
    
    async def generate_pdf_report(self, analysis_results: Dict[str, Any], filename: str = None) -> Dict[str, Any]:
        """
        Generate PDF report from analysis results
        
        Args:
            analysis_results: Complete contract analysis results
            filename: Optional custom filename
            
        Returns:
            Dictionary containing PDF file info and base64 content
        """
        try:
            if not REPORTLAB_AVAILABLE:
                return {
                    "success": False,
                    "error": "PDF generation not available - reportlab not installed"
                }
            
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"contract_analysis_{timestamp}.pdf"
            
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            file_path = self.output_dir / filename
            
            # Create PDF document
            doc = SimpleDocTemplate(str(file_path), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph("Contract Analysis Report", title_style))
            story.append(Spacer(1, 20))
            
            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            summary = self._create_executive_summary(analysis_results)
            story.append(Paragraph(summary, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Risk Analysis
            story.append(Paragraph("Risk Analysis", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            risk_table = self._create_risk_table(analysis_results)
            if risk_table:
                story.append(risk_table)
            story.append(Spacer(1, 20))
            
            # Compliance Analysis
            story.append(Paragraph("Compliance Analysis", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            compliance_text = self._create_compliance_summary(analysis_results)
            story.append(Paragraph(compliance_text, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Recommendations
            story.append(Paragraph("Recommendations", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            recommendations = self._create_recommendations(analysis_results)
            story.append(Paragraph(recommendations, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Read file and convert to base64
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            
            return {
                "success": True,
                "filename": filename,
                "format": "PDF",
                "size_bytes": len(pdf_content),
                "content_base64": base64.b64encode(pdf_content).decode(),
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_html_report(self, analysis_results: Dict[str, Any], filename: str = None) -> Dict[str, Any]:
        """
        Generate HTML report from analysis results
        
        Args:
            analysis_results: Complete contract analysis results
            filename: Optional custom filename
            
        Returns:
            Dictionary containing HTML file info and base64 content
        """
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"contract_analysis_{timestamp}.html"
            
            if not filename.endswith('.html'):
                filename += '.html'
            
            file_path = self.output_dir / filename
            
            # Create HTML content
            html_content = self._create_html_report(analysis_results)
            
            # Write HTML file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Read file and convert to base64
            with open(file_path, 'rb') as f:
                html_content_bytes = f.read()
            
            return {
                "success": True,
                "filename": filename,
                "format": "HTML",
                "size_bytes": len(html_content_bytes),
                "content_base64": base64.b64encode(html_content_bytes).decode(),
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"HTML generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_word_report(self, analysis_results: Dict[str, Any], filename: str = None) -> Dict[str, Any]:
        """
        Generate Word document report from analysis results
        
        Args:
            analysis_results: Complete contract analysis results
            filename: Optional custom filename
            
        Returns:
            Dictionary containing Word file info and base64 content
        """
        try:
            # For now, generate a rich text format that can be opened in Word
            # In production, you'd use python-docx library
            
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"contract_analysis_{timestamp}.rtf"
            
            if not filename.endswith('.rtf'):
                filename += '.rtf'
            
            file_path = self.output_dir / filename
            
            # Create RTF content (simplified)
            rtf_content = self._create_rtf_report(analysis_results)
            
            # Write RTF file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(rtf_content)
            
            # Read file and convert to base64
            with open(file_path, 'rb') as f:
                rtf_content_bytes = f.read()
            
            return {
                "success": True,
                "filename": filename,
                "format": "RTF",
                "size_bytes": len(rtf_content_bytes),
                "content_base64": base64.b64encode(rtf_content_bytes).decode(),
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Word document generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_json_report(self, analysis_results: Dict[str, Any], filename: str = None) -> Dict[str, Any]:
        """
        Generate JSON report from analysis results
        
        Args:
            analysis_results: Complete contract analysis results
            filename: Optional custom filename
            
        Returns:
            Dictionary containing JSON file info and base64 content
        """
        try:
            # Generate filename
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"contract_analysis_{timestamp}.json"
            
            if not filename.endswith('.json'):
                filename += '.json'
            
            file_path = self.output_dir / filename
            
            # Create enhanced JSON report
            json_report = {
                "metadata": {
                    "report_type": "Contract Analysis Report",
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "analysis_results": analysis_results,
                "summary": {
                    "executive_summary": self._create_executive_summary(analysis_results),
                    "risk_summary": self._create_risk_summary(analysis_results),
                    "compliance_summary": self._create_compliance_summary(analysis_results),
                    "recommendations": self._create_recommendations(analysis_results)
                }
            }
            
            # Write JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)
            
            # Read file and convert to base64
            with open(file_path, 'rb') as f:
                json_content_bytes = f.read()
            
            return {
                "success": True,
                "filename": filename,
                "format": "JSON",
                "size_bytes": len(json_content_bytes),
                "content_base64": base64.b64encode(json_content_bytes).decode(),
                "file_path": str(file_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"JSON generation failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_executive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Create executive summary text"""
        try:
            clauses = analysis_results.get("clauses_extracted", {}).get("clauses", [])
            risks = analysis_results.get("risks_analyzed", {}).get("risk_analyses", [])
            compliance = analysis_results.get("compliance_checked", {})
            
            summary = f"This contract analysis examined {len(clauses)} clauses and identified "
            
            if risks:
                high_risks = len([r for r in risks if r.get("risk_level") == "High"])
                medium_risks = len([r for r in risks if r.get("risk_level") == "Medium"])
                summary += f"{high_risks} high-risk and {medium_risks} medium-risk clauses. "
            
            if compliance:
                overall_comp = compliance.get("overall_compliance", "Unknown")
                missing = len(compliance.get("missing_clauses", []))
                summary += f"The contract shows {overall_comp.lower()} compliance with {missing} essential clauses missing."
            
            return summary
            
        except Exception as e:
            return f"Error creating executive summary: {str(e)}"
    
    def _create_risk_table(self, analysis_results: Dict[str, Any]):
        """Create risk analysis table for PDF"""
        try:
            if not REPORTLAB_AVAILABLE:
                return None
            
            risks = analysis_results.get("risks_analyzed", {}).get("risk_analyses", [])
            
            if not risks:
                return Paragraph("No risk analysis available.", getSampleStyleSheet()['Normal'])
            
            # Table data
            table_data = [["Clause", "Risk Level", "Risk Score", "Categories"]]
            
            for risk in risks[:10]:  # Limit to top 10 risks
                clause_name = risk.get("clause_name", "Unknown")[:30]  # Truncate long names
                risk_level = risk.get("risk_level", "Unknown")
                risk_score = str(risk.get("risk_score", 0))
                categories = ", ".join(risk.get("risk_categories", [])[:3])  # Limit categories
                
                table_data.append([clause_name, risk_level, risk_score, categories])
            
            # Create table
            table = Table(table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            return table
            
        except Exception as e:
            return None
    
    def _create_compliance_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Create compliance summary text"""
        try:
            compliance = analysis_results.get("compliance_checked", {})
            
            if not compliance:
                return "No compliance analysis available."
            
            overall = compliance.get("overall_compliance", "Unknown")
            present = compliance.get("essential_clauses_present", [])
            missing = compliance.get("missing_clauses", [])
            issues = compliance.get("compliance_issues", [])
            
            summary = f"Overall Compliance: {overall}\n\n"
            summary += f"Essential Clauses Present: {', '.join(present) if present else 'None'}\n"
            
            if missing:
                summary += f"Missing Essential Clauses: {', '.join(missing)}\n"
            
            if issues:
                summary += f"\nCompliance Issues ({len(issues)}):\n"
                for i, issue in enumerate(issues[:5], 1):
                    summary += f"{i}. {issue.get('issue', 'Unknown issue')}\n"
            
            return summary
            
        except Exception as e:
            return f"Error creating compliance summary: {str(e)}"
    
    def _create_recommendations(self, analysis_results: Dict[str, Any]) -> str:
        """Create recommendations text"""
        try:
            report = analysis_results.get("report_generated", {}).get("report", {})
            
            if not report:
                return "No recommendations available."
            
            overall_rec = report.get("overall_recommendation", "No overall recommendation")
            risky_clauses = report.get("top_risky_clauses", [])
            key_recs = report.get("key_recommendations", [])
            
            summary = f"Overall Recommendation: {overall_rec}\n\n"
            
            if risky_clauses:
                summary += "Top Risky Clauses:\n"
                for i, clause in enumerate(risky_clauses[:3], 1):
                    clause_name = clause.get("clause_name", "Unknown")
                    risk_level = clause.get("risk_level", "Unknown")
                    summary += f"{i}. {clause_name} (Risk Level: {risk_level})\n"
                summary += "\n"
            
            if key_recs:
                summary += "Key Recommendations:\n"
                for i, rec in enumerate(key_recs[:5], 1):
                    summary += f"{i}. {rec}\n"
            
            return summary
            
        except Exception as e:
            return f"Error creating recommendations: {str(e)}"
    
    def _create_risk_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Create risk summary text"""
        try:
            risks = analysis_results.get("risks_analyzed", {}).get("risk_analyses", [])
            
            if not risks:
                return "No risk analysis available."
            
            high_risks = len([r for r in risks if r.get("risk_level") == "High"])
            medium_risks = len([r for r in risks if r.get("risk_level") == "Medium"])
            low_risks = len([r for r in risks if r.get("risk_level") == "Low"])
            
            avg_score = sum(r.get("risk_score", 0) for r in risks) / len(risks) if risks else 0
            
            summary = f"Total Clauses Analyzed: {len(risks)}\n"
            summary += f"High Risk: {high_risks}, Medium Risk: {medium_risks}, Low Risk: {low_risks}\n"
            summary += f"Average Risk Score: {avg_score:.1f}/100\n"
            
            return summary
            
        except Exception as e:
            return f"Error creating risk summary: {str(e)}"
    
    def _create_html_report(self, analysis_results: Dict[str, Any]) -> str:
        """Create HTML report content"""
        try:
            html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contract Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
        .risk-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .risk-table th, .risk-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .risk-table th { background-color: #f2f2f2; }
        .high-risk { background-color: #ffebee; }
        .medium-risk { background-color: #fff3e0; }
        .low-risk { background-color: #e8f5e8; }
        .recommendation { background-color: #f5f5f5; padding: 15px; border-left: 4px solid #2196f3; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Contract Analysis Report</h1>
        <p>Generated on {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <p>{executive_summary}</p>
    </div>
    
    <div class="section">
        <h2>Risk Analysis</h2>
        <p>{risk_summary}</p>
        {risk_table_html}
    </div>
    
    <div class="section">
        <h2>Compliance Analysis</h2>
        <p>{compliance_summary}</p>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <div class="recommendation">{recommendations}</div>
    </div>
</body>
</html>
            """
            
            # Replace placeholders
            return html_template.format(
                timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
                executive_summary=self._create_executive_summary(analysis_results),
                risk_summary=self._create_risk_summary(analysis_results),
                risk_table_html=self._create_html_risk_table(analysis_results),
                compliance_summary=self._create_compliance_summary(analysis_results),
                recommendations=self._create_recommendations(analysis_results)
            )
            
        except Exception as e:
            return f"<html><body><h1>Error generating HTML report: {str(e)}</h1></body></html>"
    
    def _create_html_risk_table(self, analysis_results: Dict[str, Any]) -> str:
        """Create HTML risk table"""
        try:
            risks = analysis_results.get("risks_analyzed", {}).get("risk_analyses", [])
            
            if not risks:
                return "<p>No risk analysis available.</p>"
            
            html = '<table class="risk-table">'
            html += '<tr><th>Clause</th><th>Risk Level</th><th>Risk Score</th><th>Categories</th></tr>'
            
            for risk in risks[:10]:  # Limit to top 10
                clause_name = risk.get("clause_name", "Unknown")
                risk_level = risk.get("risk_level", "Unknown").lower()
                risk_score = risk.get("risk_score", 0)
                categories = ", ".join(risk.get("risk_categories", []))
                
                row_class = f"{risk_level}-risk"
                html += f'<tr class="{row_class}">'
                html += f'<td>{clause_name}</td>'
                html += f'<td>{risk_level.title()}</td>'
                html += f'<td>{risk_score}</td>'
                html += f'<td>{categories}</td>'
                html += '</tr>'
            
            html += '</table>'
            return html
            
        except Exception as e:
            return f"<p>Error creating risk table: {str(e)}</p>"
    
    def _create_rtf_report(self, analysis_results: Dict[str, Any]) -> str:
        """Create RTF report content (simplified)"""
        try:
            rtf_header = "{\\rtf1\\ansi\\deff0"
            rtf_content = rtf_header
            
            # Title
            rtf_content += "{\\pard\\qc\\fs32\\b Contract Analysis Report\\par\\par}"
            
            # Executive Summary
            rtf_content += "{\\pard\\fs24\\b Executive Summary\\par\\par}"
            rtf_content += "{\\pard\\fs20\\plain " + self._create_executive_summary(analysis_results) + "\\par\\par}"
            
            # Risk Analysis
            rtf_content += "{\\pard\\fs24\\b Risk Analysis\\par\\par}"
            rtf_content += "{\\pard\\fs20\\plain " + self._create_risk_summary(analysis_results) + "\\par\\par}"
            
            # Compliance Analysis
            rtf_content += "{\\pard\\fs24\\b Compliance Analysis\\par\\par}"
            rtf_content += "{\\pard\\fs20\\plain " + self._create_compliance_summary(analysis_results) + "\\par\\par}"
            
            # Recommendations
            rtf_content += "{\\pard\\fs24\\b Recommendations\\par\\par}"
            rtf_content += "{\\pard\\fs20\\plain " + self._create_recommendations(analysis_results) + "\\par\\par}"
            
            rtf_content += "}"
            
            return rtf_content
            
        except Exception as e:
            return f"{{\\rtf1\\ansi Error creating RTF report: {str(e)}"
