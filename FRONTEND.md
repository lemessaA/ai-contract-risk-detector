# 🎨 Frontend Documentation

Complete documentation for the AI Contract Risk Detector frontend built with Next.js, React, TypeScript, and TailwindCSS.

## 📋 **Table of Contents**

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Components](#components)
- [Pages](#pages)
- [Styling](#styling)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Deployment](#deployment)

---

## 🌟 Overview

The frontend provides a modern, responsive interface for the AI Contract Risk Detector, allowing users to upload contracts, view analysis results, interact with AI chat, compare versions, and download reports.

### Key Features
- **Drag-and-drop file upload** with validation
- **Real-time analysis progress** tracking
- **Interactive risk dashboard** with visualizations
- **AI-powered chat interface** for contract Q&A
- **Version comparison** with side-by-side view
- **Multi-format report generation** and download
- **Responsive design** for all devices

---

## 🛠️ Technology Stack

### Core Technologies
- **Next.js 14+** - React framework with App Router
- **React 18+** - UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Utility-first CSS framework

### Additional Libraries
- **Lucide React** - Icon library
- **React Hook Form** - Form handling
- **React Query** - Server state management
- **Framer Motion** - Animations
- **Recharts** - Data visualization
- **React Dropzone** - File upload

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   ├── globals.css        # Global styles
│   │   └── loading.tsx        # Loading component
│   ├── components/            # Reusable components
│   │   ├── ui/               # Base UI components
│   │   ├── forms/            # Form components
│   │   ├── charts/           # Chart components
│   │   └── layout/           # Layout components
│   ├── pages/                # Page components
│   │   ├── dashboard/        # Dashboard pages
│   │   ├── analysis/         # Analysis pages
│   │   ├── chat/             # Chat interface
│   │   └── reports/          # Report pages
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utility functions
│   ├── types/                # TypeScript type definitions
│   └── styles/               # Additional styles
├── public/                   # Static assets
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # TailwindCSS configuration
├── tsconfig.json           # TypeScript configuration
└── package.json            # Dependencies
```

---

## 🧩 Components

### Base UI Components (`src/components/ui/`)

#### Button Component
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  children,
  onClick
}) => {
  const baseClasses = 'font-medium rounded-lg transition-colors focus:outline-none focus:ring-2';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500'
  };
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
};
```

#### Card Component
```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
}

const Card: React.FC<CardProps> = ({ children, className = '', padding = 'md' }) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };
  
  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 ${paddingClasses[padding]} ${className}`}>
      {children}
    </div>
  );
};
```

### Form Components (`src/components/forms/`)

#### File Upload Component
```typescript
interface FileUploadProps {
  onFileSelect: (file: File) => void;
  acceptedTypes?: string[];
  maxSize?: number;
  disabled?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  acceptedTypes = ['.pdf', '.docx', '.txt'],
  maxSize = 10 * 1024 * 1024, // 10MB
  disabled = false
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      validateAndSelectFile(files[0]);
    }
  };
  
  const validateAndSelectFile = (file: File) => {
    // Validate file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(fileExtension)) {
      setError(`File type ${fileExtension} not supported`);
      return;
    }
    
    // Validate file size
    if (file.size > maxSize) {
      setError('File size exceeds 10MB limit');
      return;
    }
    
    setError(null);
    onFileSelect(file);
  };
  
  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      onDrop={handleDrop}
      onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
      onDragLeave={() => setDragActive(false)}
    >
      <Upload className="mx-auto h-12 w-12 text-gray-400" />
      <p className="mt-2 text-lg font-medium text-gray-900">
        Drop your contract file here, or click to browse
      </p>
      <p className="text-sm text-gray-500">
        Supports PDF, DOCX, and TXT files up to 10MB
      </p>
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};
```

### Chart Components (`src/components/charts/`)

#### Risk Chart Component
```typescript
interface RiskChartProps {
  data: {
    low: number;
    medium: number;
    high: number;
  };
}

