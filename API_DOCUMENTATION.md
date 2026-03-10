# AI Contract Risk Detector - Backend API Service

A comprehensive RESTful API service for contract risk analysis powered by Groq LLM and multi-agent AI system. This API allows developers to integrate intelligent contract analysis into their applications.

## 🚀 Quick Start for Developers

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

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
Currently no authentication required (for development). Add your API key in `.env` file.

## 🔌 Core API Endpoints

### Contract Analysis

#### Upload and Analyze Contract
```http
POST /api/analyze-contract
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST "http://localhost:8000/api/analyze-contract" \
  -F "file=@contract.pdf"
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "message": "Contract analysis started successfully",
  "estimated_time": "5-10 minutes",
  "status_url": "/api/analysis-status/{analysis_id}",
  "results_url": "/api/analysis-results/{analysis_id}"
}
```

#### Check Analysis Status
```http
GET /api/analysis-status/{analysis_id}
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "filename": "contract.pdf",
  "status": "processing|completed|failed",
  "current_step": "Current processing step",
  "progress_percentage": 75.0,
  "detailed_progress": {
    "document_parsing": true,
    "clause_extraction": true,
    "risk_analysis": false,
    "compliance_checking": false,
    "report_generation": false
  },
  "error": null
}
```

#### Get Analysis Results
```http
GET /api/analysis-results/{analysis_id}
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "filename": "contract.pdf",
  "status": "completed",
  "timestamp": "2024-01-01T12:00:00Z",
  "results": {
    "document_parsed": {
      "text_content": "Full contract text",
      "metadata": {...}
    },
    "clauses_extracted": {
      "clauses": [
        {
          "clause_id": "payment_terms",
          "clause_type": "Payment",
          "content": "Payment terms text...",
          "section": "Section 5"
        }
      ]
    },
    "risks_analyzed": {
      "analyses": [
        {
          "clause_id": "payment_terms",
          "clause_name": "Payment Terms",
          "risk_level": "High|Medium|Low",
          "risk_score": 8.5,
          "explanation": "Risk explanation...",
          "suggested_alternative": "Alternative wording...",
          "key_concerns": ["concern1", "concern2"]
        }
      ]
    },
    "compliance_checked": {
      "compliance_analysis": {
        "overall_score": 85,
        "compliance_grade": "B",
        "essential_clauses": {
          "present": [...],
          "missing": [...]
        },
        "compliance_issues": [...]
      }
    },
    "report_generated": {
      "before_sign_report": {
        "executive_summary": "Summary...",
        "top_risks": [...],
        "recommendations": [...],
        "negotiation_points": [...]
      }
    }
  }
}
```

#### Get Analysis Summary
```http
GET /api/analysis-summary/{analysis_id}
```

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "summary": {
    "total_clauses": 15,
    "high_risk_clauses": 3,
    "medium_risk_clauses": 5,
    "low_risk_clauses": 7,
    "compliance_score": 85,
    "overall_risk_level": "Medium",
    "key_recommendations": [...]
  }
}
```

#### Delete Analysis
```http
DELETE /api/analysis/{analysis_id}
```

## 🤖 AI Chat API Endpoints

#### Ask About Contract
```http
POST /api/ai-chat/ask
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `question` (required): Your question about the contract
- `analysis_id` (optional): Analysis ID for context
- `contract_text` (optional): Raw contract text

**Response:**
```json
{
  "success": true,
  "question": "What are the payment terms?",
  "answer": "Based on the contract...",
  "context_used": true,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Explain Clause
```http
POST /api/ai-chat/explain-clause
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `clause_text` (required): Clause text to explain
- `analysis_id` (optional): Analysis ID for context

#### Suggest Improvements
```http
POST /api/ai-chat/suggest-improvements
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `clause_text` (required): Clause text to improve
- `analysis_id` (optional): Analysis ID for context

#### Chat with Analysis
```http
POST /api/ai-chat/chat-with-analysis/{analysis_id}
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `message` (required): Chat message

