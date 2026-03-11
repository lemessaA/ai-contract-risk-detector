# 🌐 Web Content Contract Analyzer

## 📋 **Overview**

The Web Content Contract Analyzer allows users to analyze legal content directly from websites using **Firecrawl** for web scraping and the existing contract analysis pipeline. This feature extends the AI Contract Risk Detector to work with online legal documents without requiring file uploads.

## 🎯 **Key Features**

### **🌍 Website Analysis**
- **URL-based Analysis**: Analyze legal content directly from any website
- **Firecrawl Integration**: Professional web scraping with Firecrawl API
- **Fallback Scraping**: Built-in scraper using BeautifulSoup and aiohttp
- **Content Detection**: Automatically identify document types (Terms of Service, Privacy Policy, etc.)

### **🔍 Content Type Detection**
- **Smart Classification**: Detects Terms of Service, Privacy Policies, Cookie Policies, User Agreements, etc.
- **Confidence Scoring**: Provides confidence levels for content type detection
- **Legal Content Identification**: Identifies whether the page contains legal content

### **⚙️ Advanced Analysis**
- **Contract Analysis Pipeline**: Uses existing multi-agent analysis system
- **Risk Assessment**: Identifies potential risks in web-based legal content
- **Compliance Checking**: Verifies regulatory compliance
- **Before You Sign Report**: Generates user-friendly summaries

### **🛡️ Security & Guardrails**
- **URL Validation**: Validates URLs and blocks malicious sites
- **Content Filtering**: Applies input/output guardrails to scraped content
- **Rate Limiting**: Prevents abuse with proper rate limiting
- **Sensitive Data Protection**: Redacts sensitive information from scraped content

---

## 🚀 **Use Cases**

### **📄 Terms of Service Analysis**
```bash
curl -X POST "http://localhost:8000/api/web-content/analyze-web-content" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/terms-of-service"}'
```

### **🔒 Privacy Policy Review**
```bash
curl -X POST "http://localhost:8000/api/web-content/analyze-web-content" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/privacy"}'
```

### **📱 Platform Agreement Analysis**
```bash
curl -X POST "http://localhost:8000/api/web-content/analyze-web-content" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://platform.example.com/user-agreement"}'
```

### **🔄 Multiple URL Analysis**
```bash
curl -X POST "http://localhost:8000/api/web-content/analyze-multiple-urls" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/terms",
      "https://example.com/privacy",
      "https://example.com/cookie-policy"
    ]
  }'
```

---

## 📡 **API Endpoints**

### **🔍 Content Type Detection**
```http
POST /api/web-content/detect-content-type
```

**Request Body:**
```json
{
  "url": "https://example.com/terms-of-service"
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://example.com/terms-of-service",
  "title": "Terms of Service",
  "detected_types": ["terms_of_service", "user_agreement"],
  "confidence_scores": {
    "terms_of_service": 0.95,
    "user_agreement": 0.7
  },
  "primary_type": "terms_of_service",
  "content_length": 15420,
  "legal_content_detected": true
}
```

### **📊 Single URL Analysis**
```http
POST /api/web-content/analyze-web-content
```

**Request Body:**
```json
{
  "url": "https://example.com/terms-of-service",
  "analysis_options": {
    "include_recommendations": true,
    "risk_threshold": "medium"
  }
}
```

**Response:**
```json
{
  "message": "Web content analysis started successfully",
  "analysis_id": "uuid-string",
  "url": "https://example.com/terms-of-service",
  "status": "processing"
}
```

### **🔄 Multiple URL Analysis**
```http
POST /api/web-content/analyze-multiple-urls
```

**Request Body:**
```json
{
  "urls": [
    "https://example.com/terms",
    "https://example.com/privacy"
  ],
  "analysis_options": {
    "combine_results": true
  }
}
```

### **📈 Analysis Status**
```http
GET /api/web-content/web-analysis/{analysis_id}/status
```

**Response:**
```json
{
  "analysis_id": "uuid-string",
  "type": "web_content",
  "status": "completed",
  "progress": 100,
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z",
  "urls": ["https://example.com/terms"]
}
```

### **📋 Analysis Results**
```http
GET /api/web-content/web-analysis/{analysis_id}/results
```

**Response:**
```json
{
  "analysis_id": "uuid-string",
  "type": "web_content",
  "web_metadata": {
    "url": "https://example.com/terms-of-service",
    "title": "Terms of Service",
    "scraped_at": "2024-01-15T10:30:00Z",
    "content_length": 15420,
    "legal_content_detected": true
  },
  "contract_analysis": {
    "document_parsed": {...},
    "clauses_extracted": {...},
    "risks_analyzed": {...},
    "compliance_checked": {...},
    "before_sign_report": {...}
  },
  "guardrail_warnings": [],
  "analysis_completed_at": "2024-01-15T10:32:15Z"
}
```