const RiskChart: React.FC<RiskChartProps> = ({ data }) => {
  const chartData = [
    { name: 'Low Risk', value: data.low, fill: '#10b981' },
    { name: 'Medium Risk', value: data.medium, fill: '#f59e0b' },
    { name: 'High Risk', value: data.high, fill: '#ef4444' }
  ];
  
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
```

---

## 📄 Pages

### Home Page (`src/app/page.tsx`)
Main landing page with contract upload functionality.

```typescript
export default function HomePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    
    // Start analysis
    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/analyze-contract', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      setAnalysisId(result.analysis_id);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Contract Risk Detector
          </h1>
          <p className="text-xl text-gray-600">
            Upload your contract for instant AI-powered risk analysis
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <FileUpload onFileSelect={handleFileSelect} />
          </div>
          
          <div>
            {analysisId ? (
              <AnalysisProgress analysisId={analysisId} />
            ) : (
              <FeatureHighlights />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
```

### Analysis Dashboard (`src/pages/dashboard/AnalysisDashboard.tsx`)
Comprehensive view of contract analysis results.

```typescript
interface AnalysisDashboardProps {
  analysisId: string;
}

const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({ analysisId }) => {
  const { data: results, isLoading, error } = useAnalysisResults(analysisId);
  
  if (isLoading) return <AnalysisLoading />;
  if (error) return <ErrorMessage error={error} />;
  if (!results) return <NoData />;
  
  const riskData = {
    low: results.risks_analyzed?.risk_analyses?.filter(r => r.risk_level === 'Low').length || 0,
    medium: results.risks_analyzed?.risk_analyses?.filter(r => r.risk_level === 'Medium').length || 0,
    high: results.risks_analyzed?.risk_analyses?.filter(r => r.risk_level === 'High').length || 0
  };
  
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Clauses</h3>
          <p className="text-3xl font-bold text-blue-600">
            {results.clauses_extracted?.clauses?.length || 0}
          </p>
        </Card>
        
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Risk Score</h3>
          <p className="text-3xl font-bold text-orange-600">
            {results.compliance_checked?.compliance_score || 0}%
          </p>
        </Card>
        
        <Card>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">High Risks</h3>
          <p className="text-3xl font-bold text-red-600">
            {riskData.high}
          </p>
        </Card>
      </div>
      
      {/* Risk Distribution Chart */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
        <RiskChart data={riskData} />
      </Card>
      
      {/* Risk Details */}
      <Card>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Analysis</h3>
        <RiskList risks={results.risks_analyzed?.risk_analyses || []} />
      </Card>
      
      {/* Before Sign Report */}
      <BeforeSignReport report={results.before_sign_report} />
    </div>
  );
};
```

### AI Chat Interface (`src/pages/chat/AIChat.tsx`)
Interactive chat interface for contract questions.

```typescript
const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/ai-chat/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `question=${encodeURIComponent(input)}`
      });
      
      const result = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: result.answer,
        timestamp: new Date(),
        warnings: result.warnings
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <ChatHeader />
      
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isLoading && <LoadingBubble />}
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="border-t bg-white p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your contract..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
};
```

---

## 🎨 Styling

### TailwindCSS Configuration (`tailwind.config.js`)

```javascript
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        risk: {
          low: '#10b981',
          medium: '#f59e0b',
          high: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

### Global Styles (`src/app/globals.css`)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

@layer base {
  html {
    font-family: 'Inter', sans-serif;
  }
  
  body {
    @apply bg-gray-50 text-gray-900;
  }
}

@layer components {
  .btn-primary {
    @apply bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors;
  }
  
  .card {
    @apply bg-white rounded-xl shadow-sm border border-gray-200 p-6;
  }
  
  .risk-badge {
    @apply px-2 py-1 rounded-full text-xs font-medium;
  }
  
  .risk-low {
    @apply bg-green-100 text-green-800;
  }
  
  .risk-medium {
    @apply bg-yellow-100 text-yellow-800;
  }
  
  .risk-high {
    @apply bg-red-100 text-red-800;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
  
  .animate-pulse-slow {
    animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }
}
```

---

## 🔄 State Management

### Custom Hooks (`src/hooks/`)

#### useAnalysis Hook
```typescript
interface AnalysisResults {
  document_parsed: any;
  clauses_extracted: any;
  risks_analyzed: any;
  compliance_checked: any;
  before_sign_report: any;
}

export const useAnalysis = (analysisId: string) => {
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchResults = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`/api/analysis/${analysisId}/results`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch results');
        }
        
        const data = await response.json();
        setResults(data.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };
    
    if (analysisId) {
      fetchResults();
    }
  }, [analysisId]);
  
  return { results, isLoading, error };
};
```

#### useChat Hook
```typescript
interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  warnings?: string[];
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const sendMessage = async (question: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/ai-chat/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `question=${encodeURIComponent(question)}`
      });
      
      const result = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: result.answer,
        timestamp: new Date(),
        warnings: result.warnings
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const clearChat = () => {
    setMessages([]);
  };
  
  return { messages, isLoading, sendMessage, clearChat };
};
```

---

## 🔌 API Integration

### API Client (`src/lib/api.ts`)

```typescript
class APIClient {
  private baseURL: string;
  
  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
  }
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }
  
  // Contract Analysis
  async analyzeContract(file: File): Promise<{ analysis_id: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseURL}/analyze-contract`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze contract');
    }
    
    return response.json();
  }
  
  async getAnalysisResults(analysisId: string): Promise<any> {
    return this.request(`/analysis/${analysisId}/results`);
  }
  
  async getAnalysisStatus(analysisId: string): Promise<any> {
    return this.request(`/analysis/${analysisId}/status`);
  }
  
  // AI Chat
  async askQuestion(question: string, analysisId?: string): Promise<any> {
    const params = new URLSearchParams({ question });
    if (analysisId) {
      params.append('analysis_id', analysisId);
    }
    
    const response = await fetch(`${this.baseURL}/ai-chat/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString(),
    });
    
    return response.json();
  }
  
  // Version Comparison
  async compareVersions(
    originalText: string,
    modifiedText: string
  ): Promise<any> {
    const params = new URLSearchParams({
      original_text: originalText,
      modified_text: modifiedText,
    });
    
    const response = await fetch(`${this.baseURL}/version-comparison/compare-texts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: params.toString(),
    });
    
    return response.json();
  }
  
  // Reports
  async getAvailableFormats(): Promise<any> {
    return this.request('/reports/available-formats');
  }
  
  async generateReports(analysisId: string, formats?: string[]): Promise<any> {
    if (formats) {
      // Generate specific format
      const params = new URLSearchParams({ format: formats[0] });
      return this.request(`/reports/generate/${analysisId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString(),
      });
    } else {
      // Generate all formats
      return this.request(`/reports/generate-all/${analysisId}`, {
        method: 'POST',
      });
    }
  }
}

