#!/usr/bin/env python3
"""
MCP Server Status Display
Shows current server status and usage information
"""

import subprocess
import sys
import time
from pathlib import Path

def check_server_status():
    """Check if MCP server is running"""
    print("🔍 Checking MCP Server Status")
    print("=" * 50)
    
    # Test server imports
    try:
        from mcp.server.fastmcp import FastMCP
        print("✅ MCP SDK: Available")
        
        from ocr_pdf_mcp.pdf_text_extractor import extract_text_from_pdf
        from ocr_pdf_mcp.ocr_worker import process_ocr_pdf
        from ocr_pdf_mcp.config import Config
        print("✅ OCR Modules: Available")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    
    # Check Tesseract languages
    try:
        result = subprocess.run(['tesseract', '--list-langs'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            languages = result.stdout
            print(f"✅ Tesseract: Available")
            
            # Check Indonesian support
            if 'ind' in languages:
                print("✅ Indonesian Language: Available (eng+ind ready)")
            else:
                print("⚠️  Indonesian Language: Not installed (eng only)")
                
        else:
            print("❌ Tesseract: Not working properly")
    except:
        print("❌ Tesseract: Not found")
    
    return True

def show_server_info():
    """Display server information and usage"""
    
    print(f"\n🚀 MCP STDIO Server Information")
    print("=" * 50)
    
    print(f"📍 Server Location:")
    print(f"   {Path(__file__).parent / 'mcp_server_stdio.py'}")
    
    print(f"\n🔧 Available Tools (6):")
    tools = [
        "process_pdf_smart - Smart PDF processing with auto OCR detection",
        "extract_pdf_text - Extract digital text from PDF",
        "perform_ocr - OCR processing for images/scanned PDFs",
        "analyze_pdf_structure - Analyze PDF metadata and structure", 
        "list_ocr_languages - Check available OCR languages + Indonesian support",
        "batch_process_pdfs - Process multiple PDFs in directory"
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool}")
    
    print(f"\n🇮🇩 Indonesian Language Support:")
    print(f"   Optimal: lang='eng+ind' (English + Indonesian)")
    print(f"   Fallback: lang='eng' (English only)")
    
    print(f"\n📱 Client Integration:")
    print(f"   Claude Desktop: Update mcpSettings.json")
    print(f"   LM Studio: Configure MCP server settings")
    print(f"   Continue.dev: Add to MCP configuration")
    
    client_config = f'''{{
  "mcpServers": {{
    "ocr-pdf": {{
      "command": "python",
      "args": ["{Path(__file__).parent / 'mcp_server_stdio.py'}"],
      "env": {{}}
    }}
  }}
}}'''
    
    print(f"\n⚙️  Claude Desktop Config:")
    print(client_config)

def show_usage_examples():
    """Show usage examples"""
    
    print(f"\n📖 Usage Examples")
    print("=" * 50)
    
    print(f"🔧 Test Server Locally:")
    print(f"   python validate_tools.py")
    print(f"   python test_indonesian_support.py")
    
    print(f"\n📄 Process PDF dengan Indonesian:")
    print(f"   Tool: process_pdf_smart")
    print(f"   Input: {{\"pdf_path\": \"document.pdf\", \"language\": \"eng+ind\"}}")
    
    print(f"\n🔍 Check Indonesian Language Support:")
    print(f"   Tool: list_ocr_languages")
    print(f"   Input: {{}}")
    
    print(f"\n⚡ OCR Image dengan Indonesian:")
    print(f"   Tool: perform_ocr")
    print(f"   Input: {{\"file_path\": \"image.png\", \"language\": \"eng+ind\"}}")
    
    print(f"\n📊 Batch Process PDFs:")
    print(f"   Tool: batch_process_pdfs") 
    print(f"   Input: {{\"directory_path\": \"./pdfs\", \"language\": \"eng+ind\"}}")

def main():
    """Main status display"""
    
    print("🇮🇩 OCR PDF MCP Server - Status Dashboard")
    print("=" * 60)
    print(f"Server Type: STDIO Transport (Official MCP SDK)")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # Check status
    if check_server_status():
        print(f"\n🎉 Server Status: ✅ READY")
        
        # Show info
        show_server_info()
        show_usage_examples()
        
        print(f"\n🚨 Important Notes:")
        print(f"   • Server runs via STDIO (not HTTP)")
        print(f"   • Indonesian language pack may need manual installation")
        print(f"   • Use absolute file paths in tool calls")
        print(f"   • Server auto-starts when client connects")
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Configure your MCP client (Claude Desktop/LM Studio)")
        print(f"   2. Test connection with client")
        print(f"   3. Try processing Indonesian documents")
        
    else:
        print(f"\n❌ Server Status: NOT READY")
        print(f"   Fix dependencies and try again")

if __name__ == "__main__":
    main()