# 📚 API Documentation

Complete RESTful API documentation for the AI Contract Risk Detector backend service.

## 📋 **Table of Contents**

- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (get free at https://console.groq.com)

### Setup

1. **Clone and navigate to backend:**
```bash
git clone https://github.com/lemessaA/ai-contract-risk-detector.git
cd ai-contract-risk-detector/backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure API key:**
```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

5. **Start the API server:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

---

## 🔐 Authentication

Currently, the API operates without authentication but includes comprehensive security guardrails and rate limiting.

### Security Headers
All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Rate Limiting
- **Default**: 100 requests/minute per IP
- **Upload**: 10 uploads/minute per IP
- **Analysis**: 5 analyses/minute per IP
- **Chat**: 30 requests/minute per IP

---

## 🌐 Base URL

```
http://localhost:8000/api
```

### Health Check
```bash
GET /health
```

**Response**:
```json
{
  "message": "AI Contract Risk Detector API",
  "version": "1.0.0",
  "status": "running",
  "groq_configured": true
}
```

---

## 📡 API Endpoints

### 📄 Contract Analysis

#### Upload and Analyze Contract
```http
POST /api/analyze-contract
Content-Type: multipart/form-data
```

**Parameters**:
- `file` (required): Contract file (PDF, DOCX, or TXT)

**Response**:
```json
{
  "analysis_id": "uuid-string",
  "status": "processing",
  "message": "Contract analysis started"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/analyze-contract" \
  -F "file=@contract.pdf"
```

#### Get Analysis Status
```http
GET /api/analysis/{analysis_id}/status
```

**Response**:
```json
{
  "analysis_id": "uuid-string",
  "status": "completed|processing|failed",
  "progress": 100,
  "message": "Analysis completed successfully"
}
```

#### Get Analysis Results
```http
GET /api/analysis/{analysis_id}/results
```

**Response**:
```json
{
  "analysis_id": "uuid-string",
  "status": "completed",
  "results": {
    "document_parsed": {
      "text": "Extracted contract text...",
      "word_count": 1500
    },
    "clauses_extracted": {
      "clauses": [
        {
          "text": "Payment shall be made within 30 days...",
          "type": "Payment Terms",
          "importance": "High"
        }
      ]
    },
    "risks_analyzed": {
      "risk_analyses": [
        {
          "clause_text": "Payment shall be made within 30 days...",
          "risk_level": "Medium",
          "risk_explanation": "30-day payment terms may impact cash flow...",
          "suggestions": ["Consider shorter payment terms"]
        }
      ]
    },
    "compliance_checked": {
      "overall_compliance": "Good",
      "missing_clauses": [],
      "compliance_score": 85
    },
    "before_sign_report": {
      "summary": "This contract appears generally favorable...",
      "top_risks": [
        {
          "rank": 1,
          "clause": "Payment Terms",
          "risk": "Medium",
          "explanation": "30-day terms may affect cash flow"
        }
      ]
    }
  }
}
```

---

### 🤖 AI Chat

#### Ask Question About Contract
```http
POST /api/ai-chat/ask
Content-Type: application/x-www-form-urlencoded
```

**Parameters**:
- `question` (required): User's question about the contract
- `contract_text` (optional): Full contract text for context
- `analysis_id` (optional): Analysis ID for context

**Response**:
```json
{
  "success": true,
  "question": "What are the payment terms?",
  "answer": "Based on the contract, payment terms specify...",
  "context_used": true,
  "guardrail_triggered": false,
  "warnings": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/ai-chat/ask" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the key risks in this contract?"
```

#### Explain Specific Clause
```http
POST /api/ai-chat/explain-clause
Content-Type: application/x-www-form-urlencoded
```

**Parameters**:
- `clause_text` (required): Clause text to explain
- `analysis_id` (optional): Analysis ID for context

**Response**:
```json
{
  "success": true,
  "clause_text": "Payment shall be made within 30 days...",
  "explanation": "This clause establishes that payments...",
  "risks": ["Cash flow impact", "Late payment penalties"],
  "suggestions": ["Consider 15-day terms for better cash flow"],
  "guardrail_triggered": false
}
```

---

### 🔄 Version Comparison

#### Compare Contract Texts
```http
POST /api/version-comparison/compare-texts
Content-Type: application/x-www-form-urlencoded
```

**Parameters**:
- `original_text` (required): Original contract text
- `modified_text` (required): Modified contract text
- `version_labels` (optional): Labels for versions (default: "Original", "Modified")

**Response**:
```json
{
  "success": true,
  "version_labels": ["Original", "Modified"],
  "text_diff": {
    "diff_text": "--- Original\n+++ Modified\n@@ -1 +1 @@\n-Service Provider agrees to provide software\n+Service Provider agrees to provide custom software and consulting",
    "has_changes": true,
    "lines_added": 1,
    "lines_removed": 1,
    "lines_modified": 1
  },
  "ai_analysis": {
    "ai_analysis": "The modified version expands the scope...",
    "analysis_type": "comprehensive_change_analysis"
  },
  "clause_changes": {
    "added_clauses": [],
    "removed_clauses": [],
    "modified_clauses": [],
    "total_changes": 0
  },
  "similarity_score": 0.85,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/api/version-comparison/compare-texts" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "original_text=Service Provider agrees to provide software" \
  -d "modified_text=Service Provider agrees to provide custom software and consulting"
```

---

### 📊 Reports

#### Get Available Report Formats
```http
GET /api/reports/available-formats
```

**Response**:
```json
{
  "formats": {
    "pdf": {
      "name": "PDF",
      "description": "Portable Document Format - Best for printing and sharing",
      "available": true,
      "mime_type": "application/pdf"
    },
    "html": {
      "name": "HTML",
      "description": "Web page format - Interactive and viewable in browsers",
      "available": true,
      "mime_type": "text/html"
    },
    "json": {
      "name": "JSON",
      "description": "Data format - For integration and analysis",
      "available": true,
      "mime_type": "application/json"
    },
    "word": {
      "name": "RTF (Word-compatible)",
      "description": "Rich Text Format - Compatible with Microsoft Word",
      "available": true,
      "mime_type": "application/rtf"
    }
  },
  "total_formats": 4
}
```

#### Generate Specific Report Format
```http
POST /api/reports/generate/{analysis_id}
Content-Type: application/x-www-form-urlencoded
```

**Parameters**:
- `format` (required): Report format (pdf, html, json, rtf)
- `filename` (optional): Custom filename (without extension)

**Response**:
```json
{
  "success": true,
  "format": "pdf",
  "filename": "contract_analysis_2024-01-15.pdf",
  "download_url": "/api/reports/download/uuid-string",
  "file_size": 1024000,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### Generate All Report Formats
```http
POST /api/reports/generate-all/{analysis_id}
Content-Type: application/x-www-form-urlencoded
```

**Parameters**:
- `base_filename` (optional): Base filename for all reports

**Response**:
```json
{
  "success": true,
  "reports": {
    "pdf": {
      "filename": "contract_analysis.pdf",
      "download_url": "/api/reports/download/pdf-uuid",
      "file_size": 1024000
    },
    "html": {
      "filename": "contract_analysis.html",
      "download_url": "/api/reports/download/html-uuid",
      "file_size": 512000
    },
    "json": {
      "filename": "contract_analysis.json",
      "download_url": "/api/reports/download/json-uuid",
      "file_size": 256000
    },
    "rtf": {
      "filename": "contract_analysis.rtf",
      "download_url": "/api/reports/download/rtf-uuid",
      "file_size": 768000
    }
  },
  "total_reports": 4,
  "generated_at": "2024-01-15T10:30:00Z"
}
```

#### Download Report
```http
GET /api/reports/download/{report_id}
```

**Response**: File download with appropriate MIME type

---

## ❌ Error Handling

### Error Response Format

All errors return consistent JSON format:

```json
{
  "detail": [
    {
      "type": "validation_error",
      "loc": ["body", "file"],
      "msg": "Field required",
      "input": null
    }
  ]
}
```

### Common Error Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| 400 | Bad Request | Missing required fields |
| 404 | Not Found | Analysis ID doesn't exist |
| 413 | Payload Too Large | File exceeds size limit |
| 415 | Unsupported Media Type | Invalid file format |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | System error |

### Guardrail Errors

When guardrails are triggered, responses include additional context:

```json
{
  "success": false,
  "error": "Input contains prohibited content",
  "guardrail_triggered": true,
  "risk_level": "high"
}
```

---

## ⚡ Rate Limiting

### Limits by Endpoint

| Endpoint Type | Limit | Duration |
|---------------|-------|----------|
| Default | 100 requests | 1 minute |
| File Upload | 10 uploads | 1 minute |
| Contract Analysis | 5 analyses | 1 minute |
| AI Chat | 30 requests | 1 minute |

### Rate Limit Headers

Responses include rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

### Exceeded Limits

When limits are exceeded:

```json
{
  "error": "Rate limit exceeded. Please try again later.",
  "guardrail_triggered": true,
  "risk_level": "medium"
}
```

---

## 💡 Examples

### Complete Workflow Example

#### 1. Upload and Analyze Contract
```bash
# Upload contract
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/analyze-contract" \
  -F "file=@sample_contract.pdf")

ANALYSIS_ID=$(echo $UPLOAD_RESPONSE | jq -r '.analysis_id')
echo "Analysis ID: $ANALYSIS_ID"
```

#### 2. Check Analysis Status
```bash
# Check status
while true; do
  STATUS=$(curl -s "http://localhost:8000/api/analysis/$ANALYSIS_ID/status" | jq -r '.status')
  echo "Status: $STATUS"
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  
  sleep 2
done
```

#### 3. Get Results
```bash
# Get full results
curl -s "http://localhost:8000/api/analysis/$ANALYSIS_ID/results" | jq .
```

#### 4. Ask Questions
```bash
# Ask about specific risks
curl -X POST "http://localhost:8000/api/ai-chat/ask" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the top 3 risks in this contract?" \
  -d "analysis_id=$ANALYSIS_ID"
```

#### 5. Generate Reports
```bash
# Generate all report formats
curl -X POST "http://localhost:8000/api/reports/generate-all/$ANALYSIS_ID" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "base_filename=my_contract_analysis"
```

### Python Integration Example

```python
import requests
import json
import time

class ContractAnalyzerAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def analyze_contract(self, file_path):
        """Upload and analyze a contract"""
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/api/analyze-contract",
                files={"file": f}
            )
        
        return response.json()
    
    def get_analysis_results(self, analysis_id):
        """Get analysis results"""
        response = requests.get(f"{self.base_url}/api/analysis/{analysis_id}/results")
        return response.json()
    
    def ask_question(self, question, analysis_id=None):
        """Ask AI chat a question"""
        data = {"question": question}
        if analysis_id:
            data["analysis_id"] = analysis_id
        
        response = requests.post(
            f"{self.base_url}/api/ai-chat/ask",
            data=data
        )
        return response.json()
    
    def compare_versions(self, original_text, modified_text):
        """Compare two contract versions"""
        data = {
            "original_text": original_text,
            "modified_text": modified_text
        }
        
        response = requests.post(
            f"{self.base_url}/api/version-comparison/compare-texts",
            data=data
        )
        return response.json()
    
    def generate_reports(self, analysis_id, formats=None):
        """Generate reports in specified formats"""
        if formats is None:
            # Generate all formats
            response = requests.post(
                f"{self.base_url}/api/reports/generate-all/{analysis_id}"
            )
        else:
            # Generate specific format
            response = requests.post(
                f"{self.base_url}/api/reports/generate/{analysis_id}",
                data={"format": formats}
            )
        
        return response.json()

# Usage example
api = ContractAnalyzerAPI()

# Analyze contract
result = api.analyze_contract("contract.pdf")
analysis_id = result["analysis_id"]

# Wait for completion
time.sleep(10)

# Get results
results = api.get_analysis_results(analysis_id)

# Ask questions
answer = api.ask_question("What are the payment terms?", analysis_id)

# Generate reports
reports = api.generate_reports(analysis_id)
```

---

## 📊 API Status

### Current Version
- **Version**: 1.0.0
- **Status**: Production Ready
- **Guardrails**: Active (87.3% test coverage)
- **Security**: Enterprise-grade

### Supported Features
- ✅ Contract analysis
- ✅ AI chat
- ✅ Version comparison
- ✅ Report generation
- ✅ Security guardrails
- ✅ Rate limiting
- ✅ Audit logging

### Performance Metrics
- **Average response time**: < 2 seconds
- **File size limit**: 10MB
- **Supported formats**: PDF, DOCX, TXT
- **Report formats**: PDF, HTML, JSON, RTF

For more information, visit the [GitHub repository](https://github.com/lemessaA/ai-contract-risk-detector).
