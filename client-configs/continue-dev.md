# Continue.dev MCP Configuration

Integration configuration for Continue.dev with OCR PDF MCP server.

## Installation

1. Install the OCR PDF MCP server dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the MCP server:
   ```bash
   python run.py
   ```

## Continue.dev Configuration

### config.json Configuration

Add this to your Continue.dev `config.json` file:

```json
{
  "models": [
    {
      "title": "Your Model",
      "provider": "your-provider",
      "model": "your-model"
    }
  ],
  "contextProviders": [
    {
      "name": "mcp",
      "params": {
        "serverName": "ocr-pdf",
        "command": "python",
        "args": [
          "D:\\AI\\MCP\\python\\ocr_pdf_mcp\\run.py"
        ],
        "env": {
          "PYTHONPATH": "D:\\AI\\MCP\\python\\ocr_pdf_mcp",
          "MCP_SERVER_HOST": "localhost",
          "MCP_SERVER_PORT": "8000"
        }
      }
    }
  ],
  "slashCommands": [
    {
      "name": "pdf",
      "description": "Process PDF files with OCR",
      "run": "mcp://ocr-pdf/process_pdf_smart"
    },
    {
      "name": "ocr",
      "description": "Perform OCR on images", 
      "run": "mcp://ocr-pdf/perform_ocr"
    }
  ]
}
```

### HTTP-based Configuration

For HTTP connection to the MCP server:

```json
{
  "contextProviders": [
    {
      "name": "http",
      "params": {
        "url": "http://localhost:8000",
        "headers": {
          "Content-Type": "application/json"
        }
      }
    }
  ],
  "tools": [
    {
      "name": "ocr-pdf-tools",
      "description": "OCR PDF processing tools",
      "endpoint": "http://localhost:8000/mcp/tools/call",
      "method": "POST"
    }
  ]
}
```

## Usage in Continue.dev

### Using Slash Commands

```
/pdf path/to/document.pdf
/ocr path/to/image.png
```

### Using Context Provider

```markdown
@mcp Process this PDF file: /path/to/document.pdf
```

### Direct Tool Calls

```typescript
// In Continue.dev extension
const result = await tools.call('process_pdf_smart', {
  pdf_path: '/path/to/document.pdf',
  language: 'eng'
});
```

## Available Tools

### process_pdf_smart
Smart PDF processing with automatic OCR detection
```json
{
  "pdf_path": "string",
  "language": "string (optional, default: eng)",
  "output_format": "string (optional, default: text)"
}
```

### extract_pdf_text
Extract text directly from PDF
```json
{
  "pdf_path": "string",
  "page_range": "string (optional, e.g., '1-5')"
}
```

### perform_ocr
Perform OCR on image files
```json
{
  "image_path": "string",
  "language": "string (optional, default: eng)"
}
```

### analyze_pdf_structure
Analyze PDF document structure
```json
{
  "pdf_path": "string"
}
```

### batch_process_pdfs
Process multiple PDFs
```json
{
  "input_directory": "string",
  "output_directory": "string (optional)",
  "file_pattern": "string (optional, default: *.pdf)"
}
```

## Development Mode

For development with hot reload:

```bash
python run_server.py --dev --port 8000
```

## Troubleshooting

1. **MCP Connection**: Verify server is running on correct port
2. **Path Issues**: Use absolute paths in configuration
3. **Permissions**: Ensure Continue.dev has access to file paths
4. **Tesseract**: Install Tesseract OCR for image processing

## Repository

GitHub: https://github.com/irev/mcp-readpdfx