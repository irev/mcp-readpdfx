# Claude Desktop MCP Configuration

This is the configuration file for integrating OCR PDF MCP server with Claude Desktop.

## Installation Steps

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add this configuration to your Claude Desktop config file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

## Configuration JSON

Copy the following configuration into your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ocr-pdf": {
      "command": "python",
      "args": [
        "D:\\AI\\MCP\\python\\ocr_pdf_mcp\\ocr_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "D:\\AI\\MCP\\python\\ocr_pdf_mcp"
      }
    }
  }
}
```

## Alternative HTTP Configuration

For HTTP-based connection:

```json
{
  "mcpServers": {
    "ocr-pdf-http": {
      "command": "python",
      "args": [
        "D:\\AI\\MCP\\python\\ocr_pdf_mcp\\run_server.py",
        "--host", "localhost",
        "--port", "8000"
      ],
      "env": {
        "PYTHONPATH": "D:\\AI\\MCP\\python\\ocr_pdf_mcp"
      }
    }
  }
}
```

## Usage

After configuration, restart Claude Desktop. The OCR PDF tools will be available:

- `process_pdf_smart` - Smart PDF processing with automatic OCR detection
- `extract_pdf_text` - Extract text from PDF files
- `perform_ocr` - Perform OCR on image files
- `analyze_pdf_structure` - Analyze PDF document structure
- `batch_process_pdfs` - Process multiple PDFs in batch

## Repository

GitHub: https://github.com/irev/mcp-readpdfx