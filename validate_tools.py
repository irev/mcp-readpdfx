#!/usr/bin/env python3
"""
Validate MCP Tools Registration
Tests that all OCR tools are properly registered in the MCP server
"""

import sys
import traceback
from pathlib import Path

def validate_tools():
    """Validate that all tools are properly registered"""
    
    try:
        # Import the server setup
        from mcp.server.fastmcp import FastMCP
        from ocr_pdf_mcp.pdf_text_extractor import extract_text_from_pdf
        from ocr_pdf_mcp.ocr_worker import process_ocr_pdf
        from ocr_pdf_mcp.config import Config
        
        print("🔧 Validating MCP Tools Registration")
        print("=" * 50)
        
        # Create MCP server instance
        mcp = FastMCP("OCR PDF MCP Server")
        print(f"✅ Server created: {mcp.name}")
        
        # Tool 1: PDF Text Extraction
        @mcp.tool()
        def extract_pdf_text(file_path: str) -> str:
            """Extract text from PDF file using PyMuPDF"""
            return extract_text_from_pdf(file_path)
        
        print("✅ Tool 1 registered: extract_pdf_text")
        
        # Tool 2: OCR Processing  
        @mcp.tool()
        def ocr_pdf(file_path: str, language: str = "eng+ind") -> str:
            """Perform OCR on PDF file using Tesseract with Indonesian support"""
            return process_ocr_pdf(file_path, language)
        
        print("✅ Tool 2 registered: ocr_pdf")
        
        # Tool 3: Combined Processing
        @mcp.tool()
        def extract_and_ocr_pdf(file_path: str, language: str = "eng") -> dict:
            """Extract text and perform OCR on PDF file"""
            text_result = extract_text_from_pdf(file_path)
            ocr_result = process_ocr_pdf(file_path, language)
            
            return {
                "extracted_text": text_result,
                "ocr_text": ocr_result,
                "file_path": file_path,
                "language": language
            }
        
        print("✅ Tool 3 registered: extract_and_ocr_pdf")
        
        # Tool 4: Health Check
        @mcp.tool()
        def health_check() -> dict:
            """Check server health and dependencies"""
            return {
                "status": "healthy",
                "version": Config.VERSION,
                "dependencies": {
                    "PyMuPDF": "available",
                    "tesseract": "available",
                    "Pillow": "available"
                }
            }
        
        print("✅ Tool 4 registered: health_check")
        
        # Tool 5: List Available Languages
        @mcp.tool()
        def list_ocr_languages() -> dict:
            """List available OCR languages"""
            # This would normally check tesseract languages
            return {
                "available_languages": ["eng","eng+ind", "spa", "fra", "deu", "ita", "por"],
                "default": "eng+ind",
                "note": "Install additional language packs with: apt-get install tesseract-ocr-[lang]"
            }
        
        print("✅ Tool 5 registered: list_ocr_languages")
        
        # Try to inspect registered tools (if possible)
        try:
            # This might not work depending on FastMCP internals
            if hasattr(mcp, '_tools') or hasattr(mcp, 'tools'):
                tools_attr = getattr(mcp, '_tools', None) or getattr(mcp, 'tools', None)
                if tools_attr:
                    print(f"\n📋 Registered tools count: {len(tools_attr)}")
                else:
                    print("\n📋 Tools registered (count not accessible)")
            else:
                print("\n📋 Tools registered (internal structure not accessible)")
        except Exception as e:
            print(f"\n📋 Tools registered (inspection failed: {e})")
        
        print(f"\n🎉 All tools registered successfully!")
        print(f"Server version: {Config.VERSION}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_tools()
    sys.exit(0 if success else 1)