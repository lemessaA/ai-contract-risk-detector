# Railway Configuration Updates

## After Backend Deployment

### 1. Update Frontend API Proxy
Edit `frontend/next.config.js`:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://YOUR_BACKEND_URL.railway.app/api/:path*',
      },
    ]
  },
}
```

### 2. Update Backend CORS
Edit `backend/main.py`:

```python
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://YOUR_FRONTEND_URL.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Test Deployment
- Backend: `https://YOUR_BACKEND_URL.railway.app/health`
- Frontend: `https://YOUR_FRONTEND_URL.railway.app`

### 4. Environment Variables Needed
**Backend:**
- GROQ_API_KEY (required)
- PORT=8000
- PYTHONPATH=/app

**Frontend:**
- PORT=3000
- NODE_ENV=production
- NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_URL.railway.app