## 🔄 Version Comparison API Endpoints

#### Compare Text Versions
```http
POST /api/version-comparison/compare-texts
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `original_text` (required): Original contract text
- `modified_text` (required): Modified contract text
- `original_label` (optional): Label for original (default: "Original")
- `modified_label` (optional): Label for modified (default: "Modified")

**Response:**
```json
{
  "success": true,
  "version_labels": ["Original", "Modified"],
  "similarity_score": 0.85,
  "text_diff": {...},
  "ai_analysis": "AI analysis of changes...",
  "clause_changes": {
    "added_clauses": [...],
    "removed_clauses": [...],
    "modified_clauses": [...],
    "total_changes": 5
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Compare File Versions
```http
POST /api/version-comparison/compare-files
Content-Type: multipart/form-data
```

**Parameters:**
- `original_file` (required): Original contract file
- `modified_file` (required): Modified contract file
- `original_label` (optional): Label for original
- `modified_label` (optional): Label for modified

#### Compare Analyses
```http
POST /api/version-comparison/compare-analyses
Content-Type: application/json
```

**Parameters:**
```json
{
  "original_analysis": {...},
  "modified_analysis": {...},
  "version_labels": ["Original", "Modified"]
}
```

## 📊 Downloadable Reports API Endpoints

#### Generate PDF Report
```http
POST /api/reports/generate-pdf
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `analysis_id` (required): Analysis ID
- `filename` (optional): Custom filename

**Response:**
```json
{
  "success": true,
  "filename": "contract-analysis.pdf",
  "size_bytes": 150000,
  "mime_type": "application/pdf",
  "content_base64": "base64-encoded-pdf-content"
}
```

#### Generate HTML Report
```http
POST /api/reports/generate-html
```

#### Generate JSON Report
```http
POST /api/reports/generate-json
```

#### Generate Word (RTF) Report
```http
POST /api/reports/generate-word
```

#### Generate All Formats
```http
POST /api/reports/generate-all-formats
Content-Type: application/x-www-form-urlencoded
```

**Parameters:**
- `analysis_id` (required): Analysis ID
- `base_filename` (optional): Base filename for all reports

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "reports": {
    "pdf": {...},
    "html": {...},
    "json": {...},
    "word": {...}
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Get Available Formats
```http
GET /api/reports/available-formats
```

**Response:**
```json
{
  "formats": {
    "pdf": {
      "name": "PDF",
      "description": "Portable Document Format",
      "available": true,
      "mime_type": "application/pdf"
    },
    "html": {...},
    "json": {...},
    "word": {...}
  },
  "total_formats": 4
}
```

## 🔍 Health Check

#### API Health Status
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "app_name": "AI Contract Risk Detector",
  "version": "1.0.0",
  "groq_configured": true
}
```

## 🛠️ SDK Examples

### Python Example

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"

class ContractAnalyzerAPI:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def analyze_contract(self, file_path):
        """Upload and analyze a contract"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/analyze-contract", files=files)
        
        if response.status_code == 200:
            data = response.json()
            return data['analysis_id']
        else:
            raise Exception(f"Analysis failed: {response.text}")
    
    def get_analysis_results(self, analysis_id):
        """Get complete analysis results"""
        response = requests.get(f"{self.base_url}/analysis-results/{analysis_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get results: {response.text}")
    
    def ask_about_contract(self, question, analysis_id=None):
        """Ask AI about contract"""
        data = {
            'question': question,
            'analysis_id': analysis_id or ''
        }
        response = requests.post(f"{self.base_url}/ai-chat/ask", data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"AI Chat failed: {response.text}")

# Usage Example
api = ContractAnalyzerAPI()

# Analyze contract
analysis_id = api.analyze_contract("contract.pdf")
print(f"Analysis started: {analysis_id}")

# Get results (poll until complete)
import time
while True:
    try:
        results = api.get_analysis_results(analysis_id)
        if results['success']:
            print("Analysis complete!")
            break
        elif results['status'] == 'failed':
            print(f"Analysis failed: {results.get('error')}")
            break
        time.sleep(10)
    except:
        time.sleep(10)

# Ask questions
answer = api.ask_about_contract("What are the main risks?", analysis_id)
print(f"AI Answer: {answer['answer']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class ContractAnalyzerAPI {
    constructor(baseUrl = 'http://localhost:8000/api') {
        this.baseUrl = baseUrl;
    }

    async analyzeContract(filePath) {
        const FormData = require('form-data');
        const fs = require('fs');
        
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));

        try {
            const response = await axios.post(`${this.baseUrl}/analyze-contract`, form, {
                headers: form.getHeaders()
            });
            return response.data.analysis_id;
        } catch (error) {
            throw new Error(`Analysis failed: ${error.response?.data || error.message}`);
        }
    }

    async getAnalysisResults(analysisId) {
        try {
            const response = await axios.get(`${this.baseUrl}/analysis-results/${analysisId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get results: ${error.response?.data || error.message}`);
        }
    }

    async askAboutContract(question, analysisId = null) {
        const params = new URLSearchParams();
        params.append('question', question);
        if (analysisId) params.append('analysis_id', analysisId);

        try {
            const response = await axios.post(`${this.baseUrl}/ai-chat/ask`, params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            return response.data;
        } catch (error) {
            throw new Error(`AI Chat failed: ${error.response?.data || error.message}`);
        }
    }
}

// Usage Example
async function main() {
    const api = new ContractAnalyzerAPI();
    
    try {
        // Analyze contract
        const analysisId = await api.analyzeContract('contract.pdf');
        console.log(`Analysis started: ${analysisId}`);
        
        // Poll for results
        let results;
        while (true) {
            try {
                results = await api.getAnalysisResults(analysisId);
                if (results.success) {
                    console.log('Analysis complete!');
                    break;
                } else if (results.status === 'failed') {
                    console.log(`Analysis failed: ${results.error}`);
                    break;
                }
            } catch (error) {
                // Still processing
            }
            await new Promise(resolve => setTimeout(resolve, 10000));
        }
        
        // Ask questions
        const answer = await api.askAboutContract('What are the main risks?', analysisId);
        console.log(`AI Answer: ${answer.answer}`);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

## 📋 Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (analysis not found)
- `429`: Rate Limit Exceeded (Groq API limits)
- `500`: Internal Server Error

### Rate Limiting
- Groq free tier: 6000 tokens/minute
- Rate limit errors are automatically retried
- Consider upgrading to Groq Pro tier for production use

## 🔧 Configuration

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
GROQ_MODEL=llama-3.1-8b-instant
MAX_TOKENS=4000
TEMPERATURE=0.1
MAX_FILE_SIZE=10485760  # 10MB
DEBUG=false
```

### Supported File Formats
- PDF (.pdf)
- Microsoft Word (.docx)
- Plain Text (.txt)

### File Size Limits
- Maximum file size: 10MB (configurable)
- Large documents may take longer to process

## 🚀 Production Deployment

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t contract-analyzer-api .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key contract-analyzer-api
```

### Environment Considerations
- Use HTTPS in production
- Implement authentication/authorization
- Add rate limiting for API endpoints
- Use persistent storage instead of in-memory
- Monitor Groq API usage and costs
- Implement proper logging and monitoring

## 📞 Support

- **GitHub Issues**: https://github.com/lemessaA/ai-contract-risk-detector/issues
- **Documentation**: https://github.com/lemessaA/ai-contract-risk-detector/blob/main/README.md
- **Groq API**: https://console.groq.com

## 📄 License

This API service is provided as-is for educational and demonstration purposes.

## ⚖️ Disclaimer

This API provides AI-powered guidance based on common contract patterns and risk factors. It is not legal advice and should not replace consultation with qualified legal professionals.
