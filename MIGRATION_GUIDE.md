# 🔄 Migration Guide: HTTP → STDIO

## Overview
This guide helps migrate from the old HTTP-based MCP server to the new official STDIO implementation.

## 🎯 Quick Migration

### **Old Setup (HTTP)**
```python
# mcp_server_runner.py (800+ lines)
python run.py  # Started HTTP server on localhost:8000
```

### **New Setup (STDIO)**
```python
# mcp_server_stdio.py (~200 lines)
# No manual start - client handles execution
```

## 📋 Client Configuration Changes

### **1. Claude Desktop**

**Before:**
```json
{
  "mcpServers": {
    "ocr-pdf": {
      "url": "http://localhost:8000"
    }
  }
}
```

**After:**
```json
{
  "mcpServers": {
    "ocr-pdf": {
      "command": "python",
      "args": ["d:/AI/MCP/python/ocr_pdf_mcp/mcp_server_stdio.py"],
      "env": {}
    }
  }
}
```

### **2. LM Studio**

**Before:**
```json
{
  "name": "ocr-pdf",
  "url": "http://localhost:8000"
}
```

**After:**
```json
{
  "name": "ocr-pdf",
  "command": "python",
  "args": ["d:/AI/MCP/python/ocr_pdf_mcp/mcp_server_stdio.py"]
}
```

## 🔧 Tool Changes

### **Same 5 Tools Available:**
1. `extract_pdf_text` - Extract text using PyMuPDF
2. `ocr_pdf` - OCR processing with Tesseract  
3. `extract_and_ocr_pdf` - Combined extraction and OCR
4. `health_check` - Server health and dependencies
5. `list_ocr_languages` - Available OCR languages

### **Tool Usage - No Changes:**
```python
# Same tool calls work in both versions
result = await client.call_tool("extract_pdf_text", {"file_path": "document.pdf"})
```

## ✅ Migration Checklist

- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Validate tools: `python validate_tools.py`
- [ ] Update Claude Desktop config (STDIO)
- [ ] Update LM Studio config (STDIO)  
- [ ] Test with client connections
- [ ] Remove old HTTP server startup scripts
- [ ] Update documentation/scripts

## 🚀 Benefits of STDIO Migration

| Aspect | HTTP (Old) | STDIO (New) |
|--------|------------|-------------|
| **Code Size** | 800+ lines | ~200 lines |
| **Dependencies** | Custom FastAPI | Official MCP SDK |
| **Protocol** | Custom JSON-RPC/HTTP | Standard MCP STDIO |
| **Transport** | HTTP endpoints | STDIO communication |
| **Tool Registration** | Manual routing | @mcp.tool() decorators |
| **Client Support** | Limited | Universal MCP clients |
| **Maintenance** | High complexity | Official framework |

## 🛠️ Troubleshooting

### **Common Issues:**

**1. Import Errors**
```bash
# Solution: Ensure MCP SDK installed
pip install mcp[cli]>=1.2.0
```

**2. Path Issues**
```bash  
# Solution: Use absolute paths in client config
"args": ["d:/AI/MCP/python/ocr_pdf_mcp/mcp_server_stdio.py"]
```

**3. Tool Not Found**
```bash
# Solution: Validate tools registration
python validate_tools.py
```

## 📞 Support

- **Validation**: Run `python validate_tools.py`
- **Logs**: Check client logs for STDIO communication
- **Fallback**: Old HTTP server still available in `mcp_server_runner.py`

---

**Migration Status**: ✅ Complete  
**Recommended**: Use STDIO server (`mcp_server_stdio.py`) as primary  
**Legacy Support**: HTTP server preserved for transition period