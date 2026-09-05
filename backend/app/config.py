"""
config.py
---------
Application settings and runtime configuration for SatQuery AI.
"""

from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "SatQuery AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Storage & directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    SAMPLES_DIR: Path = DATA_DIR / "samples"
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    
    # Engine mode: 'cpu_classical' (ultra-fast, zero-crash, <150ms) or 'neural'
    ENGINE_MODE: str = "cpu_classical"
    
    # Limits
    MAX_IMAGE_SIZE_MB: int = 50
    MAX_DIMENSION: int = 4096
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.85
    
    class Config:
        env_prefix = "SATQUERY_"

settings = Settings()

# Ensure runtime directories exist
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
