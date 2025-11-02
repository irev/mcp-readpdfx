#!/usr/bin/env python3
"""
OCR PDF MCP Server - Clean Implementation
Official MCP SDK with FastMCP - Fixed version
"""

from typing import Any, Optional
import asyncio
import logging
import os
import sys
from pathlib import Path

# Configure logging to stderr only (STDIO transport requirement)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_mcp_server():
    """Create and configure the MCP server"""
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        logger.error("❌ MCP SDK not found. Install with: pip install 'mcp[cli]'")
        sys.exit(1)
    
    # Initialize FastMCP server
    mcp = FastMCP("ocr-pdf")
    
    # Import OCR functions
    try:
        from ocr_pdf_mcp.pdf_text_extractor import extract_text_from_pdf
        from ocr_pdf_mcp.ocr_worker import process_ocr_pdf
        logger.info("✅ OCR modules imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import OCR modules: {e}")
        sys.exit(1)
    
    @mcp.tool()
    async def process_pdf_smart(pdf_path: str, language: str = "eng+ind") -> str:
        """Intelligently process PDF with automatic OCR detection.
        
        Args:
            pdf_path: Absolute path to the PDF file to process
            language: OCR language codes (e.g. 'eng', 'eng+ind')
        
        Returns:
            Extracted text content from the PDF
        """
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                return f"Error: File not found at {pdf_path}"
            
            if not pdf_path.lower().endswith('.pdf'):
                return "Error: File must be a PDF (.pdf extension)"
            
            # Try digital text extraction first
            text_pages = extract_text_from_pdf(pdf_path)
            combined_text = "\n".join([page.get('text', '') for page in text_pages])
            
            # If digital extraction yields minimal text, use OCR
            if not combined_text or len(combined_text.strip()) < 50:
                logger.info("Digital text minimal, using OCR...")
                ocr_results = process_ocr_pdf(pdf_path, language=language)
                ocr_text = "\n".join([page.get('text', '') for page in ocr_results])
                return ocr_text or 'No text extracted via OCR'
            
            return combined_text
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return f"Error processing PDF: {str(e)}"
    
    @mcp.tool()
    async def extract_pdf_text(pdf_path: str) -> str:
        """Extract text directly from PDF without OCR.
        
        Args:
            pdf_path: Absolute path to the PDF file
            
        Returns:
            Extracted text content from the PDF
        """
        try:
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                return f"Error: File not found at {pdf_path}"
                
            text_pages = extract_text_from_pdf(pdf_path)
            combined_text = "\n".join([page.get('text', '') for page in text_pages])
            return combined_text or "No digital text found in PDF"
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return f"Error extracting text: {str(e)}"
    
    @mcp.tool()
    async def perform_ocr(file_path: str, language: str = "eng+ind") -> str:
        """Perform OCR on image files or scanned PDFs.
        
        Args:
            file_path: Absolute path to the image or PDF file
            language: OCR language codes (e.g. 'eng', 'eng+ind')
            
        Returns:
            OCR extracted text content
        """
        try:
            logger.info(f"Performing OCR on: {file_path}")
            
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            ext = file_path.lower().split('.')[-1]
            supported_formats = ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp']
            
            if ext not in supported_formats:
                return f"Error: Unsupported format. Supported: {', '.join(supported_formats)}"
            
            if ext == 'pdf':
                ocr_results = process_ocr_pdf(file_path, language=language)
                combined_text = "\n".join([page.get('text', '') for page in ocr_results])
                return combined_text or 'No text extracted via OCR'
            else:
                # For image files, use simple OCR
                from PIL import Image
                import pytesseract
                
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image, lang=language)
                return text or 'No text extracted via OCR'
                
        except Exception as e:
            logger.error(f"OCR error on {file_path}: {e}")
            return f"OCR error: {str(e)}"
    
    @mcp.tool()
    async def analyze_pdf_structure(pdf_path: str) -> str:
        """Analyze PDF document structure and metadata.
        
        Args:
            pdf_path: Absolute path to the PDF file
            
        Returns:
            JSON string with PDF structure analysis
        """
        try:
            logger.info(f"Analyzing PDF structure: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                return f"Error: File not found at {pdf_path}"
            
            # Simple PDF analysis using PyMuPDF
            import fitz
            
            doc = fitz.open(pdf_path)
            file_size = os.path.getsize(pdf_path)
            
            # Check for digital text
            has_text = False
            text_density = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                char_count = len(str(text).strip()) if text else 0
                text_density.append(char_count)
                if char_count > 50:
                    has_text = True
            
            doc.close()
            
            # Format analysis results
            result = {
                "file_path": pdf_path,
                "total_pages": len(doc),
                "file_size_mb": round(file_size / (1024*1024), 2),
                "has_digital_text": has_text,
                "metadata": {"title": "PDF Analysis"},
                "text_density_per_page": text_density
            }
            
            return str(result)
            
        except Exception as e:
            logger.error(f"Error analyzing PDF {pdf_path}: {e}")
            return f"Error analyzing PDF: {str(e)}"
    
    @mcp.tool()
    async def list_ocr_languages() -> str:
        """List available OCR languages with Indonesian priority.
        
        Returns:
            JSON string with available languages and Indonesian support status
        """
        try:
            import subprocess
            
            # Get actually installed languages
            try:
                result = subprocess.run(['tesseract', '--list-langs'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    installed = [line.strip() for line in lines[1:] if line.strip()]
                else:
                    installed = ['eng']
            except:
                installed = ['eng']
            
            language_info = {
                "installed_languages": installed,
                "indonesian_support": {
                    "code": "ind",
                    "name": "Indonesian (Bahasa Indonesia)",
                    "installed": "ind" in installed,
                    "required": True,
                    "status": "✅ TERSEDIA" if "ind" in installed else "❌ BELUM TERINSTAL (WAJIB!)"
                },
                "priority_languages": {
                    "ind": "Indonesian (Bahasa Indonesia) - WAJIB UNTUK TEKS INDONESIA!",
                    "eng": "English",
                    "msa": "Malay (Bahasa Malaysia)",
                    "jpn": "Japanese", 
                    "kor": "Korean",
                    "chi_sim": "Chinese Simplified",
                    "tha": "Thai",
                    "vie": "Vietnamese"
                },
                "combined_languages": {
                    "eng+ind": "English + Indonesian (Recommended)",
                    "eng+msa": "English + Malay", 
                    "eng+jpn": "English + Japanese"
                },
                "installation_guide": {
                    "indonesian_required": "Indonesian (ind) WAJIB untuk pemrosesan teks Indonesia!",
                    "download_url": "https://github.com/tesseract-ocr/tessdata/raw/main/ind.traineddata",
                    "windows_install": "Copy ind.traineddata to C:\\Program Files\\Tesseract-OCR\\tessdata\\",
                    "linux_install": "sudo apt-get install tesseract-ocr-ind",
                    "macos_install": "brew install tesseract-lang"
                },
                "current_default": "eng+ind" if "ind" in installed else "eng",
                "optimal_combination": "eng+ind (English + Indonesian for mixed documents)",
                "recommendation": "Use lang='eng+ind' for documents with mixed English-Indonesian text!"
            }
            
            return str(language_info)
            
        except Exception as e:
            logger.error(f"Error checking languages: {e}")
            return f"Error checking OCR languages: {str(e)}"

    @mcp.tool()
    async def batch_process_pdfs(directory_path: str, output_format: str = "text", language: str = "eng+ind") -> str:
        """Process multiple PDF files in a directory.
        
        Args:
            directory_path: Absolute path to directory containing PDF files
            output_format: Output format - 'text' or 'json'
            language: OCR language codes for scanned documents
            
        Returns:
            Processing results for all PDF files
        """
        try:
            logger.info(f"Batch processing PDFs in: {directory_path}")
            
            if not os.path.exists(directory_path):
                return f"Error: Directory not found at {directory_path}"
            
            if not os.path.isdir(directory_path):
                return f"Error: Path is not a directory: {directory_path}"
            
            # Find all PDF files
            pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                return f"No PDF files found in {directory_path}"
            
            results = []
            processed_count = 0
            
            for pdf_file in pdf_files[:10]:  # Limit to 10 files
                pdf_path = os.path.join(directory_path, pdf_file)
                
                try:
                    # Use smart processing for each PDF
                    text_content = await process_pdf_smart(pdf_path, language)
                    
                    if output_format == "json":
                        results.append({
                            "file": pdf_file,
                            "status": "success",
                            "text_length": len(text_content),
                            "text": text_content[:500] + "..." if len(text_content) > 500 else text_content
                        })
                    else:
                        results.append(f"=== {pdf_file} ===\\n{text_content[:300]}...\\n")
                    
                    processed_count += 1
                    
                except Exception as e:
                    if output_format == "json":
                        results.append({
                            "file": pdf_file,
                            "status": "error",
                            "error": str(e)
                        })
                    else:
                        results.append(f"=== {pdf_file} ===\\nError: {str(e)}\\n")
            
            summary = f"Processed {processed_count}/{len(pdf_files)} PDF files from {directory_path}\\n\\n"
            
            if output_format == "json":
                return summary + str({"results": results})
            else:
                return summary + "\\n".join(results)
                
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return f"Batch processing error: {str(e)}"
    
    return mcp

def main():
    """Initialize and run the MCP server with STDIO transport."""
    try:
        logger.info("Starting OCR PDF MCP Server...")
        logger.info("Available tools: process_pdf_smart, extract_pdf_text, perform_ocr, analyze_pdf_structure, list_ocr_languages, batch_process_pdfs")
        logger.info("🇮🇩 Indonesian language support: Check with list_ocr_languages tool")
        
        # Create server
        mcp = create_mcp_server()
        
        # Run with STDIO transport (standard for MCP clients)
        mcp.run(transport='stdio')
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()