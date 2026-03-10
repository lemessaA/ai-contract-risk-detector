# AI Contract Risk Detector

A comprehensive multi-agent AI system for contract risk analysis with advanced features including AI-powered chat, version comparison, and downloadable reports. This system uses Groq LLM and FastAPI to provide intelligent contract analysis before signing.

## 🚀 Features

### Core Analysis
- **Multi-Agent Analysis**: 5 specialized AI agents working together
- **Document Processing**: Support for PDF, DOCX, and TXT files
- **Risk Assessment**: Detailed clause-level risk analysis with explanations
- **Compliance Checking**: Regulatory compliance verification
- **Before You Sign Report**: User-friendly summary with top 3 risky clauses

### 🆕 New Advanced Features
- **🤖 AI Chat**: Interactive Q&A about contracts with AI assistant
- **🔄 Version Comparison**: Compare contract versions with AI analysis
- **📊 Downloadable Reports**: Generate reports in PDF, HTML, JSON, and RTF formats
- **💬 Real-time Assistance**: Ask questions, explain clauses, get improvement suggestions
- **📈 Comprehensive Dashboard**: Complete contract analysis visualization

### Technical Stack
- **Modern Frontend**: Next.js + React + TypeScript + TailwindCSS
- **RESTful API**: FastAPI backend with async processing
- **AI Integration**: Groq LLM for intelligent analysis
- **Multi-format Support**: PDF, HTML, JSON, RTF report generation

## Architecture

### Backend (Python + FastAPI)

#### Multi-Agent System:
1. **Document Parser Agent**: Extracts and cleans text from documents
2. **Clause Extractor Agent**: Identifies and categorizes contract clauses
3. **Risk Analyzer Agent**: Analyzes each clause for potential risks
4. **Compliance Checker Agent**: Verifies regulatory compliance
5. **Before Sign Report Agent**: Generates user-friendly recommendations

#### Key Components:
- **Orchestrator**: LangGraph workflow coordinating all agents
- **API Routes**: RESTful endpoints for contract analysis
- **Background Processing**: Async task handling for large documents

### Frontend (Next.js + React)

