"""
Configuration module for OCR PDF MCP Server v1.0.0
Handles environment variables and system-specific settings
"""

import os
import platform
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Production configuration for OCR PDF MCP Server"""
    
    # Version info
    VERSION = "1.0.0"
    
    # Default Tesseract path based on OS
    if platform.system() == "Windows":
        default_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    elif platform.system() == "Darwin":  # macOS
        default_tesseract = "/usr/local/bin/tesseract"
    else:  # Linux
        default_tesseract = "/usr/bin/tesseract"
    
    # Core settings
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", default_tesseract)
    OCR_LANGUAGE = os.getenv("OCR_LANGUAGE", "eng+ind")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    
    # Optional API server settings (for standalone mode)
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Performance settings
    PDF_MAX_SIZE_MB = int(os.getenv("PDF_MAX_SIZE_MB", "100"))
    OCR_TIMEOUT_SECONDS = int(os.getenv("OCR_TIMEOUT_SECONDS", "300"))
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check Tesseract
        if not Path(cls.TESSERACT_PATH).exists():
            errors.append(f"Tesseract not found at: {cls.TESSERACT_PATH}")
        
        # Check workers
        if cls.MAX_WORKERS < 1 or cls.MAX_WORKERS > 16:
            errors.append(f"MAX_WORKERS must be between 1-16, got: {cls.MAX_WORKERS}")
        
        # Check PDF size limit
        if cls.PDF_MAX_SIZE_MB < 1:
            errors.append(f"PDF_MAX_SIZE_MB must be positive, got: {cls.PDF_MAX_SIZE_MB}")
        
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
        
        return True
    
    @classmethod
    def get_info(cls):
        """Get configuration information"""
        return {
            "version": cls.VERSION,
            "tesseract_path": cls.TESSERACT_PATH,
            "ocr_language": cls.OCR_LANGUAGE,
            "max_workers": cls.MAX_WORKERS,
            "pdf_max_size_mb": cls.PDF_MAX_SIZE_MB,
            "ocr_timeout": cls.OCR_TIMEOUT_SECONDS,
            "platform": platform.system(),
            "debug": cls.DEBUG
        }