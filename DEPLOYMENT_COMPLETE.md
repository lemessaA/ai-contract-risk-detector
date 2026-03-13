# Railway Deployment Complete Guide

## 🚀 Ready to Deploy!

Your repository is now fully prepared for Railway deployment with:
- ✅ Docker configuration files
- ✅ Railway JSON configuration  
- ✅ Clean repository (no build artifacts)
- ✅ Environment variable guidance
- ✅ Step-by-step instructions

## 📋 Quick Deployment Steps

### Option 1: Web Interface (Recommended)
1. **Go to**: https://railway.app
2. **Login**: Use your GitHub account
3. **New Project**: Click "Start a New Project"
4. **Deploy from GitHub**: Select this option
5. **Repository**: Choose `lemessaA/ai-contract-risk-detector`
6. **Backend First**:
   - Root path: `/backend`
   - Environment variables:
     ```
     GROQ_API_KEY=your_groq_key_here
     PORT=8000
     PYTHONPATH=/app
     ```
7. **Frontend Second**:
   - Add new service in same project
   - Root path: `/frontend`
   - Environment variables:
     ```
     PORT=3000
     NODE_ENV=production
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     ```

### Option 2: CLI Deployment
1. **Install CLI**: `npm install -g @railway/cli`
2. **Login**: `railway login` (opens browser)
3. **Deploy Backend**: `cd backend && railway up`
4. **Deploy Frontend**: `cd frontend && railway up`

## 🔧 Post-Deployment Configuration

After both services are deployed:

### 1. Update Frontend API Proxy
Edit `frontend/next.config.js`:
```javascript
destination: 'https://YOUR_BACKEND_URL.railway.app/api/:path*',
```

### 2. Update Backend CORS
Edit `backend/main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://YOUR_FRONTEND_URL.railway.app"
]
```

## 🧪 Testing

- **Backend Health**: `https://your-backend-url.railway.app/health`
- **Frontend**: `https://your-frontend-url.railway.app`
- **API Test**: `https://your-backend-url.railway.app/api/health`

## 📊 Expected URLs

- **Backend**: `https://ai-contract-risk-detector-backend.railway.app`
- **Frontend**: `https://ai-contract-risk-detector-frontend.railway.app`

## 💰 Cost Estimate

- **Free Tier**: 500 hours/month (sufficient for testing)
- **Production**: $5-20/month for moderate usage

## 🆘 Troubleshooting

### Common Issues:
1. **Build Failures**: Check Dockerfile paths
2. **CORS Errors**: Update allowed origins
3. **API Connection**: Verify proxy configuration
4. **Environment Variables**: Ensure all required vars are set

### Debug Commands:
```bash
# Check logs
railway logs service-name

# Restart service
railway restart service-name

# Check status
railway status
```

## 🎯 Success Criteria

✅ Backend health check passes
✅ Frontend loads without errors
✅ API calls work correctly
✅ File upload functions
✅ Version comparison works
✅ Risk analysis generates reports

---

**Ready to deploy!** 🚀

Your AI Contract Risk Detector is fully configured for production deployment on Railway.
