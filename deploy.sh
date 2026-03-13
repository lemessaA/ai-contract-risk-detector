#!/bin/bash

# Railway Deployment Script
# This script guides you through deploying the AI Contract Risk Detector to Railway

echo "🚀 AI Contract Risk Detector - Railway Deployment"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "RAILWAY_DEPLOYMENT.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "✅ Project directory confirmed"

# Check if git is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "   Please commit your changes before deploying:"
    echo "   git add ."
    echo "   git commit -m 'Ready for deployment'"
    echo "   git push"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📋 Deployment Steps:"
echo "1. Go to https://railway.app"
echo "2. Click 'Start a New Project' → 'Deploy from GitHub'"
echo "3. Select your repository: lemessaA/ai-contract-risk-detector"
echo "4. Deploy Backend Service first"
echo "5. Deploy Frontend Service second"
echo ""

echo "🔧 Backend Configuration:"
echo "- Root path: /backend"
echo "- Environment variables:"
echo "  • GROQ_API_KEY=your_groq_api_key_here"
echo "  • PORT=8000"
echo "  • PYTHONPATH=/app"
echo ""

echo "🔧 Frontend Configuration:"
echo "- Root path: /frontend" 
echo "- Environment variables:"
echo "  • PORT=3000"
echo "  • NODE_ENV=production"
echo "  • NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app"
echo ""

echo "⚠️  Important Notes:"
echo "- After backend deployment, copy the backend URL"
echo "- Update frontend/next.config.js with the backend URL"
echo "- Update CORS in backend/main.py with frontend URL"
echo ""

echo "📖 For detailed instructions, see: RAILWAY_DEPLOYMENT.md"
echo ""

echo "🌐 Ready to deploy? Open: https://railway.app"

# Open Railway in browser (if possible)
if command -v xdg-open > /dev/null; then
    xdg-open https://railway.app
elif command -v open > /dev/null; then
    open https://railway.app
fi

echo "🎯 Next Steps:"
echo "1. Login to Railway"
echo "2. Connect your GitHub account" 
echo "3. Select the repository"
echo "4. Deploy backend first"
echo "5. Deploy frontend second"
echo "6. Update environment variables"
echo "7. Test the deployment"
