#!/usr/bin/env python3
"""
AI Contract Risk Detector - API Service Starter
Quick setup script for developers to run the backend API service
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")

def check_groq_api_key():
    """Check if Groq API key is configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Error: .env file not found")
        print("   Please create a .env file with your Groq API key:")
        print("   echo 'GROQ_API_KEY=your_groq_api_key_here' > .env")
        print("   Get your API key from: https://console.groq.com")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if 'GROQ_API_KEY=' not in content:
            print("❌ Error: GROQ_API_KEY not found in .env file")
            print("   Please add your Groq API key to the .env file")
            return False
    
    print("✅ Groq API key configured")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-api.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"   Output: {e.stdout}")
        print(f"   Error: {e.stderr}")
        return False
    return True

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    print("   API will be available at: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print("\n   Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main setup function"""
    print("🤖 AI Contract Risk Detector - API Service Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check Groq API key
    if not check_groq_api_key():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Start server
    start_api_server()

if __name__ == "__main__":
    main()