---

## 🛠️ **Technical Implementation**

### **🔧 Web Scraper Service**

#### **Firecrawl Integration**
```python
# Uses Firecrawl API for professional scraping
async def _scrape_with_firecrawl(self, url: str, options: Dict[str, Any] = None):
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
```

#### **Fallback Scraper**
```python
# Built-in scraper using BeautifulSoup and aiohttp
async def _scrape_fallback(self, url: str, options: Dict[str, Any] = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            # Extract and clean content
```

### **🤖 Content Analyzer Service**

#### **Analysis Pipeline**
```python
async def analyze_web_content(self, url: str, options: Dict[str, Any] = None):
    # 1. Scrape web content
    scraping_result = await web_scraper.scrape_url(url, options)
    
    # 2. Validate with guardrails
    content_validation = guardrails_system.validate_input(
        scraping_result.content, "text", "web_content"
    )
    
    # 3. Run contract analysis
    analysis_results = await self._analyze_content(
        analysis_content, url, scraping_result.title
    )
    
    # 4. Combine results
    final_results = {
        "web_metadata": {...},
        "contract_analysis": analysis_results,
        "guardrail_warnings": [...]
    }
```

#### **Legal Content Detection**
```python
def _is_likely_legal_content(self, url: str) -> bool:
    legal_keywords = [
        "terms of service", "privacy policy", "user agreement",
        "terms and conditions", "legal notice", "disclaimer"
    ]
    
    url_lower = url.lower()
    return any(keyword.replace(' ', '-') in url_lower for keyword in legal_keywords)
```

---

## 🎨 **Frontend Component**

### **📱 React Component Features**

#### **Web Content Analyzer Interface**
```typescript
// Main component with URL input, content detection, and results display
export default function WebContentAnalyzer() {
  const [url, setUrl] = useState('');
  const [analysisResult, setAnalysisResult] = useState<WebAnalysisResult | null>(null);
  const [contentType, setContentType] = useState<ContentTypeDetection | null>(null);
  
  // Content type detection
  const detectContentType = async () => { ... };
  
  // Full analysis
  const analyzeWebContent = async () => { ... };
  
  // Progress polling
  const pollAnalysisResults = async (id: string) => { ... };
}
```

#### **Key UI Features**
- **URL Input**: Validated URL input field
- **Content Type Detection**: Quick detection before full analysis
- **Progress Tracking**: Real-time progress updates
- **Results Display**: Tabbed interface for different analysis aspects
- **Risk Visualization**: Color-coded risk levels and badges
- **Export Options**: Download and copy functionality

### **🎯 User Experience**

#### **Workflow**
1. **Enter URL**: User inputs website URL
2. **Detect Type**: Optional content type detection
3. **Start Analysis**: Begin full contract analysis
4. **Monitor Progress**: Real-time progress updates
5. **View Results**: Comprehensive analysis results
6. **Export Reports**: Download or share findings

#### **Visual Design**
- **Modern Interface**: Clean, professional design
- **Responsive Layout**: Works on desktop and mobile
- **Interactive Elements**: Expandable sections, tabs, badges
- **Status Indicators**: Progress bars, status badges
- **Error Handling**: User-friendly error messages

---

## 🔧 **Configuration**

### **🔑 Environment Variables**

```bash
# Firecrawl API (optional but recommended)
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Existing variables
GROQ_API_KEY=your_groq_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
```

### **⚙️ Scraper Configuration**

```python
# Web scraper settings
MAX_CONTENT_LENGTH = 100000  # 100KB per URL
MAX_URLS_PER_ANALYSIS = 5
TIMEOUT_SECONDS = 30

# Legal content indicators
LEGAL_KEYWORDS = [
    "terms of service", "privacy policy", "user agreement",
    "terms and conditions", "legal notice", "disclaimer"
]

# Risk indicators
RISK_INDICATORS = [
    "liability", "limitation", "indemnification", "warranty",
    "dispute resolution", "arbitration", "jurisdiction"
]
```

### **🛡️ Security Settings**

```python
# Guardrails configuration
WEB_CONTENT_VALIDATION = {
    "max_url_length": 2048,
    "allowed_schemes": ["http", "https"],
    "blocked_domains": [],
    "content_sanitization": True
}
```

---

## 📊 **Performance & Scaling**

### **⚡ Performance Features**

#### **Concurrent Processing**
- **Async Operations**: All web scraping and analysis is asynchronous
- **Batch Processing**: Multiple URLs can be analyzed concurrently
- **Resource Management**: Proper timeout and resource limits

#### **Caching Strategy**
- **Content Caching**: Cache scraped content to avoid re-scraping
- **Result Caching**: Cache analysis results for repeated URLs
- **Rate Limiting**: Prevent abuse with proper rate limiting

### **📈 Scaling Considerations**

