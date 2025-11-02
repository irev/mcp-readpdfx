# ReadPDFx - GitHub Repository Instructions

## 📋 Repository Overview

ReadPDFx adalah MCP (Model Context Protocol) server production-ready untuk OCR PDF processing yang mengikuti standar MCP Protocol 2025-06-18.

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
