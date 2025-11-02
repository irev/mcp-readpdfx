#!/usr/bin/env python3
"""
OCR PDF MCP Server - Production Entry Point
Version: 1.0.0

A robust MCP server for PDF OCR and text extraction with support for:
- Automatic PDF type detection (scanned vs digital)
- OCR processing for scanned PDFs using Tesseract
- Direct text extraction for digital PDFs
- Multi-language OCR support
- Comprehensive error handling and logging

Usage:
    python server.py

Environment Variables:
    TESSERACT_PATH: Path to Tesseract executable
    OCR_LANGUAGE: Default OCR language (default: eng+ind)
    LOG_LEVEL: Logging level (default: INFO)
    MAX_WORKERS: Max OCR workers (default: 4)
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        print(f"OCR PDF MCP Server v{__version__}")

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import MCP components
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError as e:
    logger.error(f"MCP library not installed: {e}")
    logger.error("Install with: pip install mcp")
    sys.exit(1)

# Import OCR functionality
try:
    from ocr_pdf_mcp.pdf_utils import get_pdf_info
    from ocr_pdf_mcp.ocr_worker import process_ocr_pdf
    from ocr_pdf_mcp.pdf_text_extractor import extract_text_from_pdf
    from ocr_pdf_mcp.config import Config
except ImportError as e:
    logger.error(f"OCR modules not found: {e}")
    logger.error("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Initialize MCP Server
app = Server("ocr-pdf-server")

class OCRPDFServer:
    """Production OCR PDF MCP Server"""
    
    def __init__(self):
        self.version = __version__
        self.config = Config()
        self.default_language = os.getenv("OCR_LANGUAGE", "eng+ind")
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))
        
        logger.info(f"Initializing OCR PDF MCP Server v{self.version}")
        self._validate_environment()
    
    def _validate_environment(self):
        """Validate environment and dependencies"""
        try:
            # Check Tesseract
            if not os.path.exists(self.config.TESSERACT_PATH):
                raise RuntimeError(f"Tesseract not found at: {self.config.TESSERACT_PATH}")
            
            # Test imports
            import pytesseract
            import fitz
            from PIL import Image
            
            logger.info("✅ All dependencies validated")
            
        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            raise
    
    def get_tools(self) -> List[Tool]:
        """Get available MCP tools"""
        return [
            Tool(
                name="get_pdf_info",
                description="Get comprehensive information about a PDF file including page count, type detection (scanned vs digital), and metadata",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the PDF file to analyze"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="extract_pdf_text",
                description="Extract text content from digital PDF files (PDFs with embedded text)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the PDF file"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="ocr_pdf",
                description="Perform OCR (Optical Character Recognition) on scanned PDF files to extract text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the PDF file"
                        },
                        "language": {
                            "type": "string",
                            "description": f"OCR language codes (default: {self.default_language}). Examples: 'eng', 'ind', 'eng+ind'",
                            "default": self.default_language
                        },
                        "max_workers": {
                            "type": "integer",
                            "description": f"Maximum number of parallel OCR workers (default: {self.max_workers})",
                            "default": self.max_workers,
                            "minimum": 1,
                            "maximum": 8
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            Tool(
                name="process_pdf_smart",
                description="Intelligently process PDF files - automatically detects if PDF is scanned or digital and applies appropriate processing method",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the PDF file"
                        },
                        "language": {
                            "type": "string",
                            "description": f"OCR language for scanned PDFs (default: {self.default_language})",
                            "default": self.default_language
                        },
                        "force_ocr": {
                            "type": "boolean",
                            "description": "Force OCR processing even for digital PDFs (default: false)",
                            "default": False
                        }
                    },
                    "required": ["file_path"]
                }
            )
        ]
    
    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle MCP tool calls with comprehensive error handling"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate file path
            file_path = arguments.get("file_path")
            if not file_path:
                return [TextContent(type="text", text="❌ Error: file_path is required")]
            
            if not os.path.exists(file_path):
                return [TextContent(type="text", text=f"❌ Error: File not found: {file_path}")]
            
            if not file_path.lower().endswith('.pdf'):
                return [TextContent(type="text", text="❌ Error: File must be a PDF")]
            
            logger.info(f"Processing tool: {name} for file: {os.path.basename(file_path)}")
            
            # Route to appropriate handler
            if name == "get_pdf_info":
                result = await self._handle_get_pdf_info(file_path)
            elif name == "extract_pdf_text":
                result = await self._handle_extract_text(file_path)
            elif name == "ocr_pdf":
                result = await self._handle_ocr_pdf(file_path, arguments)
            elif name == "process_pdf_smart":
                result = await self._handle_smart_process(file_path, arguments)
            else:
                return [TextContent(type="text", text=f"❌ Error: Unknown tool '{name}'")]
            
            # Add timing information
            processing_time = round(asyncio.get_event_loop().time() - start_time, 2)
            result["processing_time_seconds"] = processing_time
            result["server_version"] = self.version
            
            # Format response
            response = json.dumps(result, indent=2, ensure_ascii=False)
            return [TextContent(type="text", text=response)]
            
        except Exception as e:
            processing_time = round(asyncio.get_event_loop().time() - start_time, 2)
            logger.error(f"Tool '{name}' failed after {processing_time}s: {str(e)}")
            
            error_response = {
                "status": "error",
                "error": str(e),
                "tool": name,
                "processing_time_seconds": processing_time,
                "server_version": self.version
            }
            
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    
    async def _handle_get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """Handle PDF info extraction"""
        info = get_pdf_info(file_path)
        
        return {
            "status": "success",
            "tool": "get_pdf_info",
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_size_bytes": os.path.getsize(file_path),
            "total_pages": info["total_pages"],
            "is_scanned": info["is_scanned"],
            "processing_method": "OCR required" if info["is_scanned"] else "Text extraction",
            "metadata": info
        }
    
    async def _handle_extract_text(self, file_path: str) -> Dict[str, Any]:
        """Handle text extraction from digital PDF"""
        pages = extract_text_from_pdf(file_path)
        
        # Calculate statistics
        total_chars = sum(len(page.get('text', '')) for page in pages)
        total_words = sum(len(page.get('text', '').split()) for page in pages)
        pages_with_text = sum(1 for page in pages if page.get('text', '').strip())
        
        return {
            "status": "success",
            "tool": "extract_pdf_text",
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "processing_method": "Digital text extraction",
            "total_pages": len(pages),
            "pages_with_text": pages_with_text,
            "total_characters": total_chars,
            "total_words": total_words,
            "pages": pages
        }
    
    async def _handle_ocr_pdf(self, file_path: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OCR processing"""
        language = arguments.get("language", self.default_language)
        max_workers = arguments.get("max_workers", self.max_workers)
        
        # Process with OCR
        pages = process_ocr_pdf(file_path, max_workers=max_workers)
        
        # Calculate statistics
        total_chars = sum(len(page.get('text', '')) for page in pages)
        total_words = sum(len(page.get('text', '').split()) for page in pages)
        pages_with_text = sum(1 for page in pages if page.get('text', '').strip())
        
        return {
            "status": "success",
            "tool": "ocr_pdf",
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "processing_method": "OCR",
            "ocr_language": language,
            "max_workers_used": max_workers,
            "total_pages": len(pages),
            "pages_with_text": pages_with_text,
            "total_characters": total_chars,
            "total_words": total_words,
            "pages": pages
        }
    
    async def _handle_smart_process(self, file_path: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle smart PDF processing with auto-detection"""
        language = arguments.get("language", self.default_language)
        force_ocr = arguments.get("force_ocr", False)
        
        # Get PDF info first
        info = get_pdf_info(file_path)
        
        # Decide processing method
        use_ocr = info["is_scanned"] or force_ocr
        
        if use_ocr:
            # Use OCR
            pages = process_ocr_pdf(file_path, max_workers=self.max_workers)
            processing_method = "OCR (auto-detected as scanned)" if info["is_scanned"] else "OCR (forced)"
        else:
            # Extract digital text
            pages = extract_text_from_pdf(file_path)
            processing_method = "Digital text extraction (auto-detected)"
        
        # Calculate statistics
        total_chars = sum(len(page.get('text', '')) for page in pages)
        total_words = sum(len(page.get('text', '').split()) for page in pages)
        pages_with_text = sum(1 for page in pages if page.get('text', '').strip())
        
        return {
            "status": "success",
            "tool": "process_pdf_smart",
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
            "pages": pages
        }

# Global server instance
ocr_server = OCRPDFServer()

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return ocr_server.get_tools()

@app.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]] = None) -> List[TextContent]:
    """Handle tool calls"""
    if arguments is None:
        arguments = {}
    
    return await ocr_server.handle_tool_call(name, arguments)

async def main():
    """Main entry point for production MCP server"""
    # Print version info
    print_version()
    print(f"🚀 Starting OCR PDF MCP Server...")
    print(f"📍 Tesseract: {ocr_server.config.TESSERACT_PATH}")
    print(f"🌍 Default OCR Language: {ocr_server.default_language}")
    print(f"⚡ Max Workers: {ocr_server.max_workers}")
    print("=" * 60)
    
    # Run the server using stdio transport
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ocr-pdf-server",
                    server_version=__version__,
                    capabilities=app.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)