#### Components:
- **UploadContract**: File upload with drag-drop and validation
- **RiskDashboard**: Detailed risk analysis visualization
- **BeforeSignReport**: Executive summary and recommendations

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Groq API key (get free at https://console.groq.com)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

5. Start the backend server:
```bash
python main.py
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📖 Usage

### 1. **Upload Contract**: 
Navigate to the Upload tab and select a contract file (PDF, DOCX, or TXT)

### 2. **View Analysis**: 
Switch to the Risk Dashboard tab to see detailed clause-by-clause analysis

### 3. **Get Recommendations**: 
Check the Before Sign Report tab for executive summary and key recommendations

### 🆕 4. **AI Chat**: 
Use the AI Chat tab to ask questions about your contract:
- Explain specific clauses in simple terms
- Get improvement suggestions for risky clauses
- Ask about compliance requirements
- Request negotiation points

### 🆕 5. **Version Comparison**: 
Use the Version Comparison tab to:
- Compare text between contract versions
- Upload files for comparison
- Get AI analysis of changes
- View similarity scores and change summaries

### 🆕 6. **Download Reports**: 
Use the Download Reports tab to:
- Generate PDF reports for printing
- Create HTML reports for web viewing
- Export JSON data for integration
- Generate RTF files for Microsoft Word

## 🔌 API Endpoints

### Contract Analysis
- `POST /api/analyze-contract` - Upload and analyze a contract
- `GET /api/analysis-status/{analysis_id}` - Check analysis status
- `GET /api/analysis-results/{analysis_id}` - Get full analysis results
- `GET /api/analysis-summary/{analysis_id}` - Get analysis summary
- `DELETE /api/analysis/{analysis_id}` - Delete analysis

### 🆕 AI Chat
- `POST /api/ai-chat/ask` - Ask questions about contract
- `POST /api/ai-chat/explain-clause` - Explain specific clause
- `POST /api/ai-chat/suggest-improvements` - Get improvement suggestions
- `POST /api/ai-chat/chat-with-analysis/{analysis_id}` - Chat with analysis results

### 🆕 Version Comparison
- `POST /api/version-comparison/compare-texts` - Compare text versions
- `POST /api/version-comparison/compare-files` - Compare file versions
- `POST /api/version-comparison/compare-analyses` - Compare analysis results

### 🆕 Downloadable Reports
- `POST /api/reports/generate-pdf` - Generate PDF report
- `POST /api/reports/generate-html` - Generate HTML report
- `POST /api/reports/generate-json` - Generate JSON report
- `POST /api/reports/generate-word` - Generate RTF report
- `POST /api/reports/generate-all-formats` - Generate all formats
- `GET /api/reports/available-formats` - Get available formats

### Health Check
- `GET /health` - Backend health status

## Sample Contract

A sample service agreement is provided in `sample-contracts/Sample_Service_Agreement.txt` for testing purposes.

## Configuration

### Backend Configuration (config.py)
- OpenAI API key configuration
- File upload settings
- LLM model settings
- API configuration

### Frontend Configuration (next.config.js)
- API proxy settings
- Build configuration
- Development settings

## Development

### Backend Development
```bash
cd backend
python main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Code Quality
```bash
# Backend linting
cd backend
flake8 .
black .

# Frontend linting
cd frontend
npm run lint
```

## Project Structure

```
ai-contract-risk-detector/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   ├── agents/
│   │   └── contract_agent.py   # Multi-agent orchestrator
│   ├── api/
│   │   └── routes_contract.py  # API routes
│   ├── services/
│   │   ├── document_parser.py  # Document parsing service
│   │   ├── clause_extractor.py # Clause extraction service
│   │   ├── risk_analyzer.py    # Risk analysis service
│   │   ├── compliance_checker.py # Compliance checking service
│   │   └── before_sign_report.py # Report generation service
│   └── utils/
│       └── text_splitter.py    # Text processing utilities
├── frontend/
│   ├── package.json            # Node.js dependencies
│   ├── next.config.js          # Next.js configuration
│   ├── tailwind.config.js      # TailwindCSS configuration
│   ├── tsconfig.json           # TypeScript configuration
│   ├── app/
│   │   ├── page.tsx            # Main application page
│   │   ├── layout.tsx          # Root layout
│   │   └── globals.css         # Global styles
│   └── components/
│       ├── UploadContract.tsx  # File upload component
│       ├── RiskDashboard.tsx   # Risk analysis dashboard
│       └── BeforeSignReport.tsx # Before-sign report component
├── sample-contracts/
│   └── Sample_Service_Agreement.txt # Sample contract for testing
└── README.md                   # This file
```

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Groq**: High-performance LLM inference
- **LangChain**: Framework for building LLM applications
- **PyPDF2**: PDF processing
- **python-docx**: DOCX processing
- **ReportLab**: PDF report generation
- **Pydantic**: Data validation

### Frontend
- **Next.js**: React framework for production
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **TailwindCSS**: Utility-first CSS framework
- **Heroicons**: Icon library

## Security Considerations

- File upload validation and sanitization
- API rate limiting (to be implemented)
- Input validation and sanitization
- Secure file storage (production consideration)

## ⚠️ Limitations

- AI analysis is for guidance purposes only and not legal advice
- Performance depends on Groq API availability and response times
- Rate limits on Groq free tier (6000 tokens/minute)
- Large documents may require additional processing time
- Currently uses in-memory storage (to be replaced with database in production)

## Future Enhancements

- Database integration for persistent storage
- User authentication and authorization
- Additional document formats support
- Advanced risk scoring algorithms
- Integration with legal databases
- Multi-language support
- Real-time collaboration features

## License

This project is provided as-is for educational and demonstration purposes.

## Disclaimer

This tool provides AI-powered guidance based on common contract patterns and risk factors. It is not legal advice and should not replace consultation with qualified legal professionals. Always consult with an attorney before signing legally binding documents.
