#!/usr/bin/env python3
"""
OCR PDF HTTP Server - ML Studio Compatible
Version: 1.0.0

HTTP REST API server for ML Studio and other HTTP clients.
Provides the same OCR functionality as the MCP server but through HTTP endpoints.

Usage:
    python http_server.py [--port 8000] [--host 127.0.0.1]

Environment Variables:
    TESSERACT_PATH: Path to Tesseract executable
    OCR_LANGUAGE: Default OCR language (default: eng+ind)
    LOG_LEVEL: Logging level (default: INFO)
    MAX_WORKERS: Max OCR workers (default: 4)
    HTTP_PORT: HTTP server port (default: 8000)
    HTTP_HOST: HTTP server host (default: 127.0.0.1)
"""

import asyncio
import json
import logging
import os
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn
import tempfile
import shutil

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import version info
try:
    from version import __version__, get_version_info, print_version
except ImportError:
    __version__ = "1.0.0"
    def get_version_info():
        return {"version": "1.0.0", "build": "unknown"}
    def print_version():
        print(f"OCR PDF HTTP Server v{__version__}")

# Import OCR functionality
try:
    from ocr_pdf_mcp.config import Config
    from ocr_pdf_mcp.pdf_utils import get_pdf_info
    from ocr_pdf_mcp.pdf_text_extractor import extract_text_from_pdf
    from ocr_pdf_mcp.ocr_worker import process_ocr_pdf
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory and dependencies are installed.")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="OCR PDF HTTP Server",
    description="HTTP REST API for PDF OCR and text extraction",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper JSON response"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail,
            "status_code": exc.status_code,
            "server_version": __version__
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with proper JSON response"""
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error": "Request validation failed",
            "details": exc.errors(),
            "status_code": 422,
            "server_version": __version__
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with proper JSON response"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": "Internal server error",
            "details": str(exc),
            "status_code": 500,
            "server_version": __version__
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

class OCRPDFHTTPServer:
    """HTTP server for OCR PDF processing"""
    
    def __init__(self):
        """Initialize server with configuration"""
        try:
            self.config = Config()
            self.version = __version__
            self.default_language = self.config.OCR_LANGUAGE
            self.max_workers = self.config.MAX_WORKERS
            
            logger.info(f"🚀 OCR PDF HTTP Server v{self.version} initializing...")
            logger.info(f"📍 Tesseract: {self.config.TESSERACT_PATH}")
            logger.info(f"🌍 Default Language: {self.default_language}")
            logger.info(f"⚡ Max Workers: {self.max_workers}")
            
            # Validate environment
            self._validate_environment()
            
        except Exception as e:
            logger.error(f"❌ Server initialization failed: {e}")
            raise
    
    def _validate_environment(self):
        """Validate required dependencies and configuration"""
        try:
            # Basic validation - check if Tesseract path exists
            if not os.path.exists(self.config.TESSERACT_PATH):
                raise RuntimeError(f"Tesseract not found: {self.config.TESSERACT_PATH}")
            
            logger.info("✅ Environment validation successful")
            
        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            raise
    
    async def get_pdf_info_handler(self, file_path: str) -> Dict[str, Any]:
        """Get PDF information"""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            
            if not file_path.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="File must be a PDF")
            
            info = get_pdf_info(file_path)
            
            return {
                "status": "success",
                "operation": "get_pdf_info",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size_bytes": os.path.getsize(file_path),
                "total_pages": info["total_pages"],
                "is_scanned": info["is_scanned"],
                "processing_method": "OCR required" if info["is_scanned"] else "Text extraction",
                "metadata": info,
                "server_version": self.version
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"PDF info extraction failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def extract_text_handler(self, file_path: str) -> Dict[str, Any]:
        """Extract text from digital PDF"""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            
            if not file_path.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="File must be a PDF")
            
            pages = extract_text_from_pdf(file_path)
            
            # Calculate statistics
            total_chars = sum(len(page.get('text', '')) for page in pages)
            total_words = sum(len(page.get('text', '').split()) for page in pages)
            pages_with_text = sum(1 for page in pages if page.get('text', '').strip())
            
            return {
                "status": "success",
                "operation": "extract_text",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "processing_method": "Digital text extraction",
                "total_pages": len(pages),
                "pages_with_text": pages_with_text,
                "total_characters": total_chars,
                "total_words": total_words,
                "pages": pages,
                "server_version": self.version
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def ocr_pdf_handler(self, file_path: str, language: Optional[str] = None, max_workers: Optional[int] = None) -> Dict[str, Any]:
        """Perform OCR on PDF"""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            
            if not file_path.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="File must be a PDF")
            
            # Use defaults if not provided
            language = language or self.default_language
            max_workers = max_workers or self.max_workers
            
            # Validate max_workers
            if max_workers < 1 or max_workers > 8:
                raise HTTPException(status_code=400, detail="max_workers must be between 1 and 8")
            
            pages = process_ocr_pdf(file_path, max_workers=max_workers)
            
            # Calculate statistics
            total_chars = sum(len(page.get('text', '')) for page in pages)
            total_words = sum(len(page.get('text', '').split()) for page in pages)
            pages_with_text = sum(1 for page in pages if page.get('text', '').strip())
            
            return {
                "status": "success",
                "operation": "ocr_pdf",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "processing_method": "OCR",
                "ocr_language": language,
                "max_workers_used": max_workers,
                "total_pages": len(pages),
                "pages_with_text": pages_with_text,
                "total_characters": total_chars,
                "total_words": total_words,
                "pages": pages,
                "server_version": self.version
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def smart_process_handler(self, file_path: str, language: Optional[str] = None, force_ocr: bool = False) -> Dict[str, Any]:
        """Smart PDF processing with auto-detection"""
        try:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            
            if not file_path.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="File must be a PDF")
            
            # Use defaults if not provided
            language = language or self.default_language
            
            # Get PDF info first
            info = get_pdf_info(file_path)
            
            # Decide processing method
            use_ocr = info["is_scanned"] or force_ocr
            
            if use_ocr:
                pages = process_ocr_pdf(file_path, max_workers=self.max_workers)
                processing_method = "OCR (auto-detected as scanned)" if info["is_scanned"] else "OCR (forced)"
            else:
                pages = extract_text_from_pdf(file_path)
                processing_method = "Digital text extraction (auto-detected)"
            
            # Calculate statistics
            total_chars = sum(len(page.get('text', '')) for page in pages)
            total_words = sum(len(page.get('text', '').split()) for page in pages)
            pages_with_text = sum(1 for page in pages if page.get('text', '').strip())
            
            return {
                "status": "success",
                "operation": "smart_process",
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "processing_method": processing_method,
                "pdf_type": "scanned" if info["is_scanned"] else "digital",
                "used_ocr": use_ocr,
                "ocr_language": language if use_ocr else None,
                "total_pages": len(pages),
                "pages_with_text": pages_with_text,
                "total_characters": total_chars,
                "total_words": total_words,
                "confidence_score": "high" if pages_with_text > 0 else "low",
                "pages": pages,
                "server_version": self.version
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Smart processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Initialize server
ocr_server = OCRPDFHTTPServer()

# Root endpoint - Health check and server info
@app.get("/", response_class=JSONResponse)
async def root():
    """Server health check and information"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "OCR PDF HTTP Server",
            "version": __version__,
            "endpoints": {
                "health": "/health",
                "info": "/info",
                "pdf_info": "/pdf/info",
                "extract_text": "/pdf/extract",
                "ocr": "/pdf/ocr", 
                "smart_process": "/pdf/smart",
                "upload_and_process": "/pdf/upload",
                "documentation": "/docs"
            },
            "message": "OCR PDF HTTP Server is running successfully!"
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Health check endpoint
@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": __version__,
            "tesseract_path": ocr_server.config.TESSERACT_PATH,
            "default_language": ocr_server.default_language,
            "max_workers": ocr_server.max_workers
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Server info endpoint
@app.get("/info", response_class=JSONResponse)
async def server_info():
    """Get detailed server information"""
    return JSONResponse(
        content={
            "server": "OCR PDF HTTP Server",
            "version": __version__,
            "build_info": get_version_info(),
            "configuration": {
                "tesseract_path": ocr_server.config.TESSERACT_PATH,
                "default_ocr_language": ocr_server.default_language,
                "max_workers": ocr_server.max_workers,
                "pdf_max_size_mb": getattr(ocr_server.config, 'PDF_MAX_SIZE_MB', 100),
                "ocr_timeout_seconds": getattr(ocr_server.config, 'OCR_TIMEOUT_SECONDS', 300)
            },
            "endpoints": {
                "GET /": "Server info and health check",
                "GET /health": "Health check",
                "GET /info": "Detailed server information",
                "POST /pdf/info": "Get PDF information",
                "POST /pdf/extract": "Extract text from digital PDF",
                "POST /pdf/ocr": "Perform OCR on scanned PDF",
                "POST /pdf/smart": "Smart processing (auto-detect method)",
                "POST /pdf/upload": "Upload and process PDF file",
                "GET /docs": "API documentation"
            }
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# PDF info endpoint
@app.post("/pdf/info", response_class=JSONResponse)
async def pdf_info_endpoint(file_path: str = Form(...)):
    """Get PDF information"""
    result = await ocr_server.get_pdf_info_handler(file_path)
    return JSONResponse(
        content=result,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Text extraction endpoint
@app.post("/pdf/extract", response_class=JSONResponse)
async def extract_text_endpoint(file_path: str = Form(...)):
    """Extract text from digital PDF"""
    result = await ocr_server.extract_text_handler(file_path)
    return JSONResponse(
        content=result,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# OCR endpoint
@app.post("/pdf/ocr", response_class=JSONResponse)
async def ocr_pdf_endpoint(
    file_path: str = Form(...),
    language: Optional[str] = Form(None),
    max_workers: Optional[int] = Form(None)
):
    """Perform OCR on scanned PDF"""
    result = await ocr_server.ocr_pdf_handler(file_path, language, max_workers)
    return JSONResponse(
        content=result,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Smart processing endpoint
@app.post("/pdf/smart", response_class=JSONResponse)
async def smart_process_endpoint(
    file_path: str = Form(...),
    language: Optional[str] = Form(None),
    force_ocr: bool = Form(False)
):
    """Smart PDF processing with auto-detection"""
    result = await ocr_server.smart_process_handler(file_path, language, force_ocr)
    return JSONResponse(
        content=result,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# File upload and process endpoint
@app.post("/pdf/upload", response_class=JSONResponse)
async def upload_and_process(
    file: UploadFile = File(...),
    operation: str = Form("smart_process"),
    language: Optional[str] = Form(None),
    max_workers: Optional[int] = Form(None),
    force_ocr: bool = Form(False)
):
    """Upload PDF file and process it"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process based on operation type
        if operation == "info":
            result = await ocr_server.get_pdf_info_handler(temp_file_path)
        elif operation == "extract":
            result = await ocr_server.extract_text_handler(temp_file_path)
        elif operation == "ocr":
            result = await ocr_server.ocr_pdf_handler(temp_file_path, language, max_workers)
        elif operation == "smart_process":
            result = await ocr_server.smart_process_handler(temp_file_path, language, force_ocr)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {operation}")
        
        # Update file path in result to original filename
        result["file_name"] = file.filename
        result["uploaded_file"] = True
        
        return JSONResponse(
            content=result,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    finally:
        # Cleanup temporary file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")

# Documentation endpoint
@app.get("/docs-info", response_class=HTMLResponse)
async def docs_info():
    """Custom documentation page"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OCR PDF HTTP Server v{__version__}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .endpoint {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
            .method {{ color: #2196F3; font-weight: bold; }}
            .url {{ color: #4CAF50; font-family: monospace; }}
            pre {{ background: #333; color: #fff; padding: 10px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <h1>OCR PDF HTTP Server v{__version__}</h1>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/</span>
            <p>Server health check and basic information</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <span class="url">/health</span>
            <p>Health check for monitoring systems</p>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/pdf/info</span>
            <p>Get PDF information and metadata</p>
            <pre>curl -X POST "http://127.0.0.1:8000/pdf/info" -F "file_path=/path/to/file.pdf"</pre>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/pdf/extract</span>
            <p>Extract text from digital PDF</p>
            <pre>curl -X POST "http://127.0.0.1:8000/pdf/extract" -F "file_path=/path/to/file.pdf"</pre>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/pdf/ocr</span>
            <p>Perform OCR on scanned PDF</p>
            <pre>curl -X POST "http://127.0.0.1:8000/pdf/ocr" -F "file_path=/path/to/file.pdf" -F "language=eng+ind"</pre>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/pdf/smart</span>
            <p>Smart processing with auto-detection</p>
            <pre>curl -X POST "http://127.0.0.1:8000/pdf/smart" -F "file_path=/path/to/file.pdf"</pre>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <span class="url">/pdf/upload</span>
            <p>Upload and process PDF file</p>
            <pre>curl -X POST "http://127.0.0.1:8000/pdf/upload" -F "file=@/path/to/file.pdf" -F "operation=smart_process"</pre>
        </div>
        
        <p><a href="/docs">Interactive API Documentation (Swagger)</a></p>
        <p><a href="/redoc">Alternative API Documentation (ReDoc)</a></p>
    </body>
    </html>
    """
    return html_content

def main():
    """Main entry point for HTTP server"""
    parser = argparse.ArgumentParser(description="OCR PDF HTTP Server")
    parser.add_argument("--host", default=os.getenv("HTTP_HOST", "127.0.0.1"), help="Host to bind to")
    parser.add_argument("--port", type=int, default=int(os.getenv("HTTP_PORT", "8000")), help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    # Print startup information
    print_version()
    print(f"🚀 Starting OCR PDF HTTP Server...")
    print(f"📍 Host: {args.host}:{args.port}")
    print(f"📍 Tesseract: {ocr_server.config.TESSERACT_PATH}")
    print(f"🌍 Default OCR Language: {ocr_server.default_language}")
    print(f"⚡ Max Workers: {ocr_server.max_workers}")
    print(f"📚 Documentation: http://{args.host}:{args.port}/docs")
    print("=" * 60)
    
    # Start server
    uvicorn.run(
        "http_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

if __name__ == "__main__":
    main()