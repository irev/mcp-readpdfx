from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ocr_pdf_mcp.pdf_utils import get_pdf_info
from ocr_pdf_mcp.ocr_worker import process_ocr_pdf
from ocr_pdf_mcp.pdf_text_extractor import extract_text_from_pdf
from ocr_pdf_mcp.config import Config
import time
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OCR PDF MCP", description="OCR PDF Processing API")

class PDFRequest(BaseModel):
    path: str

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "OCR PDF MCP API", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "tesseract_path": Config.TESSERACT_PATH,
        "tesseract_available": os.path.exists(Config.TESSERACT_PATH)
    }

@app.post("/analyze_pdf")
def analyze_pdf(request: PDFRequest):
    """Analyze PDF file with OCR or digital text extraction"""
    
    start = time.time()
    
    try:
        # Check if file exists
        if not os.path.exists(request.path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.path}")
        
        logger.info(f"Processing file: {request.path}")
        
        # Get PDF info
        info = get_pdf_info(request.path)
        logger.info(f"PDF info: {info}")
        
        # Process based on type
        if info["is_scanned"]:
            logger.info("Processing with OCR...")
            pages = process_ocr_pdf(request.path)
        else:
            logger.info("Extracting digital text...")
            pages = extract_text_from_pdf(request.path)
        
        processing_time = round(time.time() - start, 2)
        logger.info(f"Processing completed in {processing_time}s")
        
        return {
            "file": os.path.basename(request.path),
            "total_pages": info["total_pages"],
            "mode": "ocr" if info["is_scanned"] else "digital",
            "pages": pages,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing {request.path}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ocr_pdf_mcp.main:app", host="0.0.0.0", port=Config.PORT, reload=True)
