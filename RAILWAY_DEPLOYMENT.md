# Railway Deployment Guide

## 🚀 Deploy AI Contract Risk Detector to Railway

### Prerequisites
- GitHub repository with your code
- Railway account (free tier available)
- GROQ API key

### Step 1: Prepare Your Repository

1. **Add Dockerfiles** (already created):
   - `backend/Dockerfile` - For FastAPI backend
   - `frontend/Dockerfile` - For Next.js frontend

2. **Add Railway configs** (already created):
   - `backend/railway.toml`
   - `frontend/railway.toml`

3. **Update CORS for production**:
   - Edit `backend/main.py` to include your Railway domain

### Step 2: Deploy Backend

1. **Go to Railway Dashboard**
   - Click "New Project"
   - Select "Deploy from GitHub repo"

2. **Configure Backend Service**:
   - Select your repository
   - Set root path to `/backend`
   - Add environment variables:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     PORT=8000
     PYTHONPATH=/app
     ```

3. **Deploy**:
   - Railway will build and deploy automatically
   - Note the backend URL (e.g., `your-app.railway.app`)

### Step 3: Deploy Frontend

1. **Add New Service**:
   - In same project, click "Add Service"
   - Select "Deploy from GitHub repo"
   - Set root path to `/frontend`

2. **Configure Frontend Service**:
   - Add environment variables:
     ```
     PORT=3000
     NODE_ENV=production
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     ```

3. **Update API Proxy**:
   - Edit `frontend/next.config.js`:
   ```javascript
   destination: 'https://your-backend-url.railway.app/api/:path*',
   ```

### Step 4: Update CORS

Edit `backend/main.py` to include your Railway domains:
```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:3001", 
    "https://your-frontend-url.railway.app"
]
```

### Step 5: Test Deployment

1. **Backend Health Check**:
   ```
   https://your-backend-url.railway.app/health
   ```

2. **Frontend Access**:
   ```
   https://your-frontend-url.railway.app
   ```

### Step 6: Custom Domain (Optional)

1. **In Railway Dashboard**:
   - Go to Settings for each service
   - Add custom domain
   - Configure DNS records

2. **Update CORS**:
   - Add custom domains to `allow_origins`

### Environment Variables

#### Backend Required:
```
GROQ_API_KEY=gsk_your_key_here
PORT=8000
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

#### Frontend Required:
```
PORT=3000
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

### Troubleshooting

#### Common Issues:
1. **CORS Errors**: Update `allow_origins` in backend
2. **Build Failures**: Check Dockerfile paths
3. **API Connection**: Verify API proxy configuration
4. **Environment Variables**: Ensure all required vars are set

#### Debug Commands:
```bash
# Check backend logs
railway logs backend-service

# Check frontend logs  
railway logs frontend-service

# Restart service
railway restart service-name
```

### Cost Estimate

- **Free Tier**: 500 hours/month (sufficient for development)
- **Paid Tier**: $5-20/month for production usage
- **Scaling**: Auto-scales with traffic

### Security Notes

1. **API Keys**: Never commit API keys to git
2. **HTTPS**: Railway provides automatic SSL
3. **Environment Variables**: Use Railway's secure env var management
4. **Rate Limiting**: Already configured in middleware

### Monitoring

Railway provides:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, and network usage
- **Health Checks**: Automatic service monitoring
- **Alerts**: Email notifications for failures

### Next Steps

1. **Deploy to Railway** using this guide
2. **Test all features** in production
3. **Set up monitoring** and alerts
4. **Configure custom domain** if needed
5. **Set up CI/CD** for automatic deployments

---

**Need Help?**
- Railway docs: https://docs.railway.app/
- Docker reference: https://docs.docker.com/
- Next.js deployment: https://nextjs.org/docs/deployment
