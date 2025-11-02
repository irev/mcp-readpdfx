#!/usr/bin/env python3
"""
MCP Standard Tools Implementation

OCR PDF tools yang mengikuti MCP Protocol standard dengan proper
error handling, type safety, dan structure yang rapi.
"""

import os
import sys
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import asdict
import time

try:
    from .mcp_types import (
        MCPTool, MCPToolInputSchema, MCPContent, MCPTextContent, MCPToolResult,
        create_text_content, create_tool_result, create_tool_result_from_text_list
    )
except ImportError:
    from mcp_types import (
        MCPTool, MCPToolInputSchema, MCPContent, MCPTextContent, MCPToolResult,
        create_text_content, create_tool_result, create_tool_result_from_text_list
    )

# Import OCR modules from main package  
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
ocr_pkg_path = project_root / "ocr_pdf_mcp"
sys.path.insert(0, str(project_root))

from ocr_pdf_mcp.pdf_text_extractor import PDFTextExtractor
from ocr_pdf_mcp.ocr_worker import OCRWorker  
from ocr_pdf_mcp.pdf_utils import PDFUtils

logger = logging.getLogger(__name__)

class MCPToolsRegistry:
    """Registry untuk MCP Tools dengan proper validation dan error handling"""
    
    def __init__(self):
        self.pdf_extractor = PDFTextExtractor()
        self.ocr_worker = OCRWorker()
        self.pdf_utils = PDFUtils()
        
        # Tools definitions
        self._tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all MCP-compliant tools"""
        
        # 1. Smart PDF Processing Tool
        self._tools["process_pdf_smart"] = MCPTool(
            name="process_pdf_smart",
            description="Intelligently process PDF with automatic detection of digital text vs scanned content. Uses OCR only when necessary.",
            inputSchema=MCPToolInputSchema(
                type="object",
                properties={
                    "pdf_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF file to process"
                    },
                    "language": {
                        "type": "string", 
                        "description": "OCR language code (e.g., 'eng', 'ind', 'eng+ind')",
                        "default": "eng+ind"
                    },
                    "force_ocr": {
                        "type": "boolean",
                        "description": "Force OCR processing even for digital text",
                        "default": False
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include processing metadata in result",
                        "default": True
                    }
                },
                required=["pdf_path"]
            )
        )
        
        # 2. Extract Digital Text Tool
        self._tools["extract_pdf_text"] = MCPTool(
            name="extract_pdf_text",
            description="Extract text from digital PDF documents using built-in text data. Fast processing for PDFs with embedded text.",
            inputSchema=MCPToolInputSchema(
                type="object",
                properties={
                    "pdf_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF file"
                    },
                    "page_range": {
                        "type": "string",
                        "description": "Page range to extract (e.g., '1-5', '1,3,5', or 'all')",
                        "default": "all"
                    },
                    "preserve_layout": {
                        "type": "boolean",
                        "description": "Attempt to preserve text layout and formatting",
                        "default": True
                    }
                },
                required=["pdf_path"]
            )
        )
        
        # 3. OCR Processing Tool
        self._tools["ocr_pdf_pages"] = MCPTool(
            name="ocr_pdf_pages",
            description="Perform OCR (Optical Character Recognition) on scanned PDF pages. Best for image-based PDFs or when text extraction fails.",
            inputSchema=MCPToolInputSchema(
                type="object",
                properties={
                    "pdf_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF file"
                    },
                    "language": {
                        "type": "string",
                        "description": "Tesseract OCR language code",
                        "default": "eng"
                    },
                    "max_workers": {
                        "type": "integer",
                        "description": "Maximum number of parallel OCR workers",
                        "default": 4,
                        "minimum": 1,
                        "maximum": 8
                    },
                    "dpi": {
                        "type": "integer", 
                        "description": "Image resolution for OCR processing",
                        "default": 300,
                        "minimum": 150,
                        "maximum": 600
                    },
                    "page_range": {
                        "type": "string",
                        "description": "Page range to process (e.g., '1-5', '1,3,5', or 'all')",
                        "default": "all"
                    }
                },
                required=["pdf_path"]
            )
        )
        
        # 4. PDF Information Tool
        self._tools["get_pdf_info"] = MCPTool(
            name="get_pdf_info",
            description="Get comprehensive PDF document information including metadata, page count, text analysis, and OCR recommendations.",
            inputSchema=MCPToolInputSchema(
                type="object",
                properties={
                    "pdf_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF file"
                    },
                    "analyze_content": {
                        "type": "boolean",
                        "description": "Perform content analysis (text density, images, etc.)",
                        "default": True
                    },
                    "check_ocr_needed": {
                        "type": "boolean",
                        "description": "Check if OCR processing is recommended",
                        "default": True
                    },
                    "include_sample_text": {
                        "type": "boolean",
                        "description": "Include sample text from first pages",
                        "default": False
                    }
                },
                required=["pdf_path"]
            )
        )
        
        # 5. Batch Processing Tool
        self._tools["batch_process_pdfs"] = MCPTool(
            name="batch_process_pdfs",
            description="Process multiple PDF files in batch with consistent settings. Useful for processing document collections.",
            inputSchema=MCPToolInputSchema(
                type="object",
                properties={
                    "input_directory": {
                        "type": "string",
                        "description": "Directory containing PDF files to process"
                    },
                    "output_directory": {
                        "type": "string",
                        "description": "Directory to save processed results"
                    },
                    "processing_mode": {
                        "type": "string",
                        "description": "Processing mode for all files",
                        "enum": ["smart", "extract_only", "ocr_only"],
                        "default": "smart"
                    },
                    "language": {
                        "type": "string",
                        "description": "OCR language for batch processing",
                        "default": "eng+ind"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "File pattern to match (e.g., '*.pdf', 'report_*.pdf')",
                        "default": "*.pdf"
                    },
                    "max_files": {
                        "type": "integer",
                        "description": "Maximum number of files to process",
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                required=["input_directory", "output_directory"]
            )
        )
        
        logger.info(f"Initialized {len(self._tools)} MCP tools")
    
    # Tool Implementations
    async def process_pdf_smart(self, pdf_path: str, language: str = "eng+ind", 
                              force_ocr: bool = False, include_metadata: bool = True) -> MCPToolResult:
        """Smart PDF processing with automatic text/OCR detection"""
        try:
            # Validate file exists
            if not os.path.exists(pdf_path):
                error_content = [create_text_content(f"File not found: {pdf_path}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
            
            start_time = time.time()
            
            # Get PDF info first
            pdf_info = await self.get_pdf_info(pdf_path, analyze_content=True, check_ocr_needed=True)
            if pdf_info.isError:
                return pdf_info
            
            # Parse PDF info to decide processing method
            info_text = getattr(pdf_info.content[0], "text", "{}") if pdf_info.content else "{}"
            needs_ocr = "OCR recommended: true" in info_text or force_ocr
            
            if needs_ocr:
                # Use OCR processing
                logger.info(f"Using OCR processing for: {pdf_path}")
                result = await self.ocr_pdf_pages(pdf_path, language=language)
            else:
                # Use text extraction
                logger.info(f"Using text extraction for: {pdf_path}")
                result = await self.extract_pdf_text(pdf_path)
            
            if result.isError:
                return result
            
            # Add metadata if requested
            if include_metadata:
                processing_time = time.time() - start_time
                method = "OCR" if needs_ocr else "Text Extraction"
                
                metadata_text = f"\n\n--- Processing Metadata ---\n"
                metadata_text += f"Method: {method}\n"
                metadata_text += f"Language: {language}\n"
                metadata_text += f"Processing Time: {processing_time:.2f}s\n"
                metadata_text += f"Force OCR: {force_ocr}\n"
                
                # Add metadata to result
                result.content.append(create_text_content(metadata_text))
            
            return result
            
        except Exception as e:
            logger.error(f"Smart processing error: {e}")
            error_content = [create_text_content(f"Smart processing failed: {str(e)}")]
            return create_tool_result_from_text_list(error_content, is_error=True)
    
    async def extract_pdf_text(self, pdf_path: str, page_range: str = "all", 
                             preserve_layout: bool = True) -> MCPToolResult:
        """Extract text from digital PDF"""
        try:
            if not os.path.exists(pdf_path):
                error_content = [create_text_content(f"File not found: {pdf_path}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
            
            # Extract text using existing extractor
            result = self.pdf_extractor.extract_text(pdf_path, preserve_layout=preserve_layout)
            
            if result.get("success", False):
                extracted_text = result.get("text", "")
                page_count = result.get("pages", 0)
                
                content_text = f"--- PDF Text Extraction Results ---\n"
                content_text += f"File: {os.path.basename(pdf_path)}\n"
                content_text += f"Pages: {page_count}\n"
                content_text += f"Characters: {len(extracted_text)}\n"
                content_text += f"Preserve Layout: {preserve_layout}\n\n"
                content_text += "--- Extracted Text ---\n"
                content_text += extracted_text
                
                content = [create_text_content(content_text)]
                return create_tool_result_from_text_list(content, is_error=False)
            else:
                error_msg = result.get("error", "Unknown error")
                error_content = [create_text_content(f"Text extraction failed: {error_msg}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
                
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            error_content = [create_text_content(f"Text extraction failed: {str(e)}")]
            return create_tool_result_from_text_list(error_content, is_error=True)
    
    async def ocr_pdf_pages(self, pdf_path: str, language: str = "eng", 
                          max_workers: int = 4, dpi: int = 300, 
                          page_range: str = "all") -> MCPToolResult:
        """Perform OCR on PDF pages"""
        try:
            if not os.path.exists(pdf_path):
                error_content = [create_text_content(f"File not found: {pdf_path}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
            
            # Validate parameters
            if max_workers < 1 or max_workers > 8:
                max_workers = 4
            if dpi < 150 or dpi > 600:
                dpi = 300
            
            # Perform OCR using existing worker
            result = await self.ocr_worker.process_pdf(
                pdf_path, 
                language=language,
                max_workers=max_workers,
                dpi=dpi
            )
            
            if result.get("success", False):
                ocr_text = result.get("text", "")
                pages_processed = result.get("pages_processed", 0)
                processing_time = result.get("processing_time", 0)
                
                content_text = f"--- OCR Processing Results ---\n"
                content_text += f"File: {os.path.basename(pdf_path)}\n"
                content_text += f"Language: {language}\n"
                content_text += f"Pages Processed: {pages_processed}\n"
                content_text += f"Processing Time: {processing_time:.2f}s\n"
                content_text += f"Workers: {max_workers}\n"
                content_text += f"DPI: {dpi}\n"
                content_text += f"Characters: {len(ocr_text)}\n\n"
                content_text += "--- OCR Text ---\n"
                content_text += ocr_text
                
                content = [create_text_content(content_text)]
                return create_tool_result_from_text_list(content, is_error=False)
            else:
                error_msg = result.get("error", "Unknown error")
                error_content = [create_text_content(f"OCR processing failed: {error_msg}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
                
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            error_content = [create_text_content(f"OCR processing failed: {str(e)}")]
            return create_tool_result_from_text_list(error_content, is_error=True)
    
    async def get_pdf_info(self, pdf_path: str, analyze_content: bool = True,
                         check_ocr_needed: bool = True, include_sample_text: bool = False) -> MCPToolResult:
        """Get PDF information and analysis"""
        try:
            if not os.path.exists(pdf_path):
                error_content = [create_text_content(f"File not found: {pdf_path}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
            
            # Get PDF info using existing utils
            info = self.pdf_utils.get_pdf_info(pdf_path)
            
            if info.get("success", False):
                info_text = f"--- PDF Document Information ---\n"
                info_text += f"File: {os.path.basename(pdf_path)}\n"
                info_text += f"Size: {info.get('file_size', 0)} bytes\n"
                info_text += f"Pages: {info.get('pages', 0)}\n"
                info_text += f"Created: {info.get('created', 'Unknown')}\n"
                info_text += f"Modified: {info.get('modified', 'Unknown')}\n"
                info_text += f"Author: {info.get('author', 'Unknown')}\n"
                info_text += f"Title: {info.get('title', 'Unknown')}\n"
                info_text += f"Subject: {info.get('subject', 'Unknown')}\n"
                info_text += f"Producer: {info.get('producer', 'Unknown')}\n"
                
                if analyze_content:
                    info_text += f"\n--- Content Analysis ---\n"
                    info_text += f"Has text: {info.get('has_text', False)}\n"
                    info_text += f"Has images: {info.get('has_images', False)}\n"
                    info_text += f"Text density: {info.get('text_density', 0):.2f}%\n"
                    info_text += f"Encrypted: {info.get('encrypted', False)}\n"
                
                if check_ocr_needed:
                    ocr_needed = info.get('text_density', 0) < 50  # Low text density suggests scanned PDF
                    info_text += f"\n--- OCR Analysis ---\n"
                    info_text += f"OCR recommended: {ocr_needed}\n"
                    info_text += f"Reason: {'Low text density - likely scanned document' if ocr_needed else 'Good text density - digital document'}\n"
                
                if include_sample_text and info.get('has_text', False):
                    sample_text = info.get('sample_text', '')
                    if sample_text:
                        info_text += f"\n--- Sample Text (First 500 chars) ---\n"
                        info_text += sample_text[:500]
                        if len(sample_text) > 500:
                            info_text += "..."
                
                content = [create_text_content(info_text)]
                return create_tool_result_from_text_list(content, is_error=False)
            else:
                error_msg = info.get("error", "Unknown error")
                error_content = [create_text_content(f"PDF analysis failed: {error_msg}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
                
        except Exception as e:
            logger.error(f"PDF info error: {e}")
            error_content = [create_text_content(f"PDF analysis failed: {str(e)}")]
            return create_tool_result_from_text_list(error_content, is_error=True)
    
    async def batch_process_pdfs(self, input_directory: str, output_directory: str,
                               processing_mode: str = "smart", language: str = "eng+ind",
                               file_pattern: str = "*.pdf", max_files: int = 100) -> MCPToolResult:
        """Batch process multiple PDF files"""
        try:
            import glob
            
            if not os.path.exists(input_directory):
                error_content = [create_text_content(f"Input directory not found: {input_directory}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
            
            # Create output directory if needed
            os.makedirs(output_directory, exist_ok=True)
            
            # Find PDF files
            pattern = os.path.join(input_directory, file_pattern)
            pdf_files = glob.glob(pattern)[:max_files]
            
            if not pdf_files:
                error_content = [create_text_content(f"No PDF files found matching pattern: {file_pattern}")]
                return create_tool_result_from_text_list(error_content, is_error=True)
            
            results = []
            processed_count = 0
            error_count = 0
            
            for pdf_file in pdf_files:
                try:
                    # Process based on mode
                    if processing_mode == "smart":
                        result = await self.process_pdf_smart(pdf_file, language=language)
                    elif processing_mode == "extract_only":
                        result = await self.extract_pdf_text(pdf_file)
                    elif processing_mode == "ocr_only":
                        result = await self.ocr_pdf_pages(pdf_file, language=language)
                    else:
                        result = await self.process_pdf_smart(pdf_file, language=language)
                    
                    # Save result
                    output_file = os.path.join(output_directory, f"{os.path.basename(pdf_file)}.txt")
                    if result.content:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    f.write(content_item.text)
                    
                    if result.isError:
                        error_count += 1
                        results.append(f"ERROR - {os.path.basename(pdf_file)}: {result.content[0].text if result.content else 'Unknown error'}")
                    else:
                        processed_count += 1
                        results.append(f"SUCCESS - {os.path.basename(pdf_file)}: {len(result.content[0].text) if result.content else 0} characters")
                        
                except Exception as file_error:
                    error_count += 1
                    results.append(f"ERROR - {os.path.basename(pdf_file)}: {str(file_error)}")
            
            # Create summary
            summary_text = f"--- Batch Processing Results ---\n"
            summary_text += f"Input Directory: {input_directory}\n"
            summary_text += f"Output Directory: {output_directory}\n"
            summary_text += f"Processing Mode: {processing_mode}\n"
            summary_text += f"Language: {language}\n"
            summary_text += f"File Pattern: {file_pattern}\n"
            summary_text += f"Files Found: {len(pdf_files)}\n"
            summary_text += f"Successfully Processed: {processed_count}\n"
            summary_text += f"Errors: {error_count}\n\n"
            summary_text += "--- Individual Results ---\n"
            summary_text += "\n".join(results)
            
            content = [create_text_content(summary_text)]
            is_error = error_count > processed_count  # More errors than successes
            return create_tool_result(content, is_error=is_error)
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            error_content = [create_text_content(f"Batch processing failed: {str(e)}")]
            return create_tool_result_from_text_list(error_content, is_error=True)
    
    # Registry Methods
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get tool definition"""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[MCPTool]:
        """List all tools"""
        return list(self._tools.values())
    
    def get_tool_handler(self, tool_name: str) -> Optional[callable]:
        """Get tool handler method"""
        handler_map = {
            "process_pdf_smart": self.process_pdf_smart,
            "extract_pdf_text": self.extract_pdf_text,
            "ocr_pdf_pages": self.ocr_pdf_pages,
            "get_pdf_info": self.get_pdf_info,
            "batch_process_pdfs": self.batch_process_pdfs
        }
        return handler_map.get(tool_name)