# 🌐 OCR PDF HTTP Server - ML Studio Integration Guide

## 📋 Overview

HTTP server kompatibel dengan ML Studio dan client HTTP lainnya yang menyediakan OCR dan PDF processing capabilities melalui REST API endpoints.

## 🚀 Quick Start untuk ML Studio

### 1. Start HTTP Server

```bash
# Cara 1: Menggunakan script launcher
python start_http_server.py --port 8000

# Cara 2: Langsung dengan uvicorn
python -m uvicorn http_server:app --host 127.0.0.1 --port 8000

# Cara 3: Development mode (auto-reload)
python -m uvicorn http_server:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Verify Server Status

**URL**: `http://127.0.0.1:8000`

Server akan mengembalikan response:
```json
{
  "status": "healthy",
  "service": "OCR PDF HTTP Server",
  "version": "1.0.0",
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
}
```

## 🔧 API Endpoints untuk ML Studio

### 1. Health Check
- **URL**: `GET http://127.0.0.1:8000/health`
- **Purpose**: Check server status
- **Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
  "default_language": "eng+ind",
  "max_workers": 4
}
```

### 2. Server Information
- **URL**: `GET http://127.0.0.1:8000/info`
- **Purpose**: Get detailed server configuration
- **Response**: Comprehensive server info and endpoint descriptions

### 3. PDF Information
- **URL**: `POST http://127.0.0.1:8000/pdf/info`
- **Purpose**: Get PDF metadata and type detection
- **Body**: 
```
Content-Type: application/x-www-form-urlencoded
file_path=/path/to/your/file.pdf
```
- **Response**:
```json
{
  "status": "success",
  "operation": "get_pdf_info",
  "file_name": "document.pdf",
  "total_pages": 5,
  "is_scanned": false,
  "processing_method": "Text extraction",
  "metadata": {...}
}
```

### 4. Extract Text (Digital PDFs)
- **URL**: `POST http://127.0.0.1:8000/pdf/extract`
- **Purpose**: Extract text from digital PDFs
- **Body**:
```
Content-Type: application/x-www-form-urlencoded
file_path=/path/to/your/file.pdf
```

### 5. OCR Processing (Scanned PDFs)
- **URL**: `POST http://127.0.0.1:8000/pdf/ocr`
- **Purpose**: Perform OCR on scanned documents
- **Body**:
```
Content-Type: application/x-www-form-urlencoded
file_path=/path/to/your/file.pdf
language=eng+ind
max_workers=4
```

### 6. Smart Processing (Recommended)
- **URL**: `POST http://127.0.0.1:8000/pdf/smart`
- **Purpose**: Auto-detect and process PDF optimally
- **Body**:
```
Content-Type: application/x-www-form-urlencoded
file_path=/path/to/your/file.pdf
language=eng+ind
force_ocr=false
```

### 7. Upload and Process
- **URL**: `POST http://127.0.0.1:8000/pdf/upload`
- **Purpose**: Upload PDF file and process it
- **Body**:
```
Content-Type: multipart/form-data
file: [PDF file]
operation: smart_process
language: eng+ind
```

## 🧪 Testing dengan cURL

### Basic Health Check
```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### Get PDF Information
```bash
curl -X POST "http://127.0.0.1:8000/pdf/info" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_path=d:/AI/MCP/python/ocr_pdf_mcp/pdf-test/dokumen.pdf"
```

### Smart Processing
```bash
curl -X POST "http://127.0.0.1:8000/pdf/smart" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_path=d:/AI/MCP/python/ocr_pdf_mcp/pdf-test/dokumen.pdf&language=eng+ind"
```

### Upload and Process
```bash
curl -X POST "http://127.0.0.1:8000/pdf/upload" \
  -F "file=@d:/AI/MCP/python/ocr_pdf_mcp/pdf-test/dokumen.pdf" \
  -F "operation=smart_process" \
  -F "language=eng+ind"
```

## 🧪 Testing dengan PowerShell

### Health Check
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

### PDF Processing
```powershell
$body = @{
    file_path = "d:/AI/MCP/python/ocr_pdf_mcp/pdf-test/dokumen.pdf"
    language = "eng+ind"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/pdf/smart" -Method Post -Body $body
```

## 🔧 ML Studio Configuration

### Step 1: Start Server
```bash
cd d:\AI\MCP\python\ocr_pdf_mcp
python start_http_server.py --port 8000
```

### Step 2: Configure ML Studio
- **Base URL**: `http://127.0.0.1:8000`
- **Health Check Endpoint**: `/health`
- **Main Processing Endpoint**: `/pdf/smart`

### Step 3: Test Connection
Akses `http://127.0.0.1:8000` di browser untuk melihat server info dan available endpoints.

## 📊 Response Format

All endpoints return JSON with consistent structure:

### Success Response
```json
{
  "status": "success",
  "operation": "operation_name",
  "file_path": "/path/to/file.pdf",
  "file_name": "document.pdf",
  "processing_method": "OCR|Text extraction",
  "total_pages": 5,
  "pages_with_text": 5,
  "total_characters": 12500,
  "total_words": 2100,
  "pages": [
    {
      "page_number": 1,
      "text": "Extracted text content...",
      "character_count": 2500,
      "word_count": 420
    }
  ],
  "server_version": "1.0.0"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Error description",
  "operation": "operation_name",
  "server_version": "1.0.0"
}
```

## ⚡ Performance Tips

1. **Use Smart Processing**: `/pdf/smart` endpoint automatically detects optimal processing method
2. **Adjust Workers**: Set `max_workers` based on your CPU cores
3. **Language Optimization**: Use specific language codes for better OCR accuracy
4. **File Size**: Large files may take longer to process

## 🔍 Monitoring

### Server Logs
Server logs show all processing activities:
```
2025-11-02 19:53:25,898 - http_server - INFO - 🚀 OCR PDF HTTP Server v1.0.0 initializing...
2025-11-02 19:53:25,898 - http_server - INFO - 📍 Tesseract: C:\Program Files\Tesseract-OCR\tesseract.exe
2025-11-02 19:53:25,898 - http_server - INFO - 🌍 Default Language: eng+ind
2025-11-02 19:53:25,899 - http_server - INFO - ⚡ Max Workers: 4
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Health Monitoring
Regular health checks can be automated:
```bash
curl -f http://127.0.0.1:8000/health || echo "Server is down"
```

## 🐛 Troubleshooting

### Common Issues

1. **404 Error pada ML Studio**:
   - ✅ **Solution**: Server sekarang menyediakan proper HTTP endpoints
   - Test dengan: `curl http://127.0.0.1:8000/health`

2. **Server tidak start**:
   - Check Tesseract path dalam `.env`
   - Install dependencies: `pip install fastapi uvicorn python-multipart`

3. **OCR Error**:
   - Verify Tesseract installation
   - Check language packs: `tesseract --list-langs`

4. **File not found**:
   - Use absolute paths: `d:/AI/MCP/python/ocr_pdf_mcp/pdf-test/dokumen.pdf`
   - Ensure file exists and is accessible

## 🌐 API Documentation

Interactive API documentation tersedia di:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 🔒 Security Notes

- Server berjalan local (127.0.0.1) untuk security
- File upload menggunakan temporary directory
- Input validation untuk semua endpoints
- No external network calls required

---

**✅ ML Studio Integration Status: RESOLVED**

HTTP server sekarang menyediakan proper REST API endpoints yang kompatibel dengan ML Studio dan client HTTP lainnya, mengatasi issue 404 yang sebelumnya terjadi.