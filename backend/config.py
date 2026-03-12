"""
Configuration settings for AI Contract Risk Detector
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "AI Contract Risk Detector"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # LLM Configuration
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".pdf", ".docx", ".txt"]
    upload_dir: str = "uploads"
    
    # Database Configuration (if needed)
    database_url: Optional[str] = os.getenv("DATABASE_URL")
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
