# LM Studio MCP Configuration

This configuration enables OCR PDF MCP server integration with LM Studio.

## Prerequisites

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the MCP server:
   ```bash
   python run.py
   ```

## LM Studio Configuration

### Method 1: Direct MCP Integration

1. Open LM Studio
2. Go to **Settings** → **Extensions** → **MCP Servers**
3. Add new MCP server with these settings:

**Server Name**: `ocr-pdf`
**Command**: `python`
**Arguments**:
```
D:\AI\MCP\python\ocr_pdf_mcp\run.py
```

**Environment Variables**:
```
PYTHONPATH=D:\AI\MCP\python\ocr_pdf_mcp
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
```

### Method 2: HTTP Server Configuration

1. Start the HTTP server:
   ```bash
   python run_server.py --prod --port 8000
   ```

2. In LM Studio, configure HTTP connection:
   - **URL**: `http://localhost:8000`
   - **Protocol**: `HTTP`
   - **Content-Type**: `application/json`

### Method 3: JSON-RPC Configuration

Configure LM Studio to use JSON-RPC endpoint:

**Endpoint**: `http://localhost:8000/jsonrpc`
**Method**: `POST`
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

## Available Tools

- **process_pdf_smart**: Intelligent PDF processing with automatic OCR detection
- **extract_pdf_text**: Direct text extraction from PDFs
- **perform_ocr**: OCR on image files (PNG, JPG, etc.)
- **analyze_pdf_structure**: Analyze PDF document structure and metadata
- **batch_process_pdfs**: Process multiple PDFs in batch mode

## Usage Examples

### Smart PDF Processing
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "process_pdf_smart",
    "arguments": {
      "pdf_path": "C:\\path\\to\\document.pdf",
      "language": "eng"
    }
  },
  "id": 1
}
```

### OCR Image
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "perform_ocr",
    "arguments": {
      "image_path": "C:\\path\\to\\image.png",
      "language": "eng"
    }
  },
  "id": 2
}
```

## Troubleshooting

1. **Connection Issues**: Ensure server is running on correct port
2. **Permission Errors**: Check file path permissions
3. **Tesseract Issues**: Install Tesseract OCR and add to PATH

## Repository

GitHub: https://github.com/irev/mcp-readpdfx