#### **Horizontal Scaling**
- **Stateless Design**: Easy to scale across multiple instances
- **Load Balancing**: Distribute requests across multiple servers
- **Database Integration**: Persistent storage for analysis results

#### **Resource Optimization**
- **Memory Management**: Limit content size and processing
- **Connection Pooling**: Reuse HTTP connections
- **Background Processing**: Long-running analyses in background

---

## 🔍 **Monitoring & Analytics**

### **📊 Usage Metrics**

#### **Analysis Statistics**
```python
# Available via API endpoint
GET /api/web-content/web-analysis/stats

# Response includes:
{
  "total_analyses": 1250,
  "completed_analyses": 1180,
  "success_rate": 94.4,
  "total_urls_analyzed": 3420,
  "common_content_types": {
    "terms_of_service": 450,
    "privacy_policy": 380,
    "cookie_policy": 220
  }
}
```

#### **Performance Metrics**
- **Response Times**: Track API response times
- **Success Rates**: Monitor analysis success rates
- **Error Rates**: Track and categorize errors
- **Resource Usage**: Monitor memory and CPU usage

### **🐛 Error Handling**

#### **Common Errors**
- **Invalid URLs**: Malformed or unreachable URLs
- **Scraping Failures**: Websites blocking scrapers
- **Content Validation**: Guardrails blocking content
- **Analysis Errors**: Contract analysis failures

#### **Error Recovery**
- **Retry Logic**: Automatic retries for transient failures
- **Fallback Mechanisms**: Alternative scraping methods
- **Graceful Degradation**: Partial results when possible
- **User Notifications**: Clear error messages

---

## 🚀 **Deployment**

### **🐳 Docker Configuration**

```dockerfile
# Add web scraping dependencies
RUN pip install aiohttp beautifulsoup4 lxml

# Environment variables
ENV FIRECRAWL_API_KEY=""
ENV MAX_WEB_CONTENT_LENGTH=100000
```

### **🔄 Production Setup**

#### **Required Services**
- **Firecrawl API**: Optional but recommended for better scraping
- **Backend API**: FastAPI server with web content routes
- **Frontend**: React component for user interface

#### **Monitoring**
- **Health Checks**: Monitor scraper and analysis health
- **Performance Metrics**: Track response times and success rates
- **Error Logging**: Comprehensive error tracking
- **Usage Analytics**: Track popular content types and URLs

---

## 🎯 **Best Practices**

### **📋 Usage Guidelines**

#### **Recommended URLs**
- **Legal Pages**: Terms of Service, Privacy Policies, User Agreements
- **Platform Policies**: Community Guidelines, Acceptable Use Policies
- **Compliance Documents**: Cookie Policies, Data Processing Agreements

#### **URL Preparation**
- **Direct Links**: Use direct links to legal pages
- **Mobile Versions**: Prefer desktop versions for better content
- **Language**: Works best with English-language content

### **🛡️ Security Considerations**

#### **URL Validation**
- **Scheme Check**: Only allow HTTP/HTTPS URLs
- **Domain Filtering**: Block known malicious domains
- **Length Limits**: Prevent excessively long URLs

#### **Content Security**
- **Input Sanitization**: Clean scraped content before analysis
- **Output Filtering**: Apply output guardrails to results
- **Rate Limiting**: Prevent abuse and resource exhaustion

---

## 📈 **Future Enhancements**

### **🔮 Planned Features**

#### **Advanced Scraping**
- **JavaScript Rendering**: Handle dynamic content
- **Authentication**: Support for password-protected pages
- **Multi-language**: Support for non-English content
- **PDF Detection**: Auto-detect and analyze PDF links

#### **Enhanced Analysis**
- **Industry-Specific**: Tailored analysis for different industries
- **Regulatory Updates**: Keep up with changing regulations
- **Comparative Analysis**: Compare similar policies across sites
- **Historical Tracking**: Track changes to legal documents over time

#### **User Experience**
- **Browser Extension**: Direct analysis from browser
- **Mobile App**: Native mobile application
- **API Integrations**: Third-party integrations
- **Batch Processing**: Bulk URL analysis tools

---

## 🎉 **Summary**

The Web Content Contract Analyzer extends the AI Contract Risk Detector to work with online legal documents, providing:

- **🌐 URL-based Analysis**: Analyze legal content directly from websites
- **🔍 Smart Detection**: Automatic content type identification
- **⚙️ Professional Scraping**: Firecrawl integration with fallback
- **🛡️ Security First**: Comprehensive guardrails and validation
- **📊 Rich Analysis**: Full contract analysis pipeline applied to web content
- **🎨 Modern UI**: Intuitive React component interface
- **📈 Scalable**: Production-ready architecture with monitoring

This feature makes it easy for users to quickly analyze legal content from any website without downloading files, making contract risk assessment more accessible and efficient. 🚀