export const apiClient = new APIClient();
```

---

## 🚀 Deployment

### Build Configuration (`next.config.js`)

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### Docker Configuration

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app
COPY package.json, yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=AI Contract Risk Detector
NEXT_PUBLIC_APP_VERSION=1.0.0
```

---

## 📊 Performance Optimization

### Code Splitting
- Automatic route-based code splitting with Next.js App Router
- Dynamic imports for heavy components
- Lazy loading for charts and visualizations

### Image Optimization
- Next.js Image component for automatic optimization
- Responsive images with proper sizing
- WebP format support

### Caching Strategy
- API response caching with React Query
- Static asset caching with Next.js
- Browser caching headers

---

## 🎯 Best Practices

### TypeScript Usage
- Strict type checking enabled
- Comprehensive type definitions
- Interface segregation for components
- Generic types for reusable components

### Accessibility
- Semantic HTML elements
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

### SEO Optimization
- Meta tags and structured data
- Open Graph tags
- JSON-LD for rich snippets
- Sitemap generation

### Error Handling
- Error boundaries for React components
- Graceful degradation for API failures
- User-friendly error messages
- Logging and monitoring integration

---

## 📱 Responsive Design

The frontend is fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

Key responsive features:
- Collapsible navigation on mobile
- Touch-friendly interactions
- Optimized layouts for different screen sizes
- Progressive enhancement for older browsers

---

## 🔧 Development Workflow

### Local Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run type checking
npm run type-check

# Run linting
npm run lint

# Build for production
npm run build
```

### Testing
```bash
# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run accessibility tests
npm run test:a11y
```

The frontend provides a modern, performant, and accessible interface for the AI Contract Risk Detector, with comprehensive features for contract analysis, AI interaction, and report generation.
