"""
Configuration de l'application Aqua Verify
"""
from __future__ import annotations

from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator


class Settings(BaseSettings):
    """Configuration globale de l'application"""
    
    # Application
    APP_NAME: str = "Aqua Verify"
    APP_VERSION: str = "1.0.0"
    # En dev, on veut pouvoir tolérer des valeurs comme "WARN" dans l'env.
    # DEBUG reste un bool, mais on parse de manière robuste.
    DEBUG: bool = True

    # Niveau de log (optionnel). Valeurs typiques: DEBUG, INFO, WARNING, ERROR
    LOG_LEVEL: str = "INFO"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, v):
        if isinstance(v, bool):
            return v
        if v is None:
            return True
        s = str(v).strip().lower()
        if s in {"1", "true", "yes", "y", "on"}:
            return True
        if s in {"0", "false", "no", "n", "off"}:
            return False
        # Cas fréquents: DEBUG=WARN / INFO / ERROR (ce n'est pas un bool)
        return False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Upload
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc"]
    
    class Config:
        env_file = ".env"


settings = Settings()

