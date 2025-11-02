# Cursor MCP Configuration

Integration guide for Cursor IDE with OCR PDF MCP server.

## Prerequisites

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure Tesseract is installed and in PATH

## Cursor Configuration

### Method 1: VS Code Extension Style

Create `.cursor/extensions.json`:

```json
{
  "mcpServers": {
    "ocr-pdf": {
      "command": "python",
      "args": [
        "D:\\AI\\MCP\\python\\ocr_pdf_mcp\\run.py"
      ],
      "env": {
        "PYTHONPATH": "D:\\AI\\MCP\\python\\ocr_pdf_mcp"
      }
    }
  }
}
```

### Method 2: Settings Configuration

Add to Cursor settings.json:

```json
{
  "mcp.servers": {
    "ocr-pdf": {
      "command": "python",
      "args": ["D:\\AI\\MCP\\python\\ocr_pdf_mcp\\run.py"],
      "env": {
        "PYTHONPATH": "D:\\AI\\MCP\\python\\ocr_pdf_mcp",
        "MCP_SERVER_HOST": "localhost",
        "MCP_SERVER_PORT": "8000"
      }
    }
  }
}
```

### Method 3: HTTP Server Integration

1. Start HTTP server:
   ```bash
   python run_server.py --prod
   ```

2. Configure Cursor for HTTP:
   ```json
   {
     "mcp.httpServers": {
       "ocr-pdf": {
         "url": "http://localhost:8000",
         "endpoints": {
           "initialize": "/mcp/initialize",
           "tools/list": "/mcp/tools/list", 
           "tools/call": "/mcp/tools/call"
         }
       }
     }
   }
   ```

## Usage in Cursor

### Command Palette

1. Open Command Palette (`Ctrl+Shift+P`)
2. Search for "MCP: OCR PDF"
3. Select desired tool:
   - Smart PDF Processing
   - Text Extraction
   - OCR Image
   - PDF Analysis
   - Batch Processing

### Chat Integration

Use the following prompts in Cursor Chat:

```
@ocr-pdf Process this PDF file: /path/to/document.pdf

@ocr-pdf Extract text from: /path/to/scanned.pdf

@ocr-pdf Analyze structure of: /path/to/complex.pdf
```

### Inline Code Actions

Right-click on PDF files in explorer → "Process with OCR PDF MCP"

## Tool Specifications

### Smart PDF Processing
- **Command**: `process_pdf_smart`
- **Input**: PDF file path, language (optional)
- **Output**: Extracted text with metadata

### Text Extraction
- **Command**: `extract_pdf_text`
- **Input**: PDF file path, page range (optional)
- **Output**: Raw text content

### OCR Processing
- **Command**: `perform_ocr`
- **Input**: Image file path, language (optional)
- **Output**: OCR text results

### PDF Analysis
- **Command**: `analyze_pdf_structure`
- **Input**: PDF file path
- **Output**: Document structure and metadata

### Batch Processing
- **Command**: `batch_process_pdfs`
- **Input**: Directory path, output directory, file pattern
- **Output**: Processing results summary

## Keybindings

Add to `keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+p",
    "command": "mcp.ocr-pdf.process-smart",
    "when": "resourceExtname == .pdf"
  },
  {
    "key": "ctrl+shift+o",
    "command": "mcp.ocr-pdf.perform-ocr",
    "when": "resourceExtname =~ /\\.(png|jpg|jpeg|tiff|bmp)$/"
  }
]
```

## Workspace Configuration

For project-specific configuration, create `.cursor/workspace.json`:

```json
{
  "folders": [
    {
      "path": "."
    }
  ],
  "extensions": {
    "recommendations": ["mcp-ocr-pdf"]
  },
  "settings": {
    "mcp.ocr-pdf.defaultLanguage": "eng",
    "mcp.ocr-pdf.outputFormat": "text",
    "mcp.ocr-pdf.autoStart": true
  }
}
```

## Troubleshooting

### Server Not Starting
```bash
# Check if server starts manually
python run.py
```

### Permission Issues
- Run Cursor as administrator
- Check file path permissions
- Verify Python executable path

### OCR Issues
- Install Tesseract: `choco install tesseract` (Windows)
- Add Tesseract to PATH
- Check language data files

### Connection Problems
- Verify port 8000 is not in use
- Check Windows Firewall settings
- Test HTTP endpoint: `curl http://localhost:8000/health`

## Development

For development with debug mode:

```bash
python run_server.py --dev --host 127.0.0.1 --port 8000
```

Monitor logs in Cursor Output panel under "MCP OCR PDF" channel.

## Repository

GitHub: https://github.com/irev/mcp-readpdfx