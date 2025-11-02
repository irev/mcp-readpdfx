# Universal MCP Client Integration Guide

This guide provides integration instructions for OCR PDF MCP server with various MCP clients.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Server** (choose one)
   ```bash
   # Simple start (production mode)
   python run.py
   
   # Advanced start with options
   python run_server.py --prod --port 8000
   
   # Development mode with debug
   python run_server.py --dev
   ```

3. **Test Connection**
   ```bash
   curl http://localhost:8000/health
   ```

## MCP Protocol Endpoints

The server provides standard MCP Protocol 2025-06-18 endpoints:

- `GET /health` - Health check
- `POST /mcp/initialize` - Initialize MCP session
- `POST /mcp/tools/list` - List available tools
- `POST /mcp/tools/call` - Call MCP tools
- `GET /mcp/manifest` - Get MCP manifest
- `POST /jsonrpc` - JSON-RPC 2.0 endpoint

## Universal Configuration Template

Replace `{PATH_TO_PROJECT}` with your actual project path:

### Direct Command Configuration
```json
{
  "command": "python",
  "args": ["{PATH_TO_PROJECT}/run.py"],
  "env": {
    "PYTHONPATH": "{PATH_TO_PROJECT}",
    "MCP_SERVER_HOST": "localhost",
    "MCP_SERVER_PORT": "8000"
  }
}
```

### HTTP Configuration
```json
{
  "url": "http://localhost:8000",
  "protocol": "http",
  "endpoints": {
    "initialize": "/mcp/initialize",
    "tools_list": "/mcp/tools/list",
    "tools_call": "/mcp/tools/call",
    "manifest": "/mcp/manifest"
  }
}
```

### JSON-RPC Configuration
```json
{
  "endpoint": "http://localhost:8000/jsonrpc",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

## Available Tools

### 1. process_pdf_smart
Intelligent PDF processing with automatic OCR detection.

**Input Schema:**
```json
{
  "pdf_path": "string (required)",
  "language": "string (optional, default: 'eng')",
  "output_format": "string (optional, default: 'text')"
}
```

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "process_pdf_smart",
    "arguments": {
      "pdf_path": "/path/to/document.pdf",
      "language": "eng"
    }
  },
  "id": 1
}
```

### 2. extract_pdf_text
Direct text extraction from PDF files.

**Input Schema:**
```json
{
  "pdf_path": "string (required)",
  "page_range": "string (optional, e.g., '1-5')"
}
```

### 3. perform_ocr
OCR processing on image files.

**Input Schema:**
```json
{
  "image_path": "string (required)",
  "language": "string (optional, default: 'eng')"
}
```

### 4. analyze_pdf_structure
Analyze PDF document structure and metadata.

**Input Schema:**
```json
{
  "pdf_path": "string (required)"
}
```

### 5. batch_process_pdfs
Process multiple PDFs in batch mode.

**Input Schema:**
```json
{
  "input_directory": "string (required)",
  "output_directory": "string (optional)",
  "file_pattern": "string (optional, default: '*.pdf')"
}
```

## Client-Specific Configurations

- **[Claude Desktop](./claude-desktop.md)** - Desktop app integration
- **[LM Studio](./lm-studio.md)** - Local LM integration
- **[Continue.dev](./continue-dev.md)** - VS Code extension
- **[Cursor](./cursor.md)** - Cursor IDE integration

## Common Integration Patterns

### 1. Subprocess Integration
```python
import subprocess
import json

def call_mcp_tool(tool_name, arguments):
    cmd = ["python", "run.py"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": 1
    }
    
    proc.stdin.write(json.dumps(request).encode())
    proc.stdin.close()
    
    response = proc.stdout.read()
    return json.loads(response)
```

### 2. HTTP Client Integration
```python
import requests

def call_mcp_http(tool_name, arguments):
    response = requests.post("http://localhost:8000/mcp/tools/call", json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
        "id": 1
    })
    return response.json()
```

### 3. WebSocket Integration
```python
import websockets
import json
import asyncio

async def call_mcp_websocket(tool_name, arguments):
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
            "id": 1
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        return json.loads(response)
```

## Environment Setup

### Windows
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract (for OCR)
choco install tesseract

# Add to PATH
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

### macOS
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract
brew install tesseract
```

### Linux
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract
sudo apt-get install tesseract-ocr
```

## Troubleshooting

### Server Issues
```bash
# Check if server is running
curl http://localhost:8000/health

# View server logs
python run_server.py --dev

# Test tool manually
curl -X POST http://localhost:8000/mcp/tools/list \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### Common Problems

1. **Port Already in Use**
   ```bash
   python run_server.py --port 8001
   ```

2. **Permission Denied**
   - Check file path permissions
   - Run with appropriate user privileges

3. **Tesseract Not Found**
   - Install Tesseract OCR
   - Add to system PATH
   - Set TESSERACT_CMD environment variable

4. **Module Import Errors**
   - Verify PYTHONPATH is set correctly
   - Install all requirements: `pip install -r requirements.txt`

## Testing

### Unit Tests
```bash
python test_mcp_server.py
```

### Manual Testing
```bash
# Start server
python run.py

# In another terminal, test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/mcp/tools/list -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

## Repository

**GitHub**: https://github.com/irev/mcp-readpdfx  
**Issues**: https://github.com/irev/mcp-readpdfx/issues  
**Documentation**: https://github.com/irev/mcp-readpdfx#readme