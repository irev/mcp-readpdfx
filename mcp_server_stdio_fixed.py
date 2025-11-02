#!/usr/bin/env python3
"""
Fixed MCP Server with proper error handling and logging for LM Studio
"""

import sys
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

# Configure logging to stderr (MCP standard)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server import NotificationOptions
    from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
    from mcp.types import ReadResourceRequest, ReadResourceResult
    logger.info("✅ MCP imports successful")
except ImportError as e:
    logger.error(f"❌ MCP import failed: {e}")
    sys.exit(1)

# Import OCR modules with error handling
try:
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image
    import subprocess
    logger.info("✅ OCR modules imported successfully")
except ImportError as e:
    logger.error(f"❌ OCR module import failed: {e}")

# Initialize MCP server with resource support
mcp = FastMCP("OCR-PDF-Server")

# File upload capabilities for LM Studio
SUPPORTED_FILE_TYPES = [".pdf", ".PDF"]

logger.info("✅ MCP server initialized with file upload support")

def resolve_file_path(file_path: str) -> str:
    """
    Resolve file path, handling LM Studio user-files locations and uploaded files
    """
    logger.info(f"🔍 Resolving file path: {file_path}")
    
    # Check if file exists as-is
    if Path(file_path).exists():
        logger.info(f"✅ File found at original path: {file_path}")
        return file_path
    
    # Extract just the filename for uploaded files
    filename = Path(file_path).name
    
    # Try alternative paths for LM Studio and container environments
    alternative_paths = [
        file_path,  # Original path
        f"C:/Users/{os.getenv('USERNAME', 'user')}/.lmstudio/user-files/{filename}",  # LM Studio user files
        f"/content/{filename}",  # Container path
        f"./user-files/{filename}",  # Relative user files
        f"~/Downloads/{filename}",  # Downloads folder
        f"./{filename}",  # Current directory
        f"../uploads/{filename}",  # Upload directory
        filename  # Just the filename in current dir
    ]
    
    logger.info(f"🔍 Searching in {len(alternative_paths)} locations for: {filename}")
    
    for test_path in alternative_paths:
        expanded_path = os.path.expanduser(test_path)
        if Path(expanded_path).exists():
            logger.info(f"✅ File found: {file_path} -> {expanded_path}")
            return expanded_path
        else:
            logger.debug(f"❌ Not found: {expanded_path}")
    
    # If no file found, return original path for error handling
    logger.warning(f"⚠️ File not found in any location, returning original: {file_path}")
    return file_path

def detect_uploaded_files() -> List[str]:
    """
    Detect recently uploaded PDF files in LM Studio user directory
    """
    username = os.getenv('USERNAME', 'user')
    lm_studio_dir = Path(f"C:/Users/{username}/.lmstudio/user-files")
    
    uploaded_files = []
    
    if lm_studio_dir.exists():
        for file_path in lm_studio_dir.glob("*.pdf"):
            uploaded_files.append(str(file_path))
            logger.info(f"📤 Detected uploaded file: {file_path.name}")
    
    return uploaded_files

