# ReadPDFx - OCR PDF MCP Server

> **Production-ready MCP Protocol 2025-06-18 compliant server for OCR PDF processing**

[![MCP Protocol](https://img.shields.io/badge/MCP-2025--06--18-blue)](https://github.com/irev/mcp-readpdfx)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)

ReadPDFx is a comprehensive MCP (Model Context Protocol) server that provides intelligent OCR and PDF processing capabilities. It automatically detects whether a PDF contains digital text or scanned images and applies the appropriate processing method.

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
# Simple production start
python run.py

# Advanced start with options
python run_server.py --prod --port 8000

# Development mode
python run_server.py --dev
```

### 3. Test Connection
```bash
curl http://localhost:8000/health
```

## 🚀 Features

- **Smart PDF Processing**: Automatically detects digital vs scanned content
- **MCP Protocol 2025-06-18 Compliant**: Full standard implementation  
- **Multiple Client Support**: Claude Desktop, LM Studio, Continue.dev, Cursor
- **HTTP + JSON-RPC**: Multiple connection methods
- **Production Ready**: Comprehensive error handling and logging
- **Batch Processing**: Handle multiple files efficiently
- **OCR Support**: Advanced OCR with Tesseract integration

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR

### Windows
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Tesseract
choco install tesseract
```

### macOS
```bash
pip install -r requirements.txt
brew install tesseract
```

### Linux
```bash
pip install -r requirements.txt
sudo apt-get install tesseract-ocr
```

## 📋 Available Tools

### 1. Smart PDF Processing
Intelligent processing with automatic OCR detection:
```json
{
  "name": "process_pdf_smart",
  "arguments": {
    "pdf_path": "/path/to/document.pdf",
    "language": "eng"
  }
}
```

### 2. PDF Text Extraction
Direct text extraction from digital PDFs:
```json
{
  "name": "extract_pdf_text", 
  "arguments": {
    "pdf_path": "/path/to/document.pdf",
    "page_range": "1-5"
  }
}
```

### 3. OCR Processing
OCR on image files:
```json
{
  "name": "perform_ocr",
  "arguments": {
    "image_path": "/path/to/image.png",
    "language": "eng"
  }
}
```

### 4. PDF Structure Analysis
Analyze document structure and metadata:
```json
{
  "name": "analyze_pdf_structure",
  "arguments": {
    "pdf_path": "/path/to/document.pdf"
  }
}
```

### 5. Batch Processing
Process multiple files:
```json
{
  "name": "batch_process_pdfs",
  "arguments": {
    "input_directory": "/path/to/pdfs/",
    "output_directory": "/path/to/output/",
    "file_pattern": "*.pdf"
  }
}
```

## 🔌 Client Integration

### Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "readpdfx": {
      "command": "python",
      "args": ["path/to/readpdfx/run.py"],
      "env": {
        "PYTHONPATH": "path/to/readpdfx"
      }
    }
  }
}
```

### LM Studio
Configure MCP server with:
- **Command**: `python`
- **Args**: `path/to/readpdfx/run.py`
- **URL**: `http://localhost:8000` (HTTP mode)

### Continue.dev
Add to config.json:
```json
{
  "contextProviders": [
    {
      "name": "mcp",
      "params": {
        "command": "python",
        "args": ["path/to/readpdfx/run.py"]
      }
    }
  ]
}
```

### Cursor
Configure in settings.json:
```json
{
  "mcp.servers": {
    "readpdfx": {
      "command": "python",
      "args": ["path/to/readpdfx/run.py"]
    }
  }
}
```

**📁 See [client-configs/](./client-configs/) for detailed integration guides.**

## 🌐 API Endpoints

### MCP Protocol Endpoints
- `POST /mcp/initialize` - Initialize MCP session
- `POST /mcp/tools/list` - List available tools  
- `POST /mcp/tools/call` - Call MCP tools
- `GET /mcp/manifest` - Get MCP manifest

### HTTP Endpoints  
- `GET /health` - Health check
- `POST /jsonrpc` - JSON-RPC 2.0 endpoint
- `GET /docs` - API documentation
- `GET /tools` - Tools discovery

## 🔧 Configuration

### Environment Variables
```bash
MCP_SERVER_HOST=localhost      # Server host
MCP_SERVER_PORT=8000           # Server port  
TESSERACT_CMD=/usr/bin/tesseract  # Tesseract path
PYTHONPATH=.                   # Python path
```

### Config Files
- `mcp.json` - MCP Protocol configuration
- `mcp-config.yaml` - YAML configuration
- `pyproject.toml` - Python project config
- `package.json` - Node.js compatibility

## 🧪 Testing

### Run Tests
```bash
python test_mcp_server.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# List tools  
curl -X POST http://localhost:8000/mcp/tools/list \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Call tool
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "method": "tools/call",
    "params": {
      "name": "process_pdf_smart",
      "arguments": {"pdf_path": "/path/to/test.pdf"}
    },
    "id": 1
  }'
```

## 📊 Performance

- **Startup Time**: < 2 seconds
- **Memory Usage**: ~50MB base
- **Throughput**: 10+ PDFs/minute  
- **Concurrent Requests**: Up to 100
- **File Size Limit**: 100MB per file

## 🛠️ Development

### Development Mode
```bash
python run_server.py --dev --port 8000
```

### Project Structure
```
readpdfx/
├── run.py                 # Simple production runner
├── run_server.py          # Advanced runner with options  
├── mcp_server.py          # Core MCP server
├── mcp_tools.py           # MCP tools implementation
├── mcp_types.py           # MCP Protocol types
├── mcp_server_runner.py   # HTTP server runner
├── client-configs/        # Client integration guides
├── backup/                # Legacy files
└── tests/                 # Test files
```

### Adding New Tools
1. Define tool schema in `mcp_tools.py`
2. Implement tool handler method
3. Register tool in `MCPToolsRegistry`
4. Update tests and documentation

## 🐛 Troubleshooting

### Common Issues

**Server won't start**
```bash
# Check port availability
netstat -an | grep 8000

# Try different port
python run_server.py --port 8001
```

**OCR not working**  
```bash
# Check Tesseract installation
tesseract --version

# Install language data
tesseract --list-langs
```

**Permission errors**
- Ensure read access to PDF files
- Check write permissions for output directory
- Run with appropriate user privileges

**Connection timeout**
- Verify server is running: `curl http://localhost:8000/health`
- Check firewall settings
- Try HTTP instead of direct MCP connection

### Debug Mode
```bash
python run_server.py --dev
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Metrics (Future)
- Request count and latency
- Tool usage statistics  
- Error rates and types
- Resource utilization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-tool`
3. Make changes and add tests
4. Submit pull request

### Development Setup
```bash
git clone https://github.com/irev/mcp-readpdfx.git
cd readpdfx
pip install -r requirements-dev.txt
python test_mcp_server.py
```

## 📄 License

MIT License - see [LICENSE](./LICENSE) file.

## 🔗 Links

- **Repository**: https://github.com/irev/mcp-readpdfx
- **Issues**: https://github.com/irev/mcp-readpdfx/issues  
- **Documentation**: https://github.com/irev/mcp-readpdfx#readme
- **MCP Protocol**: [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)

## 🏆 Acknowledgments

- MCP Protocol Team for the specification
- FastAPI for the web framework
- Tesseract OCR for text recognition
- PyPDF2 and pdfplumber for PDF processing

---

**Made with ❤️ for the MCP community**