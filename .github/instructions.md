# ReadPDFx - GitHub Repository Instructions

## 📋 Repository Overview

ReadPDFx adalah MCP (Model Context Protocol) server production-ready untuk OCR PDF processing yang mengikuti standar MCP Protocol 2025-06-18.

standard referensi: https://modelcontextprotocol.io/docs/develop/build-server 
semua harus berdasar referensi

**Repository**: https://github.com/irev/mcp-readpdfx

## 🏗️ Project Structure

```
readpdfx/
├── install.py              # 🚀 Root installer
├── run.py                  # ⚡ Simple production runner
├── src/                    # 📦 Core MCP server files
│   ├── mcp_server.py       # 🧠 Core MCP server
│   ├── mcp_tools.py        # 🛠️ MCP tools implementation
│   ├── mcp_types.py        # 📝 MCP Protocol types
│   └── mcp_server_runner.py # 🌐 HTTP server runner
├── scripts/                # 🔧 Utility scripts
├── tests/                  # 🧪 Test files
├── client-configs/         # 🔌 Client integration guides
├── ocr_pdf_mcp/           # 📄 Original OCR utilities
├── backup/                 # 📦 Legacy files backup
└── .github/               # 🏢 GitHub configurations
```

## 🚀 Quick Start

### For End Users
```bash
# Clone repository
git clone https://github.com/irev/mcp-readpdfx.git
cd mcp-readpdfx

# Install dependencies
python install.py

# Run server
python run.py
```

### For Developers
```bash
# Clone repository
git clone https://github.com/irev/mcp-readpdfx.git
cd mcp-readpdfx

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python scripts/run_server.py --dev

# Run tests
python -m pytest tests/
```

## MCP Server Endpoints
The MCP server exposes the following endpoints:
- `POST /mcp/initialize`   - MCP Initialize
- `POST /mcp/tools/list`   - MCP List Tools
- `POST /mcp/tools/call`   - MCP Call Tool
- `POST /call`             - LM Studio Tool Call
- `POST /<tool_name>`      - Direct Tool Call
- `POST /jsonrpc`          - JSON-RPC 2.0
- `WS   /ws`               - WebSocket connection
- `GET  /events`           - LM Studio SSE Stream
- `GET  /stream`           - Alternative Stream
- `GET  /sse/tools`        - SSE Tools Stream
- `GET  /sse/status`       - SSE Status Stream
- `GET  /tools`            - Tools Discovery

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Document all public functions and classes
- Keep functions small and focused

### MCP Protocol Requirements
- ✅ JSON-RPC 2.0 compliance
- ✅ MCP Protocol 2025-06-18 standard
- ✅ Proper error handling
- ✅ CORS support for HTTP clients
- ✅ SSE for progress updates
- ✅ Comprehensive documentation

### Commit Messages
Use conventional commit format:
```
feat: add new OCR processing tool
fix: resolve import path issues
docs: update client integration guide
test: add unit tests for MCP server
refactor: reorganize project structure
```

seusai dengan MCP Protocol v2025-06-18 dan JSON-RPC 2.0 standards.

# 📚 OCR PDF MCP - Response Framework Implementation Guide
## 🛠️ Overview of Implementation
This document outlines the implementation of the Response Framework for the OCR PDF MCP server, ensuring compliance with MCP Protocol v2025-06-18, JSON-RPC 2.0, and Server-Sent Events (SSE) specifications.

# Terminal Commands
To execute terminal commands in Windows, you can use the Command Prompt (cmd) 
dont use powershell. Here are some examples of how to after run run.py to start the server: using another cmd command.