@mcp.tool()
def extract_pdf_text(file_path: str) -> str:
    """
    Extract text from PDF file using PyMuPDF. 
    📤 SUPPORTS FILE UPLOAD: Drag & drop PDF files in LM Studio chat!
    
    Args:
        file_path: Path to the PDF file (or just filename if uploaded to LM Studio)
        
    Returns:
        Extracted text content
    """
    try:
        logger.info(f"Extracting text from: {file_path}")
        
        # Resolve file path for different environments
        file_path = resolve_file_path(file_path)
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        doc = fitz.open(file_path)
        text_content = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            # Handle various return types from PyMuPDF
            text_str = text if isinstance(text, str) else str(text) if text else ""
            if text_str and text_str.strip():
                text_content.append(f"--- Page {page_num + 1} ---\n{text_str}")
        
        doc.close()
        
        result = "\n\n".join(text_content) if text_content else "No text found in PDF"
        logger.info(f"Successfully extracted {len(result)} characters")
        return result
        
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def perform_ocr(file_path: str, language: str = "eng+ind") -> str:
    """
    Perform OCR on PDF file using Tesseract with Indonesian support.
    📤 SUPPORTS FILE UPLOAD: Drag & drop PDF files in LM Studio chat!
    
    Args:
        file_path: Path to the PDF file (or just filename if uploaded to LM Studio)
        language: OCR language (default: eng+ind for English+Indonesian)
        
    Returns:
        OCR extracted text
    """
    try:
        logger.info(f"Performing OCR on: {file_path} with language: {language}")
        
        # Resolve file path for different environments
        file_path = resolve_file_path(file_path)
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Convert PDF to images first
        doc = fitz.open(file_path)
        ocr_results = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scaling for better OCR
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            from io import BytesIO
            img = Image.open(BytesIO(img_data))
            
            # Perform OCR
            try:
                ocr_text = pytesseract.image_to_string(img, lang=language)
                if ocr_text.strip():
                    ocr_results.append(f"--- Page {page_num + 1} (OCR) ---\n{ocr_text}")
            except pytesseract.TesseractError as te:
                logger.warning(f"OCR failed for page {page_num + 1}: {te}")
                # Fallback to English only
                if language != "eng":
                    try:
                        ocr_text = pytesseract.image_to_string(img, lang="eng")
                        ocr_results.append(f"--- Page {page_num + 1} (OCR-ENG) ---\n{ocr_text}")
                    except:
                        ocr_results.append(f"--- Page {page_num + 1} ---\nOCR failed")
        
        doc.close()
        
        result = "\n\n".join(ocr_results) if ocr_results else "No text extracted via OCR"
        logger.info(f"OCR completed, extracted {len(result)} characters")
        return result
        
    except Exception as e:
        logger.error(f"Error performing OCR: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
def process_pdf_smart(file_path: str, language: str = "eng+ind") -> str:
    """
    Smart PDF processing: tries text extraction first, falls back to OCR.
    📤 SUPPORTS FILE UPLOAD: Drag & drop PDF files in LM Studio chat!
    
    Args:
        file_path: Path to the PDF file (or just filename if uploaded to LM Studio)
        language: OCR language for fallback (default: eng+ind)
        
    Returns:
        Processing results as string
    """
    try:
        logger.info(f"Smart processing: {file_path}")
        
        # Try text extraction first
        extracted_text = extract_pdf_text(file_path)
        
        # Check if we got meaningful text (not just spaces/newlines)
        meaningful_text = bool(extracted_text.strip() and 
                             len([c for c in extracted_text if c.isalnum()]) > 50)
        
        if meaningful_text:
            result = f"Method: Text Extraction\nLanguage: {language}\nContent:\n{extracted_text}"
            logger.info("Smart processing completed using text extraction method")
        else:
            ocr_text = perform_ocr(file_path, language)
            result = f"Method: OCR Processing\nLanguage: {language}\nContent:\n{ocr_text}"
            logger.info("Smart processing completed using OCR method")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in smart processing: {e}")
        return f"Error processing {file_path}: {str(e)}"

@mcp.tool()
def list_ocr_languages() -> str:
    """
    List available OCR languages and check Indonesian support.
    
    Returns:
        Language information as formatted string
    """
    try:
        logger.info("Checking available OCR languages")
        
        # Check available Tesseract languages
        try:
            result = subprocess.run(['tesseract', '--list-langs'], 
                                  capture_output=True, text=True, check=True)
            available_langs = [lang.strip() for lang in result.stdout.split('\n') if lang.strip()]
            # Remove the first line which is usually "List of available languages (X):"
            if available_langs and 'available' in available_langs[0].lower():
                available_langs = available_langs[1:]
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Could not detect Tesseract languages, using default list")
            available_langs = ['eng']
        
        # Check Indonesian support
        indonesian_available = 'ind' in available_langs
        
        response = f"""OCR Language Information:
========================

Available Languages: {', '.join(available_langs)}
Total Languages: {len(available_langs)}

Indonesian Support:
- Status: {'✅ Available' if indonesian_available else '❌ Not installed (REQUIRED)'}
- Code: ind
- Download: https://github.com/tesseract-ocr/tessdata/raw/main/ind.traineddata

Recommended Language:
- eng+ind (English + Indonesian for mixed documents) - OPTIMAL
- eng (English only - fallback)

Default Language: {'eng+ind' if indonesian_available else 'eng'}
"""
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking languages: {e}")
        return f"Error checking OCR languages: {str(e)}"

@mcp.tool()
def analyze_pdf_structure(file_path: str) -> str:
    """
    Analyze PDF structure and metadata.
    📤 SUPPORTS FILE UPLOAD: Drag & drop PDF files in LM Studio chat!
    
    Args:
        file_path: Path to the PDF file (or just filename if uploaded to LM Studio)
        
    Returns:
        PDF analysis results as formatted string
    """
    try:
        logger.info(f"Analyzing PDF structure: {file_path}")
        
        # Resolve file path for different environments
        file_path = resolve_file_path(file_path)
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        doc = fitz.open(file_path)
        
        # Basic analysis
        page_count = len(doc)
        file_size = Path(file_path).stat().st_size
        metadata = doc.metadata
        
        # Analyze first few pages
        pages_with_text = 0
        pages_with_images = 0
        total_chars = 0
        
        for page_num in range(min(page_count, 5)):  # Limit to first 5 pages for performance
            page = doc.load_page(page_num)
            
            # Check for text
            text = page.get_text()
            text_str = text if isinstance(text, str) else str(text) if text else ""
            if text_str and text_str.strip():
                pages_with_text += 1
                total_chars += len(text_str)
            
            # Check for images  
            image_list = page.get_images()
            if image_list:
                pages_with_images += 1
        
        doc.close()
        
        # Determine document type
        is_scanned = pages_with_text < page_count * 0.5
        
        response = f"""PDF Structure Analysis:
=====================

File: {Path(file_path).name}
Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)
Pages: {page_count}

Content Analysis (first 5 pages):
- Pages with text: {pages_with_text}
- Pages with images: {pages_with_images}
- Total characters: {total_chars:,}
- Document type: {'Scanned/Image-based' if is_scanned else 'Text-based'}

Metadata:
- Title: {metadata.get('title', 'Not specified') if metadata else 'Not specified'}
- Author: {metadata.get('author', 'Not specified') if metadata else 'Not specified'}
- Creator: {metadata.get('creator', 'Not specified') if metadata else 'Not specified'}

Recommendation:
{'Use OCR processing for best results' if is_scanned else 'Use text extraction for best results'}
"""
        
        logger.info(f"PDF analysis completed: {page_count} pages, scanned: {is_scanned}")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing PDF: {e}")
        return f"Error analyzing PDF {file_path}: {str(e)}"

@mcp.tool()
def list_uploaded_files() -> str:
    """
    List PDF files that have been uploaded to LM Studio.
    
    Returns:
        List of uploaded PDF files ready for processing
    """
    try:
        logger.info("Listing uploaded PDF files")
        
        # Check for uploaded files
        uploaded_files = detect_uploaded_files()
        
        # Check LM Studio user directory
        username = os.getenv('USERNAME', 'user')
        lm_studio_dir = f"C:/Users/{username}/.lmstudio/user-files"
        lm_studio_exists = Path(lm_studio_dir).exists()
        
        response = f"""📤 Uploaded PDF Files in LM Studio
===================================

📂 Upload Directory: {lm_studio_dir}
📊 Directory Status: {'✅ Exists' if lm_studio_exists else '⚠️ Not found (upload a file first)'}

"""
        
        if uploaded_files:
            response += f"📋 Found {len(uploaded_files)} PDF file(s):\n\n"
            for i, file_path in enumerate(uploaded_files, 1):
                file_name = Path(file_path).name
                file_size = Path(file_path).stat().st_size
                response += f"{i}. 📄 {file_name} ({file_size:,} bytes)\n"
                response += f"   📍 Ready to process with: {file_name}\n\n"
            
            response += """💡 How to use uploaded files:
- Use just the filename (e.g., 'document.pdf')
- Server will automatically find the file
- Try: extract_pdf_text('document.pdf')
- Try: perform_ocr('document.pdf')
- Try: process_pdf_smart('document.pdf')
"""
        else:
            response += """❌ No PDF files found

📤 To upload files:
1. Drag & drop PDF files into LM Studio chat
2. Files will appear in this directory automatically
3. Then use any OCR tool with the filename

🛠️ Available processing tools:
- extract_pdf_text(filename)
- perform_ocr(filename) 
- process_pdf_smart(filename)
- analyze_pdf_structure(filename)
"""
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing uploaded files: {e}")
        return f"Error listing uploaded files: {str(e)}"

@mcp.tool()
def get_server_info() -> str:
    """
    Get server information and file upload capabilities.
    
    Returns:
        Server status and file upload information
    """
    try:
        logger.info("Providing server information")
        
        # Check LM Studio user directory
        username = os.getenv('USERNAME', 'user')
        lm_studio_dir = f"C:/Users/{username}/.lmstudio/user-files"
        lm_studio_exists = Path(lm_studio_dir).exists()
        
        # Check for uploaded files
        uploaded_count = len(detect_uploaded_files())
        
        return f"""OCR PDF MCP Server - File Upload Ready
=====================================

🔧 Server Status: ACTIVE ✅
� File Upload Support: ENABLED ✅
🇮🇩 Languages: English + Indonesian (eng+ind)
🎯 LM Studio Compatible: YES ✅

� Upload Status:
- Directory: {lm_studio_dir}
- Status: {'✅ Ready' if lm_studio_exists else '⚠️ Will be created on first upload'}
- Uploaded PDFs: {uploaded_count} files

�📤 How to Upload Files:
1. Drag & drop PDF files into LM Studio chat
2. Files are automatically stored in LM Studio directory
3. Use list_uploaded_files() to see available files
4. Process with any OCR tool using just the filename

️ Available Tools: 8 OCR processing tools
- list_uploaded_files: Show uploaded PDF files
- extract_pdf_text: Direct text extraction
- perform_ocr: OCR with Indonesian support  
- process_pdf_smart: Smart processing (text → OCR)
- analyze_pdf_structure: PDF analysis
- list_ocr_languages: Language info
- batch_process_pdfs: Multiple file processing
- get_server_info: This information

🚀 Transport: STDIO (MCP Protocol 2025-06-18)
📋 Supported Files: {', '.join(SUPPORTED_FILE_TYPES)}
"""
        
    except Exception as e:
        logger.error(f"Error getting server info: {e}")
        return f"Server active with error: {str(e)}"

@mcp.tool()
def batch_process_pdfs(directory_path: str, language: str = "eng+ind", max_files: int = 10) -> str:
    """
    Process multiple PDF files in a directory.
    
    Args:
        directory_path: Path to directory containing PDF files
        language: OCR language (default: eng+ind)
        max_files: Maximum number of files to process
        
    Returns:
        Batch processing results as formatted string
    """
    try:
        logger.info(f"Batch processing PDFs in: {directory_path}")
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find PDF files
        pdf_files = list(directory.glob("*.pdf"))[:max_files]
        
        if not pdf_files:
            return f"No PDF files found in {directory_path}"
        
        results = []
        successful = 0
        
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file.name}")
            
            try:
                # Use smart processing for each file
                content = process_pdf_smart(str(pdf_file), language)
                results.append(f"\n{'='*50}\nFile: {pdf_file.name}\n{'='*50}\n{content}")
                successful += 1
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                results.append(f"\n{'='*50}\nFile: {pdf_file.name}\n{'='*50}\nError: {str(e)}")
        
        summary = f"""Batch Processing Results:
========================

Directory: {directory_path}
Files found: {len(pdf_files)}
Files processed: {len(results)}
Successful: {successful}
Failed: {len(results) - successful}
Language used: {language}

{''.join(results)}
"""
        
        logger.info(f"Batch processing completed: {successful}/{len(results)} successful")
        return summary
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        return f"Error in batch processing {directory_path}: {str(e)}"

def main():
    """Main function to run the MCP server"""
    try:
        logger.info("🚀 Starting OCR PDF MCP Server (LM Studio File Upload Ready)")
        logger.info(f"✅ Server initialized with 8 tools (including file upload support)")
        logger.info(f"📤 File Upload: Drag & drop PDF files in LM Studio chat")
        logger.info(f"🇮🇩 Default language: eng+ind (English + Indonesian)")
        logger.info(f"📁 Supported files: {', '.join(SUPPORTED_FILE_TYPES)}")
        logger.info(f"📡 Ready for STDIO communication")
        
        # Run the server
        mcp.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()