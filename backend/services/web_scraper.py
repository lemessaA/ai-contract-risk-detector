"""
Web Content Scraper Service
Uses Firecrawl to scrape legal content from websites for contract analysis
"""

import os
import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from urllib.parse import urlparse, urljoin
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

@dataclass
class WebScrapingResult:
    """Result from web content scraping"""
    success: bool
    url: str
    title: str = ""
    content: str = ""
    metadata: Dict[str, Any] = None
    error: str = ""
    scraped_at: str = ""

class WebContentScraper:
    """Web content scraper using Firecrawl API"""
    
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.firecrawl_base_url = "https://api.firecrawl.dev/v1"
        self.timeout = 30
        self.max_content_length = 100000  # 100KB max
        
        # Legal content indicators
        self.legal_keywords = [
            "terms of service", "privacy policy", "user agreement", 
            "terms and conditions", "legal notice", "disclaimer",
            "cookie policy", "data protection", "privacy statement",
            "terms of use", "service agreement", "platform policy",
            "community guidelines", "acceptable use", "user terms"
        ]
        
        # Risk clause indicators
        self.risk_indicators = [
            "liability", "limitation", "indemnification", "warranty",
            "dispute resolution", "arbitration", "jurisdiction",
            "termination", "cancellation", "refund", "payment",
            "data collection", "third party", "subpoena", "compliance"
        ]
    
    async def scrape_url(self, url: str, options: Dict[str, Any] = None) -> WebScrapingResult:
        """
        Scrape content from a URL using Firecrawl
        
        Args:
            url: URL to scrape
            options: Additional scraping options
            
        Returns:
            WebScrapingResult with scraped content
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return WebScrapingResult(
                    success=False,
                    url=url,
                    error="Invalid URL format"
                )
            
            # Check if it's a legal content page
            if not self._is_likely_legal_content(url):
                logger.warning(f"URL may not contain legal content: {url}")
            
            # Use Firecrawl API
            if self.firecrawl_api_key:
                return await self._scrape_with_firecrawl(url, options)
            else:
                # Fallback to simple scraping
                return await self._scrape_fallback(url, options)
                
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return WebScrapingResult(
                success=False,
                url=url,
                error=f"Scraping failed: {str(e)}"
            )
    
    async def _scrape_with_firecrawl(self, url: str, options: Dict[str, Any] = None) -> WebScrapingResult:
        """Scrape using Firecrawl API"""
        
        headers = {
            "Authorization": f"Bearer {self.firecrawl_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "formats": ["markdown"],
            "includeTags": ["h1", "h2", "h3", "p", "li", "div"],
            "excludeTags": ["script", "style", "nav", "footer", "header"],
            "onlyMainContent": True,
            "waitFor": 2000
        }
        
        if options:
            payload.update(options)
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(
                f"{self.firecrawl_base_url}/scrape",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return WebScrapingResult(
                        success=False,
                        url=url,
                        error=f"Firecrawl API error: {response.status} - {error_text}"
                    )
                
                result = await response.json()
                
                if not result.get("success", False):
                    return WebScrapingResult(
                        success=False,
                        url=url,
                        error=f"Firecrawl scraping failed: {result.get('error', 'Unknown error')}"
                    )
                
                # Extract content
                markdown_content = result.get("markdown", "")
                metadata = result.get("metadata", {})
                
                # Clean and process content
                cleaned_content = self._clean_scraped_content(markdown_content)
                
                # Extract title
                title = metadata.get("title", "") or self._extract_title_from_content(cleaned_content)
                
                return WebScrapingResult(
                    success=True,
                    url=url,
                    title=title,
                    content=cleaned_content,
                    metadata=metadata,
                    scraped_at=self._get_timestamp()
                )
    
    async def _scrape_fallback(self, url: str, options: Dict[str, Any] = None) -> WebScrapingResult:
        """Fallback scraping using simple HTTP request and BeautifulSoup"""
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        return WebScrapingResult(
                            success=False,
                            url=url,
                            error=f"HTTP error: {response.status}"
                        )
                    
                    html_content = await response.text()
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract title
                    title = soup.find('title')
                    title_text = title.get_text().strip() if title else ""
                    
                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                        element.decompose()
                    
                    # Extract main content
                    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article'))
                    
                    if main_content:
                        content = main_content.get_text(separator='\n', strip=True)
                    else:
                        # Fallback to body content
                        body = soup.find('body')
                        content = body.get_text(separator='\n', strip=True) if body else ""
                    
                    # Clean content
                    cleaned_content = self._clean_scraped_content(content)
                    
                    return WebScrapingResult(
                        success=True,
                        url=url,
                        title=title_text,
                        content=cleaned_content,
                        metadata={"method": "fallback"},
                        scraped_at=self._get_timestamp()
                    )
                    
        except Exception as e:
            return WebScrapingResult(
                success=False,
                url=url,
                error=f"Fallback scraping failed: {str(e)}"
            )
    
    def _clean_scraped_content(self, content: str) -> str:
        """Clean and normalize scraped content"""
        
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove markdown artifacts
        content = re.sub(r'\[.*?\]\(.*?\)', '', content)  # Remove markdown links
        content = re.sub(r'[#*_`]', '', content)  # Remove markdown formatting
        
        # Remove common non-legal content
        non_legal_patterns = [
            r'cookie consent',
            r'subscribe to newsletter',
            r'follow us on',
            r'social media',
            r'copyright ©\s*\d{4}',
            r'all rights reserved',
            r'powered by',
            r'click here',
            r'learn more',
            r'read more'
        ]
        
        for pattern in non_legal_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Focus on legal sections
        legal_sections = []
        
        # Split by common section indicators
        sections = re.split(r'\n(?=\d+\.|\n[A-Z][A-Z\s]{5,}|\n[A-Z][a-z]+\s+[A-Z][a-z]+:)', content)
        
        for section in sections:
            # Check if section contains legal content
            if any(keyword.lower() in section.lower() for keyword in self.legal_keywords + self.risk_indicators):
                legal_sections.append(section.strip())
        
        # If no clear legal sections found, use the full content (but limit length)
        if not legal_sections:
            legal_content = content[:self.max_content_length]
        else:
            legal_content = '\n\n'.join(legal_sections)
            legal_content = legal_content[:self.max_content_length]
        
        return legal_content.strip()
    
    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from content"""
        lines = content.split('\n')
        
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                # Skip if it looks like a sentence (contains period)
                if '.' not in line or line.count('.') > 1:
                    continue
                
                # Check if it contains legal keywords
                if any(keyword.lower() in line.lower() for keyword in self.legal_keywords):
                    return line
        
        return ""
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _is_likely_legal_content(self, url: str) -> bool:
        """Check if URL likely contains legal content"""
        url_lower = url.lower()
        
        # Check URL path for legal indicators
        for keyword in self.legal_keywords:
            if keyword.replace(' ', '-') in url_lower or keyword.replace(' ', '_') in url_lower:
                return True
        
        # Check common legal page patterns
        legal_patterns = [
            r'/terms',
            r'/privacy',
            r'/legal',
            r'/policy',
            r'/agreement',
            r'/conditions',
            r'/guidelines'
        ]
        
        for pattern in legal_patterns:
            if re.search(pattern, url_lower):
                return True
        
        return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def batch_scrape(self, urls: List[str], options: Dict[str, Any] = None) -> List[WebScrapingResult]:
        """Scrape multiple URLs concurrently"""
        
        tasks = [self.scrape_url(url, options) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(WebScrapingResult(
                    success=False,
                    url=urls[i],
                    error=f"Batch scraping error: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_scraping_stats(self, results: List[WebScrapingResult]) -> Dict[str, Any]:
        """Get statistics from scraping results"""
        
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        total_content_length = sum(len(r.content) for r in successful)
        avg_content_length = total_content_length / len(successful) if successful else 0
        
        return {
            "total_urls": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": (len(successful) / len(results) * 100) if results else 0,
            "total_content_length": total_content_length,
            "average_content_length": avg_content_length,
            "legal_content_detected": len([r for r in successful if self._contains_legal_content(r.content)])
        }
    
    def _contains_legal_content(self, content: str) -> bool:
        """Check if content contains legal terms"""
        if not content:
            return False
        
        content_lower = content.lower()
        
        # Count legal keywords
        legal_keyword_count = sum(1 for keyword in self.legal_keywords if keyword in content_lower)
        risk_indicator_count = sum(1 for indicator in self.risk_indicators if indicator in content_lower)
        
        # Consider it legal content if it has enough indicators
        return (legal_keyword_count >= 2) or (risk_indicator_count >= 3)

# Global scraper instance
web_scraper = WebContentScraper()
