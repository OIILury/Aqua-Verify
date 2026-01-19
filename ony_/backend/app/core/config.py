"""
Configuration de l'application Aqua Verify
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration globale de l'application"""
    
    # Application
    APP_NAME: str = "Aqua Verify"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc"]
    
    class Config:
        env_file = ".env"


settings = Settings()

