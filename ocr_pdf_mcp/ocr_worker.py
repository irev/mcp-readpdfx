"""
OCR Worker Module for OCR PDF MCP Server v1.0.0
Handles parallel OCR processing of PDF pages using Tesseract
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from ocr_pdf_mcp.config import Config

# Setup logging
logger = logging.getLogger(__name__)

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH

class OCRWorker:
    """Production OCR worker with error handling and optimization"""
    
    def __init__(self, language: Optional[str] = None, timeout: Optional[int] = None):
        self.language = language or Config.OCR_LANGUAGE
        self.timeout = timeout or Config.OCR_TIMEOUT_SECONDS
        
    def ocr_page(self, image: Image.Image, page_num: int) -> Dict[str, Any]:
        """Process single page with OCR"""
        start_time = time.time()
        
        try:
            # OCR configuration for better accuracy
            config = f'-l {self.language} --oem 3 --psm 6'
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image, 
                lang=self.language,
                config=config,
                timeout=self.timeout
            )
            
            processing_time = round(time.time() - start_time, 2)
            
            # Get confidence data if available
            try:
                data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            except:
                avg_confidence = None
            
            return {
                "page": page_num,
                "type": "ocr",
                "text": text.strip(),
                "language": self.language,
                "processing_time": processing_time,
                "character_count": len(text.strip()),
                "word_count": len(text.strip().split()),
                "confidence": round(avg_confidence, 1) if avg_confidence else None,
                "status": "success"
            }
            
        except pytesseract.TesseractError as e:
            logger.error(f"Tesseract error on page {page_num}: {e}")
            return {
                "page": page_num,
                "type": "ocr",
                "text": "",
                "error": f"Tesseract error: {str(e)}",
                "processing_time": round(time.time() - start_time, 2),
                "status": "error"
            }
        except Exception as e:
            logger.error(f"OCR error on page {page_num}: {e}")
            return {
                "page": page_num,
                "type": "ocr", 
                "text": "",
                "error": str(e),
                "processing_time": round(time.time() - start_time, 2),
                "status": "error"
            }

def process_ocr_pdf(path: str, max_workers: Optional[int] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Process PDF with OCR using parallel workers
    
    Args:
        path: Path to PDF file
        max_workers: Maximum number of parallel workers
        language: OCR language(s)
    
    Returns:
        List of page results with OCR text and metadata
    """
    start_time = time.time()
    max_workers = max_workers or Config.MAX_WORKERS
    language = language or Config.OCR_LANGUAGE
    
    logger.info(f"Starting OCR processing: {path}")
    logger.info(f"Language: {language}, Workers: {max_workers}")
    
    try:
        # Convert PDF to images
        logger.info("Converting PDF to images...")
        convert_start = time.time()
        
        pages = convert_from_path(
            path,
            dpi=300,  # High DPI for better OCR accuracy
            fmt='PNG',
            thread_count=max_workers
        )
        
        convert_time = round(time.time() - convert_start, 2)
        logger.info(f"PDF conversion completed in {convert_time}s - {len(pages)} pages")
        
        # Initialize OCR worker
        worker = OCRWorker(language=language)
        
        # Process pages in parallel
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_page = {
                executor.submit(worker.ocr_page, page, page_num): page_num
                for page_num, page in enumerate(pages, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Log progress
                    status = "✅" if result["status"] == "success" else "❌"
                    chars = result.get("character_count", 0)
                    conf = result.get("confidence")
                    conf_str = f", conf: {conf}%" if conf else ""
                    logger.debug(f"{status} Page {page_num}: {chars} chars{conf_str}")
                    
                except Exception as e:
                    logger.error(f"Failed to process page {page_num}: {e}")
                    results.append({
                        "page": page_num,
                        "type": "ocr",
                        "text": "",
                        "error": str(e),
                        "status": "error"
                    })
        
        # Sort results by page number
        results.sort(key=lambda x: x["page"])
        
        # Calculate summary statistics
        total_time = round(time.time() - start_time, 2)
        successful_pages = sum(1 for r in results if r["status"] == "success")
        total_chars = sum(r.get("character_count", 0) for r in results)
        avg_confidence = None
        
        confidences = [r.get("confidence") for r in results if r.get("confidence")]
        if confidences:
            avg_confidence = round(sum(confidences) / len(confidences), 1)
        
        logger.info(f"OCR completed in {total_time}s")
        logger.info(f"Success rate: {successful_pages}/{len(results)} pages")
        logger.info(f"Total characters: {total_chars:,}")
        if avg_confidence:
            logger.info(f"Average confidence: {avg_confidence}%")
        
        return results
        
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise
