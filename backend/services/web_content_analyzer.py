"""
Web Content Analyzer Service
Integrates web scraping with contract analysis pipeline
"""

import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from services.web_scraper import web_scraper, WebScrapingResult
from agents.contract_agent import ContractAnalysisOrchestrator
from storage import get_analysis_store, store_analysis
from guardrails import guardrails_system

logger = logging.getLogger(__name__)

class WebContentAnalyzer:
    """Analyzer for web content using contract analysis pipeline"""
    
    def __init__(self):
        self.orchestrator = ContractAnalysisOrchestrator()
        self.max_urls_per_analysis = 5
        self.max_content_length = 50000  # 50KB per URL
    
    async def analyze_web_content(self, url: str, analysis_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze legal content from a single URL
        
        Args:
            url: URL to analyze
            analysis_options: Additional analysis options
            
        Returns:
            Analysis results with web-specific metadata
        """
        try:
            # Generate analysis ID
            analysis_id = str(uuid.uuid4())
            
            # Initialize analysis status
            analysis_store = get_analysis_store()
            analysis_store[analysis_id] = {
                "id": analysis_id,
                "type": "web_content",
                "status": "processing",
                "started_at": datetime.now().isoformat(),
                "urls": [url],
                "progress": 0
            }
            
            # Update progress
            analysis_store[analysis_id]["progress"] = 10
            analysis_store[analysis_id]["status"] = "scraping"
            
            # Scrape web content
            scraping_result = await web_scraper.scrape_url(url, analysis_options)
            
            if not scraping_result.success:
                analysis_store[analysis_id].update({
                    "status": "failed",
                    "error": scraping_result.error,
                    "completed_at": datetime.now().isoformat()
                })
                return {
                    "success": False,
                    "analysis_id": analysis_id,
                    "error": scraping_result.error,
                    "scraping_result": scraping_result.__dict__
                }
            
            # Update progress
            analysis_store[analysis_id]["progress"] = 30
            analysis_store[analysis_id]["status"] = "analyzing"
            analysis_store[analysis_id]["scraping_result"] = scraping_result.__dict__
            
            # Validate scraped content with guardrails
            content_validation = guardrails_system.validate_input(
                scraping_result.content,
                input_type="text",
                context="web_content"
            )
            
            if content_validation.triggered and content_validation.action.value == "block":
                analysis_store[analysis_id].update({
                    "status": "failed",
                    "error": "Scraped content contains prohibited material",
                    "completed_at": datetime.now().isoformat()
                })
                return {
                    "success": False,
                    "analysis_id": analysis_id,
                    "error": "Content validation failed",
                    "guardrail_result": content_validation.__dict__
                }
            
            # Use sanitized content if needed
            analysis_content = content_validation.sanitized_content or scraping_result.content
            
            # Update progress
            analysis_store[analysis_id]["progress"] = 50
            
            # Run contract analysis on scraped content
            analysis_results = await self._analyze_content(
                analysis_content,
                url,
                scraping_result.title,
                analysis_options
            )
            
            # Update progress
            analysis_store[analysis_id]["progress"] = 90
            
            # Combine results
            final_results = {
                "analysis_id": analysis_id,
                "type": "web_content",
                "web_metadata": {
                    "url": url,
                    "title": scraping_result.title,
                    "scraped_at": scraping_result.scraped_at,
                    "content_length": len(scraping_result.content),
                    "legal_content_detected": web_scraper._contains_legal_content(scraping_result.content)
                },
                "scraping_metadata": scraping_result.metadata,
                "contract_analysis": analysis_results,
                "guardrail_warnings": [
                    content_validation.message
                ] if content_validation.triggered else [],
                "analysis_completed_at": datetime.now().isoformat()
            }
            
            # Store final results
            analysis_store[analysis_id].update({
                "status": "completed",
                "progress": 100,
                "results": final_results,
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "results": final_results
            }
            
        except Exception as e:
            logger.error(f"Web content analysis failed: {str(e)}")
            
            if 'analysis_id' in locals():
                analysis_store = get_analysis_store()
                analysis_store[analysis_id].update({
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now().isoformat()
                })
            
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}"
            }
    
    async def analyze_multiple_urls(self, urls: List[str], analysis_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze legal content from multiple URLs
        
        Args:
            urls: List of URLs to analyze
            analysis_options: Additional analysis options
            
        Returns:
            Combined analysis results
        """
        try:
            # Validate URL count
            if len(urls) > self.max_urls_per_analysis:
                return {
                    "success": False,
                    "error": f"Too many URLs. Maximum {self.max_urls_per_analysis} URLs allowed per analysis"
                }
            
            # Generate analysis ID
            analysis_id = str(uuid.uuid4())
            
            # Initialize analysis status
            analysis_store = get_analysis_store()
            analysis_store[analysis_id] = {
                "id": analysis_id,
                "type": "web_content_batch",
                "status": "processing",
                "started_at": datetime.now().isoformat(),
                "urls": urls,
                "progress": 0
            }
            
            # Scrape all URLs concurrently
            analysis_store[analysis_id]["status"] = "scraping"
            analysis_store[analysis_id]["progress"] = 10
            
            scraping_results = await web_scraper.batch_scrape(urls, analysis_options)
            
            # Filter successful scrapes
            successful_scrapes = [r for r in scraping_results if r.success]
            failed_scrapes = [r for r in scraping_results if not r.success]
            
            if not successful_scrapes:
                analysis_store[analysis_id].update({
                    "status": "failed",
                    "error": "All URLs failed to scrape",
                    "scraping_results": [r.__dict__ for r in scraping_results],
                    "completed_at": datetime.now().isoformat()
                })
                return {
                    "success": False,
                    "analysis_id": analysis_id,
                    "error": "All URLs failed to scrape",
                    "scraping_results": [r.__dict__ for r in scraping_results]
                }
            
            # Update progress
            analysis_store[analysis_id]["progress"] = 30
            analysis_store[analysis_id]["status"] = "analyzing"
            
            # Combine content from all successful scrapes
            combined_content = self._combine_scraped_content(successful_scrapes)
            
            # Validate combined content
            content_validation = guardrails_system.validate_input(
                combined_content,
                input_type="text",
                context="web_content_batch"
            )
            
            if content_validation.triggered and content_validation.action.value == "block":
                analysis_store[analysis_id].update({
                    "status": "failed",
                    "error": "Combined content contains prohibited material",
                    "completed_at": datetime.now().isoformat()
                })
                return {
                    "success": False,
                    "analysis_id": analysis_id,
                    "error": "Content validation failed",
                    "guardrail_result": content_validation.__dict__
                }
            
            # Use sanitized content if needed
            analysis_content = content_validation.sanitized_content or combined_content
            
            # Update progress
            analysis_store[analysis_id]["progress"] = 60
            
            # Run contract analysis
            analysis_results = await self._analyze_content(
                analysis_content,
                "multiple_urls",
                "Combined Legal Content",
                analysis_options
            )
            
            # Update progress
            analysis_store[analysis_id]["progress"] = 90
            
            # Create comprehensive results
            final_results = {
                "analysis_id": analysis_id,
                "type": "web_content_batch",
                "batch_metadata": {
                    "total_urls": len(urls),
                    "successful_scrapes": len(successful_scrapes),
                    "failed_scrapes": len(failed_scrapes),
                    "scraping_stats": web_scraper.get_scraping_stats(scraping_results)
                },
                "individual_results": [
                    {
                        "url": result.url,
                        "title": result.title,
                        "success": result.success,
                        "content_length": len(result.content),
                        "legal_content_detected": web_scraper._contains_legal_content(result.content),
                        "error": result.error if not result.success else None
                    }
                    for result in scraping_results
                ],
                "combined_analysis": analysis_results,
                "guardrail_warnings": [
                    content_validation.message
                ] if content_validation.triggered else [],
                "analysis_completed_at": datetime.now().isoformat()
            }
            
            # Store final results
            analysis_store[analysis_id].update({
                "status": "completed",
                "progress": 100,
                "results": final_results,
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "results": final_results
            }
            
        except Exception as e:
            logger.error(f"Batch web content analysis failed: {str(e)}")
            
            if 'analysis_id' in locals():
                analysis_store = get_analysis_store()
                analysis_store[analysis_id].update({
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now().isoformat()
                })
            
            return {
                "success": False,
                "error": f"Batch analysis failed: {str(e)}"
            }
    
    async def _analyze_content(self, content: str, source: str, title: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze scraped content using contract analysis pipeline"""
        
        try:
            # Create a temporary file-like object for the web content
            import tempfile
            import os
            
            # Create a temporary file with the web content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Run the full contract analysis pipeline using the orchestrator
                analysis_results = await self.orchestrator.analyze_contract(temp_file_path)
                
                # Add web-specific metadata to results
                if "before_sign_report" in analysis_results:
                    analysis_results["before_sign_report"]["web_source"] = source
                    analysis_results["before_sign_report"]["web_title"] = title
                
                # Add web-specific recommendations
                web_recommendations = self._generate_web_recommendations(content, source)
                
                if "recommendations" not in analysis_results:
                    analysis_results["recommendations"] = []
                
                analysis_results["recommendations"].extend(web_recommendations)
                
                return analysis_results
                
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "partial_results": True
            }
    
    def _combine_scraped_content(self, scraping_results: List[WebScrapingResult]) -> str:
        """Combine content from multiple scraping results"""
        
        combined_sections = []
        
        for result in scraping_results:
            if result.success and result.content:
                section = f"""
# {result.title or result.url}

Source: {result.url}
Scraped: {result.scraped_at}

{result.content}

---
"""
                combined_sections.append(section)
        
        return "\n".join(combined_sections)
    
    def _generate_web_recommendations(self, content: str, source: str) -> List[str]:
        """Generate web-specific recommendations"""
        
        recommendations = []
        
        # Check for common web legal issues
        content_lower = content.lower()
        
        # Privacy recommendations
        if "privacy" in content_lower and "gdpr" not in content_lower:
            recommendations.append("Consider adding GDPR compliance mentions for European users")
        
        # Cookie policy recommendations
        if "cookie" in content_lower and "consent" not in content_lower:
            recommendations.append("Add explicit cookie consent mechanism for compliance")
        
        # Data collection transparency
        if "data" in content_lower and "collect" in content_lower and "share" not in content_lower:
            recommendations.append("Clarify how collected data is shared with third parties")
        
        # Jurisdiction recommendations
        if "jurisdiction" not in content_lower and "law" in content_lower:
            recommendations.append("Specify the governing law and jurisdiction for disputes")
        
        # Update frequency recommendations
        if "update" not in content_lower and "change" not in content_lower:
            recommendations.append("Include information about how often terms are updated")
        
        # Contact information
        if "contact" not in content_lower and "email" not in content_lower:
            recommendations.append("Add contact information for legal questions")
        
        return recommendations
    
    def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """Get status of web content analysis"""
        
        analysis_store = get_analysis_store()
        
        if analysis_id not in analysis_store:
            return {
                "error": "Analysis not found",
                "analysis_id": analysis_id
            }
        
        analysis = analysis_store[analysis_id]
        
        return {
            "analysis_id": analysis_id,
            "type": analysis.get("type", "unknown"),
            "status": analysis.get("status", "unknown"),
            "progress": analysis.get("progress", 0),
            "started_at": analysis.get("started_at"),
            "completed_at": analysis.get("completed_at"),
            "urls": analysis.get("urls", []),
            "error": analysis.get("error"),
            "results": analysis.get("results") if analysis.get("status") == "completed" else None
        }
    
    def get_analysis_results(self, analysis_id: str) -> Dict[str, Any]:
        """Get complete results of web content analysis"""
        
        analysis_store = get_analysis_store()
        
        if analysis_id not in analysis_store:
            return {
                "error": "Analysis not found",
                "analysis_id": analysis_id
            }
        
        analysis = analysis_store[analysis_id]
        
        if analysis.get("status") != "completed":
            return {
                "error": "Analysis not completed",
                "analysis_id": analysis_id,
                "status": analysis.get("status"),
                "progress": analysis.get("progress", 0)
            }
        
        return analysis["results"]
    
    async def detect_legal_content_type(self, url: str) -> Dict[str, Any]:
        """Detect the type of legal content on a webpage"""
        
        try:
            # Quick scrape with minimal content
            scraping_result = await web_scraper.scrape_url(
                url, 
                {"formats": ["markdown"], "onlyMainContent": True}
            )
            
            if not scraping_result.success:
                return {
                    "success": False,
                    "error": scraping_result.error,
                    "url": url
                }
            
            # Analyze content type
            content_lower = scraping_result.content.lower()
            title_lower = scraping_result.title.lower()
            url_lower = url.lower()
            
            detected_types = []
            confidence_scores = {}
            
            # Check for different legal document types
            type_patterns = {
                "terms_of_service": [
                    "terms of service", "terms and conditions", "terms of use",
                    "service terms", "user terms", "user agreement"
                ],
                "privacy_policy": [
                    "privacy policy", "privacy statement", "data protection",
                    "privacy notice", "information privacy"
                ],
                "cookie_policy": [
                    "cookie policy", "cookie notice", "cookie consent",
                    "cookie usage", "cookie information"
                ],
                "user_agreement": [
                    "user agreement", "platform agreement", "community guidelines",
                    "acceptable use", "user conduct"
                ],
                "disclaimer": [
                    "disclaimer", "legal disclaimer", "liability disclaimer",
                    "use disclaimer", "content disclaimer"
                ],
                "data_processing": [
                    "data processing", "data processing agreement", "dpa",
                    "processor agreement", "data controller"
                ]
            }
            
            for doc_type, patterns in type_patterns.items():
                score = 0
                
                # Check URL
                for pattern in patterns:
                    if pattern.replace(' ', '-') in url_lower:
                        score += 3
                    elif pattern.replace(' ', '_') in url_lower:
                        score += 3
                
                # Check title
                for pattern in patterns:
                    if pattern in title_lower:
                        score += 5
                
                # Check content
                for pattern in patterns:
                    if pattern in content_lower:
                        score += 2
                
                if score > 0:
                    detected_types.append(doc_type)
                    confidence_scores[doc_type] = min(score / 10, 1.0)  # Normalize to 0-1
            
            # Sort by confidence
            detected_types.sort(key=lambda x: confidence_scores[x], reverse=True)
            
            return {
                "success": True,
                "url": url,
                "title": scraping_result.title,
                "detected_types": detected_types,
                "confidence_scores": confidence_scores,
                "primary_type": detected_types[0] if detected_types else None,
                "content_length": len(scraping_result.content),
                "legal_content_detected": web_scraper._contains_legal_content(scraping_result.content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Content type detection failed: {str(e)}",
                "url": url
            }

# Global analyzer instance
web_analyzer = WebContentAnalyzer